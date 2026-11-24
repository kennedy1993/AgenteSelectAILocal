import argparse
import json
import numbers
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import database
from sql_generation import criar_chain_sql

MATRIX_PATH = Path(__file__).with_name("matriz_avaliacao.json")


def normalizar_valor(value):
    if hasattr(value, "item"):
        value = value.item()
    if value is None or pd.isna(value):
        return None
    if isinstance(value, numbers.Integral):
        return int(value)
    if isinstance(value, numbers.Real):
        value = round(float(value), 2)
        return int(value) if value.is_integer() else value
    return value


def validar_resultado(case, sql, dataframe):
    sql_upper = sql.upper()

    missing_tables = [
        table
        for table in case["required_tables"]
        if not re.search(rf"\b{re.escape(table)}\b", sql_upper)
    ]

    available_columns = {str(column).upper(): column for column in dataframe.columns}
    exact_missing_columns = [
        column
        for column in case["expected_columns"]
        if column.upper() not in available_columns
    ]
    aliases = case.get("column_aliases", {})
    resolved_columns = []
    unresolved_columns = []
    for column in case["expected_columns"]:
        candidates = [column, *aliases.get(column, [])]
        resolved = next(
            (
                available_columns[name.upper()]
                for name in candidates
                if name.upper() in available_columns
            ),
            None,
        )
        if resolved is None:
            unresolved_columns.append(column)
        else:
            resolved_columns.append(resolved)

    actual_rows = []
    rows_match = False
    if not unresolved_columns:
        actual_rows = [
            tuple(normalizar_valor(row[column]) for column in resolved_columns)
            for _, row in dataframe.iterrows()
        ]
        expected_rows = [
            tuple(normalizar_valor(value) for value in row)
            for row in case["expected_rows"]
        ]
        rows_match = Counter(actual_rows) == Counter(expected_rows)

    failures = []
    if missing_tables:
        failures.append(f"Tabelas esperadas ausentes na SQL: {', '.join(missing_tables)}")
    if exact_missing_columns:
        failures.append(
            f"Colunas esperadas ausentes no resultado: {', '.join(exact_missing_columns)}"
        )
    if unresolved_columns:
        failures.append(
            f"Colunas sem alias equivalente no resultado: {', '.join(unresolved_columns)}"
        )
    elif not rows_match:
        failures.append(
            f"Resultado diferente do esperado. Esperado: {expected_rows}; "
            f"obtido: {actual_rows}"
        )

    return {
        "failures": failures,
        "tables_match": not missing_tables,
        "columns_exact": not exact_missing_columns,
        "rows_match": rows_match,
        "actual_rows": [list(row) for row in actual_rows],
    }


def executar_caso(case, chain_sql, schema):
    started_at = time.perf_counter()
    raw_sql = chain_sql.invoke({"schema": schema, "question": case["question"]})
    sql = database.limpar_query_sql(raw_sql)
    result = {
        "id": case["id"],
        "question": case["question"],
        "expected_columns": case["expected_columns"],
        "expected_rows": case["expected_rows"],
        "sql": sql,
        "elapsed_seconds": 0.0,
        "sql_executed": False,
        "tables_match": False,
        "columns_exact": False,
        "rows_match": False,
        "actual_rows": [],
        "failures": [],
    }

    try:
        dataframe = database.executar_consulta_sql(sql)
        result["sql_executed"] = True
        result.update(validar_resultado(case, sql, dataframe))
    except (ValueError, pd.errors.DatabaseError) as error:
        result["failures"] = [f"SQL rejeitada ou inválida: {error}"]
        result["tables_match"] = all(
            re.search(rf"\b{re.escape(table)}\b", sql, re.IGNORECASE)
            for table in case["required_tables"]
        )

    result["elapsed_seconds"] = round(time.perf_counter() - started_at, 2)
    result["passed"] = result["sql_executed"] and not result["failures"]
    return result


