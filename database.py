"""
Modulo de Banco de Dados Local (SQLite) com o Schema HR da Oracle.
Recria localmente as tabelas EMPLOYEES, JOB_HISTORY, DEPARTMENTS e JOBS
utilizadas na demonstracao oficial do Oracle AI Database 26ai (Select AI).
"""

import re
import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).parent / "hr_oracle.db"

SCHEMA_DDL = """
CREATE TABLE IF NOT EXISTS DEPARTMENTS (
    DEPARTMENT_ID INTEGER PRIMARY KEY,
    DEPARTMENT_NAME TEXT NOT NULL,
    LOCATION TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS JOBS (
    JOB_ID TEXT PRIMARY KEY,
    JOB_TITLE TEXT NOT NULL,
    MIN_SALARY REAL,
    MAX_SALARY REAL
);

CREATE TABLE IF NOT EXISTS EMPLOYEES (
    EMPLOYEE_ID INTEGER PRIMARY KEY,
    FIRST_NAME TEXT NOT NULL,
    LAST_NAME TEXT NOT NULL,
    EMAIL TEXT NOT NULL,
    HIRE_DATE TEXT NOT NULL,
    JOB_ID TEXT NOT NULL,
    SALARY REAL NOT NULL,
    DEPARTMENT_ID INTEGER,
    FOREIGN KEY (JOB_ID) REFERENCES JOBS(JOB_ID),
    FOREIGN KEY (DEPARTMENT_ID) REFERENCES DEPARTMENTS(DEPARTMENT_ID)
);

CREATE TABLE IF NOT EXISTS JOB_HISTORY (
    EMPLOYEE_ID INTEGER NOT NULL,
    START_DATE TEXT NOT NULL,
    END_DATE TEXT NOT NULL,
    JOB_ID TEXT NOT NULL,
    DEPARTMENT_ID INTEGER NOT NULL,
    PRIMARY KEY (EMPLOYEE_ID, START_DATE),
    FOREIGN KEY (EMPLOYEE_ID) REFERENCES EMPLOYEES(EMPLOYEE_ID),
    FOREIGN KEY (JOB_ID) REFERENCES JOBS(JOB_ID),
    FOREIGN KEY (DEPARTMENT_ID) REFERENCES DEPARTMENTS(DEPARTMENT_ID)
);
""".strip()


