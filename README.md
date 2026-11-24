# Select AI Local — Agente Text-to-SQL com LangChain, Ollama (Docker) e Streamlit

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-LCEL-1C3C3C?logo=langchain&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Docker_LLM-000000?logo=ollama&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Schema_HR_Oracle-003B57?logo=sqlite&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Data_App-FF4B4B?logo=streamlit&logoColor=white)

Uma implementação **local e sem custo de API** inspirada no recurso **Select AI** do **Oracle AI Database 26ai**. Este projeto demonstra consultas a um conjunto de dados fictício, baseado em um subconjunto do schema **HR** da Oracle, por meio de **linguagem natural em Português do Brasil (Text-to-SQL / NL2SQL)**, orquestrado com **LangChain (LCEL)**, **Ollama em Docker** e interface interativa em **Streamlit**. O protótipo não se conecta ao Oracle Database nem deve ser usado com dados reais de clientes ou funcionários.

---

## Visão Geral e Problema de Negócio

Consultar dados estruturados em bancos relacionais normalmente exige domínio de SQL (`JOINs`, `GROUP BY`, `HAVING`, subqueries). Recursos modernos como o *Oracle 26ai Select AI* democratizam esse acesso traduzindo perguntas em linguagem natural para SQL, mas exigem **assinaturas de APIs pagas na nuvem** (OpenAI, OCI Generative AI, Cohere) e envio de metadados corporativos para fora do ambiente local.

Este projeto demonstra uma experiência semelhante em ambiente local:
- **Inferência local sem custo de API:** O modelo roda em container Docker via **Ollama** (`qwen3.5:0.8b`); a imagem e o modelo precisam ser baixados na configuração inicial.
- **4 modos inspirados no Select AI (`runsql`, `showsql`, `narrate` e `chat`):** Demonstra os fluxos em uma interface visual local; não reproduz nem substitui o produto Oracle.
- **Proteção de leitura no SQLite:** Validação de comandos e abertura do arquivo do banco em modo somente leitura. Isso é uma proteção para a demonstração, não uma certificação de segurança para produção.

---

## Arquitetura do Sistema (Pipeline Text-to-SQL com LCEL)

```mermaid
flowchart LR
    subgraph Contexto["1. Metadados e Schema Relacional"]
        DB[("SQLite Local<br/>(hr_oracle.db)")] --> DDL["Extração de Schema DDL<br/>(EMPLOYEES, JOB_HISTORY,<br/>DEPARTMENTS, JOBS)"]
    end

    subgraph Orquestracao["2. Orquestração LangChain (LCEL) + Ollama Docker"]
        User["Pergunta em Português<br/>(Streamlit UI)"] --> Mode{"Modo Select AI"}
        DDL --> PromptSQL["ChatPromptTemplate<br/>(Text-to-SQL)"]
        Mode -- "showsql / runsql / narrate" --> PromptSQL
        PromptSQL --> LLM["ChatOllama (Docker)<br/>(qwen3.5:0.8b)"]
        LLM --> Clean["Sanitização + Guardrail<br/>(Somente SELECT)"]
    end

    subgraph Execucao["3. Execução e Entrega"]
        Clean -- "showsql" --> OutSQL["Exibe Código SQL"]
        Clean -- "runsql" --> ExecSQL["Executa no SQLite"]
        ExecSQL --> OutTable["Tabela Interativa<br/>(DataFrame)"]
        Clean -- "narrate" --> ExecNarrate["Executa SQL +<br/>Chain Narrativa PT-BR"]
        ExecNarrate --> OutNarrate["Explicação Executiva<br/>em Português"]
    end
```

---

## Modos demonstrados (inspirados no Select AI)

| Modo Select AI | Comando Equivalente no Oracle 26ai | O que a Aplicação Faz |
| :--- | :--- | :--- |
| **`runsql`** | `SELECT AI runsql <pergunta>;` | Converte a pergunta em SQL, valida a consulta, executa no SQLite local e exibe a tabela + query utilizada. |
| **`showsql`** | `SELECT AI showsql <pergunta>;` | Gera e exibe a instrução SQL, sem executá-la no banco. |
| **`narrate`** | `SELECT AI narrate <pergunta>;` | Gera o SQL, executa no SQLite local e usa outra *chain* LCEL para narrar os resultados em Português do Brasil. |
| **`chat`** | `SELECT AI chat <pergunta>;` | Conversa livre com o LLM local; não consulta os dados do banco. |

