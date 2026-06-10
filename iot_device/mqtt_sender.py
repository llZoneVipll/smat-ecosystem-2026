import paho.mqtt.client as mqtt
import json
import time
import random

# =============================================
# CONFIGURACIÓN
# =============================================
BROKER     = "broker.hivemq.com"
PORT       = 1883
TOPIC      = "fisi/smat/estaciones/1"
ESTACION_ID = 1

# =============================================
# BUCLE PRINCIPAL
# =============================================
def enviar_datos_mqtt():
    client = mqtt.Client()
    client.connect(BROKER, PORT)
    print(f"{'='*50}")
    print(f"  Sensor MQTT iniciado — Publicando en: {TOPIC}")
    print(f"{'='*50}\n")

    while True:
        valor = round(random.uniform(20.0, 85.0), 2)

        payload = {
            "valor": valor,
            "timestamp": time.time()
        }

        client.publish(TOPIC, json.dumps(payload))

        if valor > 70.0:
            print(f"[ALERTA MQTT] Valor crítico publicado: {valor} cm")
        else:
            print(f"[MQTT] Publicado: {valor} cm → Topic: {TOPIC}")

        time.sleep(10)

if __name__ == "__main__":
    enviar_datos_mqtt()