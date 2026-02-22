FROM python:3.9-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY ai_daily_digest/ ai_daily_digest/

CMD ["python", "-m", "ai_daily_digest"]
