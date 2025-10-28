FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./
COPY templates/ ./templates/

EXPOSE 5002

ENV ANALYZER_URL=http://complexity-analyzer:5000/analyze

CMD ["flask", "run", "--host=0.0.0.0", "--port=5002"]