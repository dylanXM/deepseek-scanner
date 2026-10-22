FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN ollama pull deepseek-r1:7b
CMD ["python", "app.py"]
