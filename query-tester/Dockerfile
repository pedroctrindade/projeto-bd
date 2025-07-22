FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY compare_query_speed.py .

CMD ["python", "compare_query_speed.py"]
