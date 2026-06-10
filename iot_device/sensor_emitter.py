import requests
import time
import random

# =============================================
# CONFIGURACIÓN — Edita estos 3 valores
# =============================================
API_URL     = "http://localhost:8000/lecturas/"
ESTACION_ID = 1          # ID de tu estación en la DB
TOKEN       = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbl9zbWF0IiwiZXhwIjoxNzc5ODk3MzgxfQ.lFdc2qAeueTknwxznqHaNaeLibqt7ubkrouSDFccyTc"  # Obtenido del login

# Umbral de inundación (cm)
UMBRAL_ALERTA   = 70.0
INTERVALO_NORMAL     = 10  # segundos en modo normal
INTERVALO_EMERGENCIA =  2  # segundos en modo emergencia


# =============================================
# EMULACIÓN DEL SENSOR
# =============================================
def leer_sensor_emulado() -> float:
    """Simula un sensor de nivel de río (0–100 cm)."""
    return round(random.uniform(10.5, 85.0), 2)


# =============================================
# BUCLE PRINCIPAL DE TELEMETRÍA
# =============================================
def enviar_telemetria():
    print(f"{'='*50}")
    print(f"  Iniciando Emisor IoT — Estación {ESTACION_ID}")
    print(f"{'='*50}\n")

    while True:
        valor = leer_sensor_emulado()

        # --- Reto Semana 9: Lógica de Alarma ---
        if valor > UMBRAL_ALERTA:
            print(f"[ALERTA] Umbral de inundación superado: {valor} cm")
            intervalo = INTERVALO_EMERGENCIA
            modo = "EMERGENCIA"
        else:
            intervalo = INTERVALO_NORMAL
            modo = "Normal"

        # --- Envío a la API ---
        payload = {
            "valor":       valor,
            "estacion_id": ESTACION_ID
        }
        headers = {
            "Authorization": f"Bearer {TOKEN}"
        }

        try:
            response = requests.post(API_URL, json=payload, headers=headers, timeout=5)

            if response.status_code in (200, 201):
                print(f"[OK]    Lectura enviada: {valor} cm  | Modo: {modo} | Próxima en {intervalo}s")
            else:
                print(f"[ERROR] Código HTTP: {response.status_code} — {response.text}")

        except requests.exceptions.ConnectionError:
            print(f"[CRÍTICO] No hay conexión con el servidor. Reintentando en {intervalo}s...")
        except Exception as e:
            print(f"[CRÍTICO] Error inesperado: {e}")

        time.sleep(intervalo)


if __name__ == "__main__":
    enviar_telemetria()