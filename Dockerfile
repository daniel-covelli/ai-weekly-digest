FROM python:3.9-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY ai_daily_digest/ ai_daily_digest/

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "ai_daily_digest.app:app"]
