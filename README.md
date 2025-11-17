# Chat-Bot 🤖

Bot de Telegram para reportar inundaciones mediante análisis de imágenes con Deep Learning. Los usuarios envían fotos de posibles inundaciones, el bot las clasifica automáticamente y almacena los reportes con geolocalización para análisis posterior.

## 🏗️ Arquitectura

El servicio implementa una **Arquitectura Hexagonal (Ports and Adapters)** combinada con **Clean Architecture**:

```
API Layer (FastAPI Webhook)
    ↓
Controller (Telegram Handler)
    ↓
Use Cases (Business Logic)
    ↓
Domain Layer (Interfaces & Value Objects)
    ↓
Infrastructure Layer (Adapters)
    ├─ Telegram (Bot API)
    ├─ InferenceModel (Flood-Model Client)
    ├─ ApiGateway (Report Service Client)
    └─ Redis (Session Management)
```

### Estructura del Proyecto

```
Chat-Bot/
├── app/
│   ├── api/                        # Endpoints REST
│   │   └── routes.py
│   ├── controller/                 # Controladores de Telegram
│   │   └── telegram_controller.py
│   ├── use_cases/                  # Lógica de negocio
│   │   ├── process_message_uc.py
│   │   ├── process_photo_uc.py
│   │   ├── process_callback_uc.py
│   │   └── submit_report_uc.py
│   ├── domain/                     # Capa de dominio
│   │   ├── interface/             # Puertos (interfaces)
│   │   └── value_objects/         # Objetos de valor
│   ├── infrastructure/             # Adaptadores
│   │   ├── Telegram/
│   │   ├── InferenceModel/
│   │   ├── ApiGateway/
│   │   └── Redis/
│   ├── service/                    # Servicios de sesión
│   │   └── session/
│   ├── config/                     # Configuración e inyección de dependencias
│   │   └── dependencies.py
│   └── main.py                    # Aplicación FastAPI
├── public/
│   ├── bogota_.geojson           # Límites geográficos de Bogotá
│   └── images/
├── requirements.txt
└── README.md
```

## 🛠️ Tecnologías

- **Framework Web**: FastAPI 0.117.0
- **Runtime**: Python 3.10+
- **Bot Framework**: python-telegram-bot 22.4
- **HTTP Client**: httpx 0.28.1
- **Caché/Sesiones**: Redis (hiredis)
- **Geoespacial**: 
  - GeoPandas 1.1.1
  - Shapely
- **Servidor ASGI**: Uvicorn 0.37.0
- **Utilidades**: python-dotenv 1.0.0

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Json-Esutpinan/Chat-Bot.git
cd Chat-Bot
```

### 2. Crear entorno virtual

```bash
python -m venv .venv
```

### 3. Activar entorno virtual

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Telegram Bot
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/webhook

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# Services
GATEWAY_URL=
FLOOD_MODEL_URL=
```

## ▶️ Ejecución

### Modo Desarrollo

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### Modo Producción

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 4
```

### Con Gunicorn (Producción)

```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
```

## 📡 API Endpoints

### Health Check

```http
GET /healthz
```

**Respuesta:**
```json
{
  "status": "ok"
}
```

### Telegram Webhook

```http
POST /api/webhook
Content-Type: application/json
```

Recibe actualizaciones de Telegram (mensajes, fotos, callbacks).

## 🤖 Flujo de Uso

### 1. Usuario inicia conversación

```
Usuario: /start
Bot: ¡Bienvenido! Envía una foto de una posible inundación
```

### 2. Usuario envía foto

```
Usuario: [Envía foto]
Bot: Analizando imagen...
Bot: ✅ Imagen clasificada como "inundación" (92.3% confianza)
     📍 Por favor, envía tu ubicación
```

### 3. Usuario envía ubicación

```
Usuario: [Comparte ubicación]
Bot: ¿Deseas agregar descripción adicional?
     [Sí] [No]
```

### 4. Bot envía reporte

```
Bot: ✅ Reporte enviado exitosamente
```

## 🔄 Integración con Microservicios

El Chat-Bot se integra con dos servicios:

### Flood-Model Service
- **URL**: `{GATEWAY_URL}/flood-model/classify-image`
- **Función**: Clasifica imágenes como inundación/no-inundación
- **Response**: `{"prediction": {"flooded": 0.923, "non_flooded": 0.077}}`

### Report Service
- **URL**: `{GATEWAY_URL}/reports`
- **Función**: Almacena reportes de inundaciones
- **Request**: Datos de imagen, ubicación, descripción

## 📊 Casos de Uso Implementados

1. **ProcessMessageUseCase**: Procesa mensajes de texto del usuario
2. **ProcessPhotoUseCase**: Analiza fotos enviadas y las clasifica
3. **ProcessCallbackUseCase**: Maneja interacciones con botones inline
4. **SubmitReportUseCase**: Envía el reporte completo al servicio backend

## 🗃️ Gestión de Sesiones

El bot utiliza Redis para mantener el estado de cada conversación:

- **StateManager**: Gestiona el flujo conversacional
- **ReportDataManager**: Almacena datos temporales del reporte

Estados disponibles:
- `WAITING_PHOTO`
- `WAITING_LOCATION`
- `WAITING_DESCRIPTION`
- `WAITING_CONFIRMATION`

## 🌍 Validación Geográfica

El bot valida que las ubicaciones estén dentro de los límites de Bogotá usando:
- Archivo GeoJSON (`public/bogota_.geojson`)
- GeoPandas para operaciones espaciales
- Shapely para geometrías

## 📝 Dataset
**GeoJson Bogotá:** Secretaría Distrital de Planeación. (2022, August 5). Municipio Bogotá D.C. - Dataset - Datos Abiertos Bogotá. https://datosabiertos.bogota.gov.co/en/dataset/municipio