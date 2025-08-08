import boto3
import time
import os
from botocore.exceptions import ClientError

def create_bucket():
    s3_endpoint = os.getenv("MLFLOW_S3_ENDPOINT_URL", "http://minio:9000")
    access_key = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")
    bucket_name = os.getenv("MLFLOW_S3_BUCKET", "mlflow")

    s3 = boto3.resource(
        's3',
        endpoint_url=s3_endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name='us-east-1',
    )

    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' já existe.")
    except ClientError:
        # Criar bucket
        s3.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' criado com sucesso.")

if __name__ == "__main__":
    # Espera o MinIO iniciar (opcional, ajustar conforme necessidade)
    time.sleep(5)
    create_bucket()