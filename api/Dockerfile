FROM public.ecr.aws/docker/library/python:3.13-slim

WORKDIR /app

# Security patch:
# CVE-2026-103111: update libpcre2-8-0 to the fixed Debian release.
RUN apt-get update \
    && apt-get install -y --no-install-recommends --only-upgrade libpcre2-8-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt \
    && python -m pip install --no-cache-dir --upgrade \
       "msgpack>=1.2.1" \
       "setuptools>=78.1.1"

COPY app ./app

RUN adduser --disabled-password --gecos "" appuser

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
