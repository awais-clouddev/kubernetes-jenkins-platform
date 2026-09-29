FROM public.ecr.aws/docker/library/python:3.13-slim

WORKDIR /app

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
