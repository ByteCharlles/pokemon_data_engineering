# 🐉 Pokémon Data Engineering & Analytics

Este projeto implementa um pipeline de dados completo (ETL) utilizando a **Arquitetura de Medalhão (Bronze, Silver, Gold)**. O objetivo é extrair dados da API de Pokemon, processar estatísticas de 50.000 combates e apresentar insights estratégicos através de um Dashboard interativo.

## 🏗️ Arquitetura do Projeto (Medallion)

* **Bronze (Raw):** Ingestão de dados brutos da PokéAPI em formato JSON.
* **Silver (Cleaned):** Limpeza, tipagem e padronização dos dados. Exportação em **Parquet (PyArrow)** para performance e **CSV** para portabilidade.
* **Gold (Analytics):** Cruzamento das tabelas de Pokémons e Combates para cálculo de indicadores de performance.

## 🛠️ Stack Tecnológica

* **Linguagem:** Python 3.12
* **Processamento:** Pandas, PyArrow (Otimização colunar)
* **Banco de Dados:** PostgreSQL (SQLAlchemy + Psycopg2 com lógica de Upsert)
* **Visualização:** Streamlit & Plotly (Gráficos dinâmicos e correlações de Pokemons)
* **Infraestrutura:** Loguru (Logs) e Dotenv.

## 📊 Insights Analíticos

O projeto responde às 4 perguntas fundamentais do desafio com base na análise estatística dos 50.000 combates processados:

1. **Atributos Determinantes:** A **Velocidade (Speed)** é o fator crítico para o sucesso, apresentando uma correlação de **~0.93** com a vitória. Em um sistema de turnos, atacar primeiro é a maior vantagem competitiva.
2. **Performance por Tipo:** Os tipos **Flying (Voador)**, **Dragon (Dragão)** e **Electric (Elétrico)** dominam o meta. O tipo Flying, em especial, se destaca pela alta frequência de Pokémons com base de velocidade elevada.
3. **Dream Team (Top 6):** Com base no Win Rate histórico, a equipe com maior probabilidade de vitória é composta por:
* *Mega Aerodactyl (98.4%), Weavile (97.4%), Tornadus-T (96.8%), Mega Beedrill (96.6%), Aerodactyl (96.4%) e Mega Gallade (96.1%).*


4. **Correlações de Atributos:** * **Ataque:** Possui correlação moderada (~0.50).
* **Defesa/HP:** Apresentam correlação baixa (~0.15 a 0.25), indicando que ser um "tanque" não compensa a falta de agilidade neste dataset.

A métrica principal para a Camada Gold é:


$$\text{Win Rate} = \left( \frac{\text{Total Wins}}{\text{Total Battles}} \right) \times 100$$

## 🚀 Como Executar

1. **Clone o repositório:**
```bash
git clone https://github.com/seu-usuario/pokemon-data-engineering.git
cd pokemon-data-engineering

```


2. **Ambiente Virtual (Recomendado):**
```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate

```


3. **Configuração de Variáveis de Ambiente:**
Crie um arquivo `.env` na raiz do projeto com suas credenciais do PostgreSQL:
```env
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="db_pokemon"
DB_USER="seu_usuario"
DB_PASSWORD="sua_senha"

```


4. **Instalação de Dependências:**
```bash
pip install --upgrade pip
pip install -r requirements.txt

```


5. **Execução do Pipeline:**
```bash
# Linux/Mac
PYTHONPATH=. python3 main.py

# Windows
$env:PYTHONPATH="."
python main.py

```


6. **Iniciar o Dashboard:**
```bash
# Linux/Mac
PYTHONPATH=. streamlit run app/streamlit_app.py

# Windows
$env:PYTHONPATH="."
streamlit run app/streamlit_app.py

```

## 🏗️ Estrutura do Projeto

* `etl/`: Scripts de extração e limpeza de dados.
* `data/`: Armazenamento dos dados processados (arquivos `.csv`, `.parquet` ou `.db`).
* `app/`: Código fonte da aplicação Streamlit.
* `notebooks/`: Análises exploratórias preliminares.

## 📈 Análises Realizadas

O dashboard foca em responder:

1. **Win Rate por Tipo:** Quais tipos de Pokémon dominam o meta?
2. **Influência de Atributos:** Qual a correlação entre *Speed*, *Attack* e a vitória final?
3. **Team Builder:** Sugestão de composição baseada em dados históricos.

## 📁 Estrutura do Projeto

```text
├── app/                # Aplicação Streamlit
├── assets/             # PDF da página do projeto final no Streamlit
├── data/               # Armazenamento local (Bronze, Silver, Gold)
├── src/
│   ├── infrastructure/ # Conexão com API e Banco de Dados
│   ├── pipeline/       # Scripts de ETL (Extract, Transform, Load, Gold)
│   └── utils/          # Logger e utilitários
└── main.py             # Orquestrador do pipeline

```

> 🤖 **Nota:** Este projeto contou com o auxílio de Inteligência Artificial para depuração de erros e refatoração de código.