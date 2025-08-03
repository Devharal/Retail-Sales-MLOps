# FROM python:3.9.17-slim

# ARG WEB_UI_PORT
# ENV WEB_UI_PORT=${WEB_UI_PORT}

# COPY requirements.txt /service/requirements.txt
# RUN pip install -r /service/requirements.txt

# COPY app/ /service/app/
# WORKDIR /service/app

# EXPOSE ${WEB_UI_PORT}

FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 8000
CMD ["streamlit", "run", "app.py", "--server.port=8000", "--server.enableCORS=false"]