def inicializar_banco() -> Path:
    """Cria e popula o banco SQLite local com o schema HR da Oracle caso nao exista."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript(SCHEMA_DDL)

    # Verifica se ja foi populado
    cursor.execute("SELECT COUNT(*) FROM EMPLOYEES")
    if cursor.fetchone()[0] == 0:
        departamentos = [
            (10, "Administration", "Sao Paulo"),
            (50, "Shipping", "Campinas"),
            (60, "IT", "Sao Paulo"),
            (80, "Sales", "Rio de Janeiro"),
            (90, "Executive", "Sao Paulo"),
            (110, "Accounting", "Belo Horizonte"),
        ]
        cursor.executemany(
            "INSERT INTO DEPARTMENTS VALUES (?, ?, ?)", departamentos
        )

        cargos = [
            ("AD_VP", "Administration Vice President", 15000, 30000),
            ("AD_ASST", "Administration Assistant", 3000, 6000),
            ("SA_REP", "Sales Representative", 6000, 12000),
            ("SA_MAN", "Sales Manager", 10000, 20000),
            ("ST_MAN", "Stock Manager", 5500, 8500),
            ("IT_PROG", "Programmer", 4000, 10000),
            ("AC_ACCOUNT", "Public Accountant", 4200, 9000),
            ("AC_MGR", "Accounting Manager", 8200, 16000),
        ]
        cursor.executemany("INSERT INTO JOBS VALUES (?, ?, ?, ?)", cargos)

        colaboradores = [
            (101, "Neena", "Yang", "NYANG", "2019-09-21", "AD_VP", 17000.0, 90),
            (200, "Jennifer", "Whalen", "JWHALEN", "2017-09-17", "AD_ASST", 4400.0, 10),
            (176, "Jonathon", "Taylor", "JTAYLOR", "2020-03-24", "SA_REP", 8600.0, 80),
            (102, "Lex", "De Haan", "LDEHAAN", "2021-01-13", "AD_VP", 17000.0, 90),
            (122, "Payam", "Kaufling", "PKAUFLIN", "2022-05-01", "ST_MAN", 7900.0, 50),
            (103, "Alexander", "Hunold", "AHUNOLD", "2021-01-03", "IT_PROG", 9000.0, 60),
            (104, "Bruce", "Ernst", "BERNST", "2022-05-21", "IT_PROG", 6000.0, 60),
            (205, "Shelley", "Higgins", "SHIGGINS", "2018-06-07", "AC_MGR", 12008.0, 110),
        ]
        cursor.executemany(
            "INSERT INTO EMPLOYEES VALUES (?, ?, ?, ?, ?, ?, ?, ?)", colaboradores
        )

        # Historico de mudancas de cargo:
        # Neena Yang (101), Jennifer Whalen (200) e Jonathon Taylor (176) mudaram >= 2 vezes
        historico = [
            (101, "2019-09-21", "2021-10-27", "AC_ACCOUNT", 110),
            (101, "2021-10-28", "2023-03-15", "AC_MGR", 110),
            (200, "2017-09-17", "2020-06-17", "AD_ASST", 90),
            (200, "2020-07-01", "2022-12-31", "AC_ACCOUNT", 90),
            (176, "2020-03-24", "2021-12-31", "SA_REP", 80),
            (176, "2022-01-01", "2023-12-31", "SA_MAN", 80),
            (102, "2021-01-13", "2023-07-24", "IT_PROG", 60),
        ]
        cursor.executemany(
            "INSERT INTO JOB_HISTORY VALUES (?, ?, ?, ?, ?)", historico
        )

        conn.commit()

    conn.close()
    return DB_PATH


def obter_schema_ddl() -> str:
    """Retorna a definicao DDL das tabelas para servir de contexto ao LLM."""
    return SCHEMA_DDL


def limpar_query_sql(texto_llm: str) -> str:
    """Extrai apenas a instrucao SQL limpa gerada pelo LLM."""
    match = re.search(r"```(?:sql)?\s*([\s\S]*?)```", texto_llm, re.IGNORECASE)
    if match:
        texto_llm = match.group(1)

    texto_llm = texto_llm.strip()

    # Caso o modelo retorne texto antes do SELECT/WITH, isola a partir do SELECT/WITH
    select_match = re.search(r"\b(SELECT|WITH)\b[\s\S]*", texto_llm, re.IGNORECASE)
    if select_match:
        texto_llm = select_match.group(0).strip()

    # Remove prefixo de schema "HR". caso o modelo adicione por habito do Oracle
    texto_llm = re.sub(r'"?HR"?\.', "", texto_llm, flags=re.IGNORECASE)

    # Remove ponto-e-virgula final
    if texto_llm.endswith(";"):
        texto_llm = texto_llm[:-1].strip()

    return texto_llm


def executar_consulta_sql(sql_query: str) -> pd.DataFrame:
    """Executa consultas de leitura no banco SQLite local."""
    query_limpa = limpar_query_sql(sql_query)

    # Guardrail de seguranca: bloqueia comandos destrutivos (DML/DDL)
    comandos_proibidos = r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE|REPLACE|PRAGMA)\b"
    if re.search(comandos_proibidos, query_limpa, re.IGNORECASE):
        raise ValueError(
            "Guardrail de seguranca: Apenas consultas de leitura (SELECT) sao permitidas pelo Select AI."
        )

    if not query_limpa.upper().startswith(("SELECT", "WITH")):
        raise ValueError(f"A instrucao gerada nao e um SELECT valido: {query_limpa}")

    conn = sqlite3.connect(f"{DB_PATH.as_uri()}?mode=ro", uri=True)
    try:
        df = pd.read_sql_query(query_limpa, conn)
        return df
    finally:
        conn.close()


def obter_resumo_banco() -> dict:
    """Retorna contagens rapidas das tabelas do schema HR para os cards da interface."""
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM EMPLOYEES")
        total_emp = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM DEPARTMENTS")
        total_dept = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM JOBS")
        total_jobs = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM JOB_HISTORY")
        total_hist = cur.fetchone()[0]
        return {
            "employees": total_emp,
            "departments": total_dept,
            "jobs": total_jobs,
            "job_history": total_hist,
        }
    finally:
        conn.close()
