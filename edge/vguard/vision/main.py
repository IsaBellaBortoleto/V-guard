import cv2
import numpy as np
import mediapipe as mp
import math
import time

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# ============================================================
# CONFIGURAÇÃO
# ============================================================

MODEL_PATH = "models/face_landmarker.task"

# Limiares INICIAIS.
# NÃO são valores definitivos do V-GUARD.
EAR_THRESHOLD = 0.22
MAR_THRESHOLD = 0.60

# Quantidade de tempo que os olhos precisam permanecer
# fechados para considerarmos "olhos fechados prolongadamente".
EYES_CLOSED_TIME = 1.0


# ============================================================
# LANDMARKS
# ============================================================

# Olho direito da pessoa
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

# Olho esquerdo da pessoa
LEFT_EYE = [362, 385, 387, 263, 373, 380]

# Boca
MOUTH_LEFT = 61
MOUTH_RIGHT = 291
MOUTH_TOP = 13
MOUTH_BOTTOM = 14


# ============================================================
# FUNÇÕES GEOMÉTRICAS
# ============================================================

def distance(p1, p2):
    """
    Distância euclidiana entre dois pontos 2D.
    """
    return math.sqrt(
        (p1.x - p2.x) ** 2 +
        (p1.y - p2.y) ** 2
    )


def calculate_ear(landmarks, eye_indices):
    """
    Calcula o Eye Aspect Ratio (EAR).

    Pontos:

          p2 ----- p3
        /             \
       p1               p4
        \             /
          p6 ----- p5

    EAR = (|p2-p6| + |p3-p5|)
          ---------------------
               2|p1-p4|
    """

    p1 = landmarks[eye_indices[0]]
    p2 = landmarks[eye_indices[1]]
    p3 = landmarks[eye_indices[2]]
    p4 = landmarks[eye_indices[3]]
    p5 = landmarks[eye_indices[4]]
    p6 = landmarks[eye_indices[5]]

    vertical_1 = distance(p2, p6)
    vertical_2 = distance(p3, p5)

    horizontal = distance(p1, p4)

    if horizontal == 0:
        return 0.0

    ear = (vertical_1 + vertical_2) / (2.0 * horizontal)

    return ear


def calculate_mar(landmarks):
    """
    Calcula uma versão simples do Mouth Aspect Ratio.

    MAR = distância vertical da boca /
          distância horizontal da boca
    """

    left = landmarks[MOUTH_LEFT]
    right = landmarks[MOUTH_RIGHT]

    top = landmarks[MOUTH_TOP]
    bottom = landmarks[MOUTH_BOTTOM]

    horizontal = distance(left, right)
    vertical = distance(top, bottom)

    if horizontal == 0:
        return 0.0

    return vertical / horizontal


# ============================================================
# DESENHO
# ============================================================

def draw_point(frame, landmark, width, height):
    """
    Converte landmark normalizado para coordenadas da imagem.
    """

    x = int(landmark.x * width)
    y = int(landmark.y * height)

    cv2.circle(
        frame,
        (x, y),
        2,
        (0, 255, 0),
        -1
    )


def draw_selected_landmarks(frame, landmarks):
    """
    Desenha somente os landmarks utilizados pelo algoritmo.
    """

    height, width, _ = frame.shape

    indices = (
        RIGHT_EYE +
        LEFT_EYE +
        [
            MOUTH_LEFT,
            MOUTH_RIGHT,
            MOUTH_TOP,
            MOUTH_BOTTOM
        ]
    )

    for index in indices:
        draw_point(
            frame,
            landmarks[index],
            width,
            height
        )


# ============================================================
# CLASSIFICAÇÃO
# ============================================================

def classify_driver(ear, mar, eyes_closed_start):
    """
    Classificação extremamente simples.

    Retorna:

        NORMAL
        OLHOS FECHADOS
        BOCA ABERTA
    """

    now = time.time()

    # Olhos fechados
    if ear < EAR_THRESHOLD:

        if eyes_closed_start is None:
            eyes_closed_start = now

        duration = now - eyes_closed_start

        if duration >= EYES_CLOSED_TIME:
            state = "OLHOS FECHADOS"

        else:
            state = "PISCANDO"

    else:

        eyes_closed_start = None
        duration = 0

        state = "NORMAL"

    # Boca aberta
    if mar > MAR_THRESHOLD:
        mouth_state = "BOCA ABERTA"
    else:
        mouth_state = "BOCA NORMAL"

    return state, mouth_state, eyes_closed_start


# ============================================================
# MEDIAPIPE
# ============================================================

base_options = python.BaseOptions(
    model_asset_path=MODEL_PATH
)

options = vision.FaceLandmarkerOptions(
    base_options=base_options,

    running_mode=vision.RunningMode.VIDEO,

    num_faces=1,

    min_face_detection_confidence=0.5,

    min_face_presence_confidence=0.5,

    min_tracking_confidence=0.5
)

landmarker = vision.FaceLandmarker.create_from_options(
    options
)


# ============================================================
# CÂMERA
# ============================================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erro: não foi possível abrir a câmera.")
    exit()


eyes_closed_start = None

timestamp_ms = 0

previous_time = time.time()


# ============================================================
# LOOP PRINCIPAL
# ============================================================

while True:

    ret, frame = cap.read()

    if not ret:
        print("Erro ao capturar frame.")
        break

    # --------------------------------------------------------
    # BGR -> RGB
    # --------------------------------------------------------

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    # MediaPipe Image
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    # Timestamp obrigatório para VIDEO mode
    timestamp_ms += 33

    result = landmarker.detect_for_video(
        mp_image,
        timestamp_ms
    )

    # --------------------------------------------------------
    # PROCESSAMENTO DA FACE
    # --------------------------------------------------------

    if result.face_landmarks:

        landmarks = result.face_landmarks[0]

        # EAR dos dois olhos
        right_ear = calculate_ear(
            landmarks,
            RIGHT_EYE
        )

        left_ear = calculate_ear(
            landmarks,
            LEFT_EYE
        )

        # EAR médio
        ear = (
            right_ear +
            left_ear
        ) / 2.0

        # MAR
        mar = calculate_mar(
            landmarks
        )

        # Classificação
        eye_state, mouth_state, eyes_closed_start = classify_driver(
            ear,
            mar,
            eyes_closed_start
        )

        # ----------------------------------------------------
        # DESENHO
        # ----------------------------------------------------

        draw_selected_landmarks(
            frame,
            landmarks
        )

        # ----------------------------------------------------
        # TEXTO
        # ----------------------------------------------------

        cv2.putText(
            frame,
            f"EAR: {ear:.3f}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"MAR: {mar:.3f}",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Olhos: {eye_state}",
            (20, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Boca: {mouth_state}",
            (20, 145),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

    else:

        eyes_closed_start = None

        cv2.putText(
            frame,
            "ROSTO NAO DETECTADO",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )

    # --------------------------------------------------------
    # FPS
    # --------------------------------------------------------

    current_time = time.time()

    fps = 1.0 / (current_time - previous_time)

    previous_time = current_time

    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (20, 180),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    # --------------------------------------------------------
    # MOSTRAR
    # --------------------------------------------------------

    cv2.imshow(
        "V-GUARD - Visao Computacional",
        frame
    )

    # Q para sair
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# ============================================================
# FINALIZAÇÃO
# ============================================================

cap.release()

cv2.destroyAllWindows()

landmarker.close()