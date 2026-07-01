FROM python:3.11-slim
WORKDIR /app

# Instalar las librerias directamente ya que son pocas
RUN pip install paho-mqtt requests

# Copiar el script del puente
COPY mqtt_bridge.py .

# Ejecutar el daemon
CMD ["python", "mqtt_bridge.py"]