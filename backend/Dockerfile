# 1. Imagen base ligera de Python
FROM python:3.11-slim

# 2. Definir el directorio de trabajo dentro del contenedor
WORKDIR /app

# --- AÑADE ESTA LÍNEA PARA EL RETO ---
# Instalar curl para que el healthcheck de Docker Compose funcione
RUN apt-get update && apt-get install -y curl
# -------------------------------------

# 3. Copiar los requerimientos e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar el resto del código del backend
COPY . .

# 5. Crear una carpeta dedicada para la base de datos (Persistencia)
RUN mkdir -p /app/data

# 6. Exponer el puerto nativo de FastAPI
EXPOSE 8000

# 7. Comando para arrancar Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]