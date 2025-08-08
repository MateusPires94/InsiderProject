FROM python:3.11-slim

RUN mkdir -p /mlflow/

WORKDIR /mlflow

# Instala mlflow e boto3 (para S3/MinIO), psycopg2-binary para Postgres e sklearn só como exemplo
RUN pip install --no-cache-dir mlflow==3.1.4 boto3 psycopg2-binary pymysql

COPY create_bucket.py entrypoint.sh ./

RUN chmod +x entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["./entrypoint.sh"]