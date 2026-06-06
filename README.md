# Modelo ao Deploy: Diagnostico de Falhas em Motores Industriais

Curso completo que percorre o ciclo de vida de um projeto de Machine Learning em producao: da definicao do problema ate a publicacao na nuvem.

---

## Ementa do Curso

| Modulo | Topico | Tecnologias |
|--------|--------|-------------|
| 01 | Definicao de Projeto e Desenvolvimento do Modelo | Python, scikit-learn, XGBoost |
| 02 | Conteinerizacao e Serving via API | FastAPI, Docker |
| 03 | Desenvolvimento de Dashboard | Streamlit |
| 04 | Deploy do Modelo na AWS | AWS, Docker |
| 05 | Publicacao da Aplicacao e Boas Praticas | AWS, CI/CD |

---

## Problema de Negocio

Motores industriais sao ativos criticos em plantas de manufatura. Uma falha nao prevista causa paradas de producao, danos ao equipamento e riscos a seguranca. A manutencao tradicional, feita em intervalos fixos, e ineficiente: ou e feita cedo demais (custo desnecessario) ou tarde demais (apos a falha).

**Objetivo:** Construir um sistema que, a partir de leituras de sensores em tempo real, classifique automaticamente o estado do motor em uma das quatro categorias abaixo.

| Codigo | Estado | Descricao |
|--------|--------|-----------|
| 0 | Normal | Operacao dentro dos parametros esperados |
| 1 | Desbalanceamento | Vibracao alta e rotacao instavel |
| 2 | Superaquecimento | Temperatura e corrente elevadas |
| 3 | Falha Mecanica | Queda de rotacao com vibracao e corrente altas |

---

## Dataset

Banco de dados SQLite em `data/motor.db` com tres tabelas:

**`motores`** - Cadastro dos 20 motores monitorados
| Coluna | Tipo | Descricao |
|--------|------|-----------|
| motor_id | INTEGER | Identificador unico |
| fabricante | TEXT | Ex: Siemens, ABB, WEG |
| modelo | TEXT | Modelo do motor |
| potencia_kw | REAL | Potencia nominal em kW |
| ano_instalacao | INTEGER | Ano de instalacao |

**`leituras`** - 30.000 leituras de sensores (intervalo de 1 minuto)
| Coluna | Tipo | Descricao |
|--------|------|-----------|
| motor_id | INTEGER | Referencia ao motor |
| timestamp | TIMESTAMP | Data e hora da leitura |
| rotacao_rpm | REAL | Rotacao em RPM |
| vibracao_mm_s | REAL | Vibracao em mm/s |
| temperatura_c | REAL | Temperatura em graus Celsius |
| corrente_a | REAL | Corrente eletrica em Amperes |
| falha | INTEGER | Classe alvo (0 a 3) |

**`tipos_falha`** - Descricao de cada classe de falha

**Distribuicao das classes:**

```
Normal           : 26.291 leituras (87.6%)
Desbalanceamento :  1.205 leituras  (4.0%)
Superaquecimento :  1.718 leituras  (5.7%)
Falha Mecanica   :    786 leituras  (2.6%)
```

---

## Estrutura do Projeto

```
ModeloAoDeploy/
├── data/
│   └── motor.db
├── models/
│   └── motor_classifier.joblib      (gerado apos treinamento)
├── notebooks/
│   ├── 01_eda.ipynb                 (analise exploratoria)
│   └── 02_modeling.ipynb            (treinamento e avaliacao)
├── src/
│   ├── functions/
│   │   ├── database.py              (conexao e queries SQLite)
│   │   └── model.py                 (treinar, avaliar, salvar, carregar)
│   └── utils/
│       ├── preprocessing.py         (feature engineering e split)
│       └── visualization.py         (plots EDA e avaliacao)
├── .env
├── requirements.txt
└── README.md
```

---

## Como Executar

### 1. Configurar ambiente

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/Mac
# .venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

### 2. Configurar variaveis de ambiente

O arquivo `.env` ja esta configurado com os caminhos padrao:

```
DB_PATH=data/motor.db
MODEL_PATH=models/motor_classifier.joblib
```

### 3. Executar a EDA

Abra o notebook `notebooks/01_eda.ipynb` no VS Code ou Jupyter e execute todas as celulas.

### 4. Treinar o modelo

Abra o notebook `notebooks/02_modeling.ipynb` e execute todas as celulas. O artefato sera salvo em `models/motor_classifier.joblib`.

### 5. Usar o modelo via codigo

```python
from src.functions.model import load

artefato = load()
model  = artefato["model"]
scaler = artefato["scaler"]

# X deve conter as colunas de FEATURE_COLS (ver preprocessing.py)
predicao = model.predict(scaler.transform(X))
```

---

## Abordagem de Machine Learning

### Feature Engineering

Alem das quatro leituras brutas dos sensores, sao criadas features derivadas com janela deslizante de 5 minutos por motor:

| Feature | Descricao |
|---------|-----------|
| `rotacao_mean` | Media movel da rotacao |
| `vibracao_std` | Desvio padrao da vibracao |
| `temperatura_max` | Maxima de temperatura |
| `corrente_mean` | Media movel da corrente |
| `vibracao_por_rotacao` | Razao vibracao / rotacao |

### Modelo

**Random Forest** com `class_weight="balanced"` para compensar o desbalanceamento de classes.

### Metricas esperadas

| Metrica | Valor esperado |
|---------|---------------|
| Accuracy | > 0.90 |
| F1 Macro | > 0.85 |

---

## Proximos Modulos

**Modulo 02** vai empacotar este modelo em uma API REST usando FastAPI e Docker, expondo um endpoint `/predict` que recebe leituras de sensores e retorna a classificacao da falha.