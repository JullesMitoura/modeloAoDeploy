# Deploy Manual na AWS — macOS e Linux

Guia para publicar a API de inferencia no Elastic Beanstalk usando o Amazon ECR como registro de imagens Docker.

## Variaveis

Substitua os placeholders abaixo pelos valores da sua conta antes de executar os comandos:

| Placeholder | Descricao | Exemplo |
|---|---|---|
| `<AWS_ACCOUNT_ID>` | ID numerico da sua conta AWS | `975037863921` |
| `<REGION>` | Regiao AWS escolhida | `us-east-1` |

---

## Pre-requisitos

### 1. Instalar AWS CLI e EB CLI

```bash
brew install awscli awsebcli
```

### 2. Configurar credenciais

```bash
aws configure
```

Preencha com os dados da sua conta:

```
AWS Access Key ID:     <sua access key>
AWS Secret Access Key: <sua secret key>
Default region name:   <REGION>
Default output format: json
```

> As chaves sao geradas em: **AWS Console → seu usuario → Security credentials → Access keys → Create access key**

---

## Configurar o Dockerrun.aws.json

Edite o arquivo `Dockerrun.aws.json` substituindo `<AWS_ACCOUNT_ID>` e `<REGION>` pelos valores da sua conta:

```json
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "<AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/motor-inference:latest",
    "Update": "true"
  },
  "Ports": [
    {
      "ContainerPort": 8000,
      "HostPort": 80
    }
  ]
}
```

---

## Criar o repositorio no ECR

Via console: **Amazon ECR → Registros privados → Repositorios → Criar repositorio**

Nome: `motor-inference`

Ou via CLI:

```bash
aws ecr create-repository --repository-name motor-inference --region <REGION>
```

---

## Build e Push da Imagem

### 1. Autenticar o Docker no ECR

```bash
aws ecr get-login-password --region <REGION> | \
  docker login --username AWS --password-stdin \
  <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com
```

### 2. Build da imagem

```bash
docker build -t motor-inference .
```

### 3. Tag da imagem

```bash
docker tag motor-inference:latest \
  <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/motor-inference:latest
```

### 4. Push para o ECR

```bash
docker push \
  <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/motor-inference:latest
```

---

## Deploy no Elastic Beanstalk

### Primeiro deploy

```bash
eb init motor-inference --platform docker --region <REGION>
eb create motor-inference-env --single
```

O flag `--single` cria um ambiente sem load balancer (~$7.50/mes vs ~$25/mes com load balancer).

### Verificar o ambiente

```bash
eb status
```

A URL da aplicacao aparece no campo `CNAME`. Acesse `/docs` para a documentacao interativa da API.

---

## Atualizar o Deploy

A cada nova versao do modelo ou da API, repita os passos de build e push e execute:

```bash
eb deploy
```

---

## Encerrar o Ambiente

Para evitar cobranças quando o ambiente nao estiver em uso:

```bash
eb terminate motor-inference-env
```

---

## Custos estimados (single-instance)

| Recurso | Custo estimado/mes |
|---|---|
| EC2 t3.micro | ~$7.50 |
| ECR (armazenamento) | ~$0.02 |
| **Total** | **~$7.52** |

> Lembre de encerrar o ambiente apos o uso para evitar cobranças desnecessarias.
