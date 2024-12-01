FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY app2.py .

EXPOSE 5000

CMD ["python", "app2.py"]
