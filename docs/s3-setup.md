# Configurar S3 para Artefatos do Modelo

O bucket S3 armazena o modelo treinado (`.joblib`). O pipeline de treino faz o upload a cada execução e a API de inferência faz o download na inicialização.

---

## 1. Criar o bucket

**AWS Console → S3 → Create bucket**

| Campo | Valor |
|---|---|
| Bucket name | `motor-model-artifacts` (ou outro nome único) |
| Region | mesma região do EB e ECR (ex: `us-east-1`) |
| Block all public access | ativado |
| Versioning | recomendado ativar |

Ou via CLI:

```bash
aws s3api create-bucket \
  --bucket motor-model-artifacts \
  --region us-east-1
```

---

## 2. Permissões IAM

### Usuario de CI/CD (GitHub Actions)

O usuario utilizado pelo GitHub Actions (cujas chaves estao nos secrets `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`) precisa de permissao para **escrever** no bucket.

**IAM → Users → seu usuario → Add permissions → Attach policies directly**

Selecione `AmazonS3FullAccess` ou crie uma policy customizada:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject"],
      "Resource": "arn:aws:s3:::motor-model-artifacts/*"
    }
  ]
}
```

### Instancia EC2 do Elastic Beanstalk (backend)

A instancia precisa de permissao para **ler** o modelo no bucket.

**IAM → Roles → aws-elasticbeanstalk-ec2-role → Add permissions → Attach policies**

Selecione `AmazonS3ReadOnlyAccess` ou a policy customizada acima (somente `s3:GetObject`).

---

## 3. Configurar variavel de ambiente no Elastic Beanstalk

A API precisa saber o nome do bucket para carregar o modelo.

**EB Console → motor-inference-env → Configuration → Updates, monitoring, and logging → Edit**

Em **Environment properties**, adicione:

| Key | Value |
|---|---|
| `S3_BUCKET` | `motor-model-artifacts` |

---

## 4. Adicionar secret no GitHub

**GitHub → repositorio → Settings → Secrets and variables → Actions → New repository secret**

| Secret | Valor |
|---|---|
| `S3_BUCKET` | `motor-model-artifacts` |

---

## 5. Fazer o primeiro upload do modelo

Antes do pipeline agendado rodar, envie o modelo atual manualmente:

```bash
aws s3 cp models/motor_classifier.joblib \
  s3://motor-model-artifacts/models/motor_classifier.joblib
```

Ou execute o workflow de treino manualmente:
**GitHub → Actions → Train Model → Run workflow**

---

## Estrutura no bucket

```
motor-model-artifacts/
└── models/
    └── motor_classifier.joblib
```

---

## Fluxo completo

```
GitHub Actions (cron 1h)
  └── treina com data/motor.db
  └── salva models/motor_classifier.joblib
  └── upload para S3

Elastic Beanstalk (backend)
  └── inicializa container
  └── download do modelo do S3
  └── serve /predict
```