# 1. Imagen base: Usamos una versión ligera de Python
FROM python:3.11-slim
# Directorio de trabajo: Creamos una carpeta dentro del contenedor
WORKDIR /app

# Copiamos los requerimientos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt
# Copiar código
COPY etl.py .
# Ejecutar comando inicial
CMD ["python", "etl.py"]