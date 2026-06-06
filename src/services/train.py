import boto3

from src.config import MODEL_PATH, S3_BUCKET, S3_MODEL_KEY
from src.functions.database import load_data
from src.functions.model import save, train
from src.utils.preprocessing import engineer_features, prepare_dataset


def main():
    print("Carregando dados...")
    df = load_data()
    df = engineer_features(df)

    X_train, _, y_train, _ = prepare_dataset(df)

    print(f"Treinando com {len(X_train)} amostras...")
    pipeline = train(X_train, y_train)
    save(pipeline)
    print(f"Modelo salvo em {MODEL_PATH}")

    if S3_BUCKET:
        print(f"Enviando para s3://{S3_BUCKET}/{S3_MODEL_KEY}...")
        s3 = boto3.client("s3")
        s3.upload_file(str(MODEL_PATH), S3_BUCKET, S3_MODEL_KEY)
        print("Concluido.")
    else:
        print("S3_BUCKET nao configurado — artefato salvo apenas localmente.")


if __name__ == "__main__":
    main()
