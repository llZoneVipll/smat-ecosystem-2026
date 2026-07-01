import paho.mqtt.client as mqtt
import requests
import json
import sys
import time

# =============================================
# CONFIGURACIÓN
# =============================================
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT   = 1883
MQTT_TOPIC  = "fisi/smat/estaciones/+/lecturas"  # '+' wildcard para cualquier estación
API_URL     = "http://localhost:8000/lecturas/"
JWT_TOKEN   = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbl9zbWF0IiwiZXhwIjoxNzgxMTA2NjAzfQ.CGgl0ASB7cyza5MNZ2ezp9vWWK0Cg0we7htDzNJ6SrA"  # Reemplaza con tu token

# =============================================
# FILTRO DEADBAND — Memoria Caché Local
# =============================================
UMBRAL_CAMBIO_PORCENTAJE = 5.0   # 5% de variación mínima
TIEMPO_MINIMO_REPORTE    = 60    # segundos máximos sin reportar

# Caché: { estacion_id: {"valor": float, "timestamp": float} }
cache = {}


def debe_enviar(estacion_id: int, nuevo_valor: float) -> tuple:
    """
    Retorna (True, motivo) si el dato debe enviarse a la API.
    Retorna (False, motivo) si el dato es redundante y debe bloquearse.
    """
    ahora = time.time()

    # Si es la primera lectura de esta estación, siempre enviar
    if estacion_id not in cache:
        return True, "Primera lectura de la estación"

    ultimo_valor     = cache[estacion_id]["valor"]
    ultimo_timestamp = cache[estacion_id]["timestamp"]

    # Condición 1 — Han pasado más de 60 segundos (reporte mínimo de vida)
    segundos_transcurridos = ahora - ultimo_timestamp
    if segundos_transcurridos > TIEMPO_MINIMO_REPORTE:
        return True, f"Reporte de vida ({int(segundos_transcurridos)}s sin reportar)"

    # Condición 2 — El valor cambió más del 5%
    if ultimo_valor != 0:
        variacion = abs((nuevo_valor - ultimo_valor) / ultimo_valor) * 100
    else:
        variacion = 100.0

    if variacion > UMBRAL_CAMBIO_PORCENTAJE:
        return True, f"Cambio significativo ({variacion:.1f}% > {UMBRAL_CAMBIO_PORCENTAJE}%)"

    # Dato redundante — bloquear
    return False, f"Filtrado ({variacion:.1f}% de cambio, bajo el umbral)"


# =============================================
# CALLBACKS MQTT
# =============================================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("🟢 Conectado exitosamente al Broker MQTT")
        client.subscribe(MQTT_TOPIC)
        print(f"📡 Escuchando transmisiones en el tópico: {MQTT_TOPIC}\n")
    else:
        print(f"🔴 Error de conexión al Broker. Código: {rc}")
        sys.exit(1)


def on_message(client, userdata, msg):
    try:
        # 1. Decodificar el payload MQTT
        payload_raw = msg.payload.decode("utf-8")
        data_json   = json.loads(payload_raw)

        # 2. Extraer ID de la estación desde el tópico
        # Ejemplo: fisi/smat/estaciones/1/lecturas -> index [3] = "1"
        topic_parts = msg.topic.split('/')
        estacion_id = int(topic_parts[3])
        nuevo_valor = float(data_json["valor"])

        print(f"\n📩 Telemetría recibida — Estación [{estacion_id}]: {nuevo_valor} cm")

        # 3. Aplicar Filtro Deadband
        enviar, motivo = debe_enviar(estacion_id, nuevo_valor)

        if not enviar:
            print(f"🚫 [FILTRADO] Dato bloqueado — {motivo}")
            return

        # 4. Preparar payload para FastAPI
        api_payload = {
            "valor":       nuevo_valor,
            "estacion_id": estacion_id
        }

        # 5. Enviar a la API con JWT
        headers = {
            "Content-Type":  "application/json",
            "Authorization": f"Bearer {JWT_TOKEN}"
        }
        response = requests.post(API_URL, json=api_payload, headers=headers, timeout=5)

        if response.status_code in (200, 201):
            # 6. Actualizar caché solo si se guardó exitosamente
            cache[estacion_id] = {
                "valor":     nuevo_valor,
                "timestamp": time.time()
            }
            print(f"💾 [DB Sincronizada] {nuevo_valor} cm guardado — {motivo}")
        else:
            print(f"⚠️  [Fallo de Ingesta] API rechazó el dato. Código: {response.status_code}")

    except KeyError as e:
        print(f"❌ Error de esquema: Falta la llave {e} en el payload MQTT.")
    except ValueError:
        print("❌ Error de casteo: El valor o ID de estación no son numéricos.")
    except Exception as e:
        print(f"❌ Error crítico en el Bridge: {e}")


# =============================================
# INICIO DEL BRIDGE
# =============================================
print("=" * 50)
print("  🚀 Inicializando el Bridge de Acoplamiento SMAT...")
print("=" * 50)

bridge_client = mqtt.Client()
bridge_client.on_connect = on_connect
bridge_client.on_message = on_message

try:
    bridge_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    bridge_client.loop_forever()
except KeyboardInterrupt:
    print("\n🛑 Bridge detenido por el administrador.")