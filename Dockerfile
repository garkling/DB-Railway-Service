FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /code

COPY pyproject.toml README.md ./
RUN mkdir -p app && touch app/__init__.py
RUN pip install --upgrade pip && pip install -e ".[dev]"

COPY app/ app/
COPY sql/ sql/
COPY tests/ tests/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]