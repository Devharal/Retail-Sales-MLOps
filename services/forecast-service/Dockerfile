FROM python:3.9-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
RUN chmod +x ./app/start_app.sh

CMD ["./app/start_app.sh"]
