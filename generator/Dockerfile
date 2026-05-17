FROM python:3.12-slim

WORKDIR /app

COPY generate_fake_logs.py /app/generate_fake_logs.py

ENV DATA_DIR=/app/data
ENV INTERVAL_SECONDS=10

CMD ["python", "/app/generate_fake_logs.py"]