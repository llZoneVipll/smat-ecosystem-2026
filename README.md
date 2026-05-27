## IoT Device — Emulación de Hardware y Telemetría

### ¿Qué hace?
La carpeta `iot_device/` contiene un script Python que simula el comportamiento de un
microcontrolador físico (ESP32 o Raspberry Pi). El script emula sensores de nivel de río
y envía datos automáticamente a la API SMAT cada ciertos segundos.

### ¿Cómo se comunica con la nube?

El hardware emulado usa el protocolo **HTTP** para comunicarse con el backend mediante estos pasos:

1. Autenticación: Primero se obtiene un Token JWT haciendo POST a `/token` con usuario y contraseña.
2. Envío de datos: El token se incluye en cada petición como header `Authorization: Bearer <token>`.
3. Telemetría: El script hace POST a `/lecturas/` enviando el valor del sensor y el ID de la estación.

### Modos de operación

| Modo | Condición | Frecuencia de envío |
|---|---|---|
| Normal | Nivel <= 70 cm | Cada 10 segundos |
| Emergencia | Nivel > 70 cm | Cada 2 segundos |

### Cómo ejecutarlo

1. Instalar dependencias:
```bash
pip install requests
```

2. Configurar el script `iot_device/sensor_emitter.py`:
```python
API_URL     = "http://localhost:8000/lecturas/"
ESTACION_ID = 1       # ID de tu estación en la DB
TOKEN       = "tu_token_jwt"  # Obtenido del endpoint /token
```

3. Correr el script:
```bash
python sensor_emitter.py
```

### Sistema completo (3 terminales)

| Terminal | Comando | Descripción |
|---|---|---|
| 1 | `cd backend && python -m uvicorn app.main:app --reload` | API FastAPI |
| 2 | `cd iot_device && python sensor_emitter.py` | Sensor emulado |
| 3 | Emulador Flutter | App móvil |