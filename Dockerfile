FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY tg_folder_manager/ ./tg_folder_manager/
COPY config.yaml .
COPY .env .
RUN mkdir -p /app/data
ENV PYTHONUNBUFFERED=1
CMD ["python3", "-m", "tg_folder_manager"]