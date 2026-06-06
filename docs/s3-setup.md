# Configurar S3, ECR e Elastic Beanstalk — Modulo 06

Este guia cobre todos os recursos AWS que precisam ser criados manualmente antes de executar os workflows do modulo 06.

---

## 1. Criar o bucket S3

O bucket armazena o modelo treinado. O pipeline de retreino faz o upload a cada execucao e a API de inferencia faz o download na inicializacao.

**AWS Console → S3 → Create bucket**

| Campo | Valor |
|---|---|
| Bucket name | `motor-model-artifacts` (deve ser globalmente unico) |
| Region | mesma regiao do EB e ECR (ex: `us-east-1`) |
| Block all public access | ativado |
| Versioning | recomendado ativar |

Ou via CLI:

```bash
aws s3api create-bucket \
  --bucket motor-model-artifacts \
  --region us-east-1
```

---

## 2. Criar os repositorios ECR

Dois repositorios sao necessarios: um para o backend e outro para o frontend.

```bash
aws ecr create-repository --repository-name motor-inference --region us-east-1
aws ecr create-repository --repository-name motor-frontend  --region us-east-1
```

Ou via console: **ECR → Repositories → Create repository** para cada um.

---

## 3. Configurar permissoes IAM

### 3.1 Usuario de CI/CD (GitHub Actions)

O usuario cujas chaves estao nos secrets `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` precisa de permissao para escrever no S3 e fazer push no ECR.

**IAM → Users → seu usuario → Add permissions → Attach policies directly**

Policies necessarias:
- `AmazonEC2ContainerRegistryFullAccess` — push de imagens no ECR
- `AmazonS3FullAccess` — upload do modelo no S3

Ou crie uma policy customizada com escopo minimo:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecr:PutImage"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject"],
      "Resource": "arn:aws:s3:::motor-model-artifacts/*"
    }
  ]
}
```

### 3.2 Instancia EC2 do Elastic Beanstalk (backend)

A instancia precisa de permissao para ler imagens do ECR e baixar o modelo do S3.

**IAM → Roles → aws-elasticbeanstalk-ec2-role → Add permissions → Attach policies**

Policies necessarias:
- `AmazonEC2ContainerRegistryReadOnly` — pull de imagens do ECR
- `AmazonS3ReadOnlyAccess` — download do modelo do S3

---

## 4. Criar os ambientes Elastic Beanstalk

### Backend (ja existente no modulo 03)

Se ainda nao existir:

```bash
eb init motor-inference --platform docker --region us-east-1
eb create motor-inference-env --single
```

### Frontend (novo no modulo 06)

```bash
eb init motor-frontend --platform docker --region us-east-1
eb create motor-frontend-env --single
```

---

## 5. Configurar variaveis de ambiente no EB

### Backend — variavel S3_BUCKET

A API precisa saber o nome do bucket para carregar o modelo.

**EB Console → motor-inference-env → Configuration → Updates, monitoring, and logging → Edit**

Em **Environment properties**, adicione:

| Key | Value |
|---|---|
| `S3_BUCKET` | `motor-model-artifacts` |

---

## 6. Adicionar secrets no GitHub

**GitHub → repositorio → Settings → Secrets and variables → Actions → New repository secret**

| Secret | Descricao |
|---|---|
| `AWS_ACCESS_KEY_ID` | Chave de acesso IAM |
| `AWS_SECRET_ACCESS_KEY` | Chave secreta IAM |
| `AWS_REGION` | Ex: `us-east-1` |
| `S3_BUCKET` | Nome do bucket (ex: `motor-model-artifacts`) |

---

## 7. Upload inicial do modelo

Antes do pipeline agendado rodar, envie o modelo atual manualmente:

```bash
aws s3 cp models/motor_classifier.joblib \
  s3://motor-model-artifacts/models/motor_classifier.joblib
```

Ou dispare o workflow manualmente:
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
GitHub Actions (cron — toda hora)
  └── treina com data/motor.db
  └── upload para S3

Elastic Beanstalk — backend (motor-inference-env)
  └── inicializa container
  └── download do modelo do S3
  └── serve /predict

GitHub Actions (push em modulo06 / main)
  └── build Dockerfile.backend → push ECR motor-inference → deploy EB backend
  └── build Dockerfile.frontend → push ECR motor-frontend → deploy EB frontend
```