def gerar_relatorio(results, model, ollama_url):
    passed = sum(result["passed"] for result in results)
    rate = passed / len(results) * 100 if results else 0
    executed = sum(result["sql_executed"] for result in results)
    tables_match = sum(result["tables_match"] for result in results)
    exact_columns = sum(result["columns_exact"] for result in results)
    rows_match = sum(result["rows_match"] for result in results)
    lines = [
        "# Avaliação Text-to-SQL — Execução local",
        "",
        f"- Data/hora: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"- Modelo: `{model}`",
        f"- Endpoint Ollama: `{ollama_url}`",
        f"- Casos aprovados: **{passed}/{len(results)} ({rate:.1f}%)**",
        f"- SQL executável: **{executed}/{len(results)}**.",
        f"- Tabelas requeridas mencionadas: **{tables_match}/{len(results)}**.",
        f"- Resultados equivalentes: **{rows_match}/{len(results)}** (ordem das linhas ignorada; números comparados com duas casas decimais e aliases alternativos explicitamente listados aceitos).",
        f"- Nomes de colunas exatos: **{exact_columns}/{len(results)}**.",
        "- Aprovação estrita exige SQL executável somente leitura, tabelas requeridas, "
        "nomes de colunas solicitados e resultado esperado.",
        "- Escopo: uma execução com temperatura 0 sobre o conjunto fictício local; "
        "não é uma avaliação estatística nem uma certificação para produção.",
        "",
        "| Caso | Resultado | Tempo (s) |",
        "|---|---:|---:|",
    ]
    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        lines.append(
            f"| `{result['id']}` | {status} | {result['elapsed_seconds']:.2f} |"
        )

    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        lines.extend(
            [
                "",
                f"## {result['id']} — {status}",
                "",
                f"**Pergunta:** {result['question']}",
                "",
                f"**Esperado:** `{json.dumps(result['expected_rows'], ensure_ascii=False)}`",
                f"**Obtido:** `{json.dumps(result['actual_rows'], ensure_ascii=False)}`",
                "",
                "```sql",
                result["sql"] or "(resposta SQL vazia)",
                "```",
            ]
        )
        if result["failures"]:
            lines.extend(["", "**Falhas:**"])
            lines.extend(f"- {failure}" for failure in result["failures"])

    return "\n".join(lines) + "\n"


def main():
    load_dotenv(PROJECT_ROOT / ".env")
    parser = argparse.ArgumentParser(
        description="Executa a matriz Text-to-SQL contra o modelo Ollama local."
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OLLAMA_MODEL", "qwen3.5:0.8b"),
        help="Nome do modelo Ollama.",
    )
    parser.add_argument(
        "--ollama-url",
        default=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        help="URL base da API Ollama.",
    )
    args = parser.parse_args()

    with MATRIX_PATH.open(encoding="utf-8") as matrix_file:
        matrix = json.load(matrix_file)

    database.inicializar_banco()
    schema = database.obter_schema_ddl()
    llm = ChatOllama(
        model=args.model,
        base_url=args.ollama_url,
        reasoning=False,
        temperature=0,
    )
    chain_sql = criar_chain_sql(llm)
    results = []
    for index, case in enumerate(matrix, start=1):
        print(f"[{index}/{len(matrix)}] {case['id']}: {case['question']}", flush=True)
        result = executar_caso(case, chain_sql, schema)
        results.append(result)
        status = "PASS" if result["passed"] else "FAIL"
        print(f"  {status} ({result['elapsed_seconds']:.2f}s)", flush=True)

    report_path = Path(__file__).with_name("resultados_qwen3.5_0.8b.md")
    report_path.write_text(
        gerar_relatorio(results, args.model, args.ollama_url), encoding="utf-8"
    )
    print(f"\nAprovados: {sum(item['passed'] for item in results)}/{len(results)}")
    print(f"Relatório: {report_path}")
    if not all(result["passed"] for result in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
