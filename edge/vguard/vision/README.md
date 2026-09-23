# V-GUARD — Visão Computacional

Módulo de visão computacional do projeto V-GUARD.

A primeira versão utiliza o MediaPipe Face Landmarker para realizar a detecção de landmarks faciais e extrair métricas utilizadas na análise do estado do motorista:

- EAR (Eye Aspect Ratio)
- MAR (Mouth Aspect Ratio)
- Yaw, Pitch e Roll (orientação da cabeça)

A implementação inicial utiliza Python e OpenCV e pode ser executada utilizando uma webcam.

## Requisitos

- Python 3.10 ou 3.11
- Webcam
- pip
- Git (opcional)

Verifique a versão do Python:

```bash
python --version
```
No Linux, caso python não esteja disponível:
```bash
python3 --version
```


### Estrutura do projeto
```
vguard-vision/
│
├── main.py
├── requirements.txt
├── README.md
│
└── models/
    └── face_landmarker.task
```

### Para executá-lo:
#### 1. Criar o ambiente virtual

Clone o projeto ou entre na pasta do módulo:

cd vguard-vision

Crie o ambiente virtual:

Windows:
```
python -m venv .venv
```
Linux:
```
python3 -m venv .venv
```

#### 2. Ativar o ambiente virtual
Windows — PowerShell:
```
.venv\Scripts\Activate.ps1
```
Windows — CMD:
```
.venv\Scripts\activate
```
Linux
```bash
source .venv/bin/activate
```

Após a ativação, o terminal deverá indicar o ambiente .venv ativo.

#### 3. Atualizar o pip
```bash
python -m pip install --upgrade pip
```
#### 4. Instalar as dependências

Com o ambiente virtual ativado:
```bash
pip install -r requirements.txt
```
As dependências utilizadas atualmente são:
```
mediapipe==0.10.35
opencv-python==4.11.0.86
numpy==2.1.3
```
#### 5. Modelo do MediaPipe

O projeto utiliza o modelo face_landmarker.task.

O arquivo deve estar localizado em:
```
models/face_landmarker.task
```
Estrutura esperada:
```
vguard-vision/
│
├── main.py
├── requirements.txt
├── README.md
│
└── models/
    └── face_landmarker.task
```
#### 6. Executar

Com o ambiente virtual ativado:
```bash
python main.py
```
O programa deverá abrir a webcam e mostrar a detecção facial.
```
Pressione:

Q

para encerrar a execução.
```
#### 7. O que a versão inicial faz

O pipeline atual é:
```
Câmera
   ↓
MediaPipe Face Landmarker
   ↓
Landmarks faciais
   ↓
EAR ─────────┐
             │
MAR ─────────┼──→ Análise do estado do motorista
             │
Head Pose ───┘
```

O EAR é utilizado para analisar a abertura dos olhos.

O MAR é utilizado para analisar a abertura da boca.

A orientação da cabeça será utilizada para obter:

Yaw
Pitch
Roll

Essas métricas serão posteriormente combinadas com análise temporal para identificar possíveis estados relacionados à fadiga e distração.

#### 8. Próximas etapas

A implementação será desenvolvida incrementalmente:

Detecção facial e landmarks
Cálculo do EAR
Cálculo do MAR
Estimativa de Yaw, Pitch e Roll
Análise temporal
Classificação do estado do motorista
Geração de eventos
Integração com o restante do V-GUARD
#### 9. Desativar o ambiente virtual

Quando terminar o desenvolvimento:
```bash
deactivate
```
Para trabalhar novamente no projeto, basta ativar o ambiente:
Windows
```
.venv\Scripts\Activate.ps1
```
Linux
```bash
source .venv/bin/activate
```