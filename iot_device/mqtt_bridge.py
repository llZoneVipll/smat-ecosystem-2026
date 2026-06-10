import paho.mqtt.client as mqtt
import requests
import json
import time
import threading

# =============================================
# CONFIGURACIÓN
# =============================================
BROKER  = "broker.hivemq.com"
PORT    = 1883
TOPIC   = "fisi/smat/estaciones/#"
API_URL = "http://localhost:8000/lecturas/"
TOKEN   = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbl9zbWF0IiwiZXhwIjoxNzgxMDYwMTAzfQ.Yxb5gnIUa5EAg4FWRZiVOmcuQQs7dPhWchdUMjwldO4"  # Reemplaza con tu token

# Tiempo máximo sin recibir datos antes de marcar OFFLINE (segundos)
TIMEOUT_OFFLINE = 30

# Diccionario para rastrear el último mensaje de cada estación
last_seen = {}


# =============================================
# CALLBACK — Se ejecuta al recibir un mensaje
# =============================================
def on_message(client, userdata, msg):
    try:
        # 1. Decodificar el mensaje MQTT
        payload = json.loads(msg.payload.decode())
        print(f"\n📩 Mensaje recibido en [{msg.topic}]: {payload}")

        # 2. Extraer el ID de la estación desde el tópico
        # Ejemplo: fisi/smat/estaciones/1 -> ID = 1
        estacion_id = msg.topic.split('/')[-1]

        # 3. Registrar el momento del último mensaje
        last_seen[estacion_id] = time.time()

        # 4. Preparar datos para el Backend
        data_to_send = {
            "valor":       payload["valor"],
            "estacion_id": int(estacion_id)
        }

        # 5. Enviar a la API mediante HTTP POST
        headers = {"Authorization": f"Bearer {TOKEN}"}
        response = requests.post(API_URL, json=data_to_send, headers=headers, timeout=5)

        if response.status_code in (200, 201):
            print(f" Dato persistido en DB — Estación {estacion_id}: {payload['valor']} cm")
        else:
            print(f"  Error API ({response.status_code}): {response.text}")

    except Exception as e:
        print(f" Error procesando mensaje: {e}")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("🔗 Conectado al Broker MQTT exitosamente")
        client.subscribe(TOPIC)
        print(f" Suscrito al tópico: {TOPIC}\n")
    else:
        print(f" Error de conexión al Broker. Código: {rc}")


# =============================================
# HILO DE MONITOREO — Detecta estaciones Offline
# =============================================
def check_deadlines():
    while True:
        current_time = time.time()
        for eid, t in list(last_seen.items()):
            segundos_sin_datos = current_time - t
            if segundos_sin_datos > TIMEOUT_OFFLINE:
                print(f"[OFFLINE] Estación {eid} sin datos hace {int(segundos_sin_datos)}s")
        time.sleep(10)


# =============================================
# INICIO DEL BRIDGE
# =============================================
print("=" * 50)
print("  🚀 Bridge SMAT iniciado. Esperando datos...")
print("=" * 50)

# Lanzar hilo de monitoreo en segundo plano
threading.Thread(target=check_deadlines, daemon=True).start()

# Configurar y conectar cliente MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT)
client.loop_forever()