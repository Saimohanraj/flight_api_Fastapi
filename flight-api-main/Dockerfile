FROM python:3.10-slim
RUN apt update -y && apt upgrade -y && apt install -y netcat-traditional git curl libglib2.0-0 libsm6 libxrender1 libxext6
RUN pip install --upgrade pip --no-cache-dir
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
CMD [ "uvicorn", "--host", "0.0.0.0", "--port", "8000", "aircraft_api:app" ]