Os comandos acima são apresentados como referência conceitual. A aplicação não envia comandos `SELECT AI` a um banco Oracle.

---

## Tecnologias Utilizadas

| Camada | Tecnologia | Papel no Projeto |
| :--- | :--- | :--- |
| **Front-end / Data App** | [Streamlit](https://streamlit.io/) | Interface de chat, seletor de modos (`st.segmented_control`), métricas e explorador de tabelas. |
| **Orquestração LLM** | [LangChain (LCEL)](https://www.langchain.com/) | Pipelines declarativos (`prompt \| llm \| StrOutputParser()`) para Text-to-SQL e Data-to-Text. |
| **Motor de IA (Docker)** | [Ollama](https://ollama.com/) (`qwen3.5:0.8b`) | Inferência local de baixa latência containerizada via Docker Compose. |
| **Banco Relacional** | [SQLite](https://www.sqlite.org/) + [Pandas](https://pandas.pydata.org/) | Banco de dados embarcado pré-populado com o schema clássico `HR` da Oracle. |

---

## Estrutura do Repositório

```text
AgenteSelectAILocal/
├── app.py                 # Interface Streamlit e pipelines LangChain (LCEL) para os 4 modos do Select AI
├── database.py            # Criação automática do banco SQLite (Schema HR), extração DDL e guardrails SQL
├── docker-compose.yml     # Serviço Docker para execução isolada do Ollama com volume persistente
├── requirements.txt       # Dependências Python do projeto
├── tests/                 # Testes automatizados do acesso somente leitura ao SQLite
├── docs/                  # Material de apoio para demonstração
└── README.md              # Documentação técnica e guia de execução
```

---

## Como Executar o Projeto Localmente

### 1. Subir o Ollama no Docker e Baixar o Modelo

```bash
# Subir o container do Ollama na porta 11434
docker compose up -d

# Baixar o modelo leve utilizado pelo agente
docker exec -it ollama-select-ai ollama pull qwen3.5:0.8b
```

*(Nota: Caso você já tenha outro container do Ollama ou o Ollama local rodando na porta `11434` com o modelo `qwen3.5:0.8b`, a aplicação conectará nele automaticamente).*

### 2. Instalar as Dependências Python

```bash
# Criar e ativar ambiente virtual (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar bibliotecas
pip install -r requirements.txt
```

### 3. Executar a Aplicação no Streamlit

```bash
streamlit run app.py
```

Acesse no navegador em: **`http://localhost:8501`**

### 4. Executar os testes automatizados

```bash
python -m unittest discover -s tests -v
```

---

## Exemplos de Consultas em Português para Testar

1. **"Mostre quais funcionários mudaram de cargo pelo menos duas vezes"**
   - *Reproduz o exemplo clássico do artigo do Oracle 26ai Select AI, realizando `JOIN` entre `EMPLOYEES` e `JOB_HISTORY` com `GROUP BY` e `HAVING COUNT(DISTINCT JOB_ID) >= 2` (retornando Neena Yang, Jennifer Whalen e Jonathon Taylor).*
2. **"Liste todos os funcionários e seus salários"**
   - *Cruza `EMPLOYEES` e `DEPARTMENTS` ordenando pelos maiores salários.*
3. **"Qual a média salarial por departamento?"**
   - *Gera agregação com `AVG(SALARY)` e `COUNT(EMPLOYEE_ID)` agrupada por departamento.*
4. **"Quem são os funcionários do departamento de TI (IT)?"**
   - *Filtra colaboradores pelo nome do departamento na tabela `DEPARTMENTS`.*

---

## Demonstração para gestor ou cliente

Consulte o [roteiro de apresentação](docs/roteiro-apresentacao.md) para a sequência sugerida, pré-requisitos, resultados verificados e limitações do protótipo.
