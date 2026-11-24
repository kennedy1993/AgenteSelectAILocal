# Avaliação Text-to-SQL — Execução local

- Data/hora: 2026-11-24T13:20:10-04:00
- Modelo: `qwen3.5:0.8b`
- Endpoint Ollama: `http://localhost:11434`
- Casos aprovados: **7/15 (46.7%)**
- SQL executável: **7/15**.
- Tabelas requeridas mencionadas: **13/15**.
- Resultados equivalentes: **7/15** (ordem das linhas ignorada; números comparados com duas casas decimais e aliases alternativos explicitamente listados aceitos).
- Nomes de colunas exatos: **7/15**.
- Aprovação estrita exige SQL executável somente leitura, tabelas requeridas, nomes de colunas solicitados e resultado esperado.
- Escopo: uma execução com temperatura 0 sobre o conjunto fictício local; não é uma avaliação estatística nem uma certificação para produção.

| Caso | Resultado | Tempo (s) |
|---|---:|---:|
| `total_employees` | FAIL | 7.77 |
| `total_departments` | FAIL | 3.10 |
| `it_employees` | PASS | 5.20 |
| `highest_salary_ties` | PASS | 5.50 |
| `department_salary_averages` | FAIL | 3.28 |
| `multiple_historical_jobs` | FAIL | 5.10 |
| `hired_since_2021` | PASS | 4.47 |
| `overall_average_salary` | PASS | 4.38 |
| `job_history_row_count` | PASS | 2.98 |
| `employees_by_current_job` | PASS | 6.08 |
| `sales_employees` | PASS | 4.58 |
| `departments_with_multiple_employees` | FAIL | 3.14 |
| `department_with_highest_average` | FAIL | 3.32 |
| `lowest_salary_employee` | FAIL | 3.01 |
| `departments_without_employees` | FAIL | 3.79 |

## total_employees — FAIL

**Pergunta:** Quantos funcionários existem em EMPLOYEES? Retorne uma única coluna chamada TOTAL_EMPLOYEES.

**Esperado:** `[[8]]`
**Obtido:** `[]`

```sql
0
```

**Falhas:**
- SQL rejeitada ou inválida: A instrucao gerada nao e um SELECT valido: 0

## total_departments — FAIL

**Pergunta:** Quantos departamentos existem? Retorne uma única coluna chamada TOTAL_DEPARTMENTS.

**Esperado:** `[[6]]`
**Obtido:** `[]`

```sql
TOTAL_DEPARTMENTS
```

**Falhas:**
- SQL rejeitada ou inválida: A instrucao gerada nao e um SELECT valido: TOTAL_DEPARTMENTS

## it_employees — PASS

**Pergunta:** Liste EMPLOYEE_ID, FIRST_NAME e LAST_NAME dos funcionários do departamento de TI (IT).

**Esperado:** `[[103, "Alexander", "Hunold"], [104, "Bruce", "Ernst"]]`
**Obtido:** `[[103, "Alexander", "Hunold"], [104, "Bruce", "Ernst"]]`

```sql
SELECT e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME, d.DEPARTMENT_NAME
FROM EMPLOYEES e
JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID
WHERE d.DEPARTMENT_NAME = 'IT' COLLATE NOCASE
```

## highest_salary_ties — PASS

**Pergunta:** Quais funcionários recebem o maior salário? Retorne EMPLOYEE_ID, FIRST_NAME, LAST_NAME e SALARY, incluindo empates.

**Esperado:** `[[101, "Neena", "Yang", 17000], [102, "Lex", "De Haan", 17000]]`
**Obtido:** `[[101, "Neena", "Yang", 17000], [102, "Lex", "De Haan", 17000]]`

```sql
SELECT e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME, e.SALARY FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID WHERE e.SALARY = (SELECT MAX(e.SALARY) FROM EMPLOYEES e)
```

## department_salary_averages — FAIL

**Pergunta:** Para cada departamento, retorne DEPARTMENT_NAME, AVG_SALARY (média salarial arredondada para duas casas) e EMPLOYEE_COUNT.

**Esperado:** `[["Accounting", 12008, 1], ["Administration", 4400, 1], ["Executive", 17000, 2], ["IT", 7500, 2], ["Sales", 8600, 1], ["Shipping", 7900, 1]]`
**Obtido:** `[]`

```sql
DEPARTMENTS, EMPLOYEES, JOBS
```

**Falhas:**
- SQL rejeitada ou inválida: A instrucao gerada nao e um SELECT valido: DEPARTMENTS, EMPLOYEES, JOBS

## multiple_historical_jobs — FAIL

**Pergunta:** Liste EMPLOYEE_ID, FIRST_NAME e LAST_NAME dos funcionários com pelo menos dois JOB_ID diferentes em JOB_HISTORY.

**Esperado:** `[[101, "Neena", "Yang"], [176, "Jonathon", "Taylor"], [200, "Jennifer", "Whalen"]]`
**Obtido:** `[]`

```sql
SELECT DISTINCT e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME
FROM EMPLOYEES e
JOIN JOB_HISTORY jh ON e.EMPLOYEE_ID = jh.EMPLOYEE_ID
WHERE COUNT(DISTINCT jh.JOB_ID) >= 2
```

**Falhas:**
- SQL rejeitada ou inválida: Execution failed on sql 'SELECT DISTINCT e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME
FROM EMPLOYEES e
JOIN JOB_HISTORY jh ON e.EMPLOYEE_ID = jh.EMPLOYEE_ID
WHERE COUNT(DISTINCT jh.JOB_ID) >= 2': misuse of aggregate function COUNT()

## hired_since_2021 — PASS

**Pergunta:** Liste EMPLOYEE_ID, FIRST_NAME, LAST_NAME e HIRE_DATE dos funcionários contratados em ou após 2021-01-01.

**Esperado:** `[[102, "Lex", "De Haan", "2021-01-13"], [103, "Alexander", "Hunold", "2021-01-03"], [104, "Bruce", "Ernst", "2022-05-21"], [122, "Payam", "Kaufling", "2022-05-01"]]`
**Obtido:** `[[102, "Lex", "De Haan", "2021-01-13"], [103, "Alexander", "Hunold", "2021-01-03"], [104, "Bruce", "Ernst", "2022-05-21"], [122, "Payam", "Kaufling", "2022-05-01"]]`

```sql
SELECT e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME, e.HIRE_DATE FROM EMPLOYEES e WHERE e.HIRE_DATE >= '2021-01-01'
```

## overall_average_salary — PASS

**Pergunta:** Qual é a média salarial de todos os funcionários? Retorne uma coluna chamada AVG_SALARY, arredondada para duas casas.

**Esperado:** `[[10238.5]]`
**Obtido:** `[[10238.5]]`

```sql
SELECT ROUND(AVG(e.SALARY), 2) AS AVG_SALARY FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID
```

## job_history_row_count — PASS

**Pergunta:** Quantos registros existem em JOB_HISTORY? Retorne uma coluna chamada TOTAL_HISTORY_ROWS.

**Esperado:** `[[7]]`
**Obtido:** `[[7]]`

```sql
SELECT COUNT(*) AS TOTAL_HISTORY_ROWS FROM JOB_HISTORY
```

## employees_by_current_job — PASS

**Pergunta:** Para cada JOB_ID atualmente presente em EMPLOYEES, retorne JOB_ID e EMPLOYEE_COUNT, ordenados por JOB_ID.

**Esperado:** `[["AC_MGR", 1], ["AD_ASST", 1], ["AD_VP", 2], ["IT_PROG", 2], ["SA_REP", 1], ["ST_MAN", 1]]`
**Obtido:** `[["IT_PROG", 2], ["AD_VP", 2], ["ST_MAN", 1], ["SA_REP", 1], ["AD_ASST", 1], ["AC_MGR", 1]]`

```sql
SELECT DISTINCT j.JOB_ID, COUNT(e.EMPLOYEE_ID) AS EMPLOYEE_COUNT FROM JOBS j JOIN EMPLOYEES e ON e.JOB_ID = j.JOB_ID GROUP BY j.JOB_ID ORDER BY EMPLOYEE_COUNT DESC
```

## sales_employees — PASS

**Pergunta:** Liste EMPLOYEE_ID, FIRST_NAME e LAST_NAME dos funcionários do departamento Sales.

**Esperado:** `[[176, "Jonathon", "Taylor"]]`
**Obtido:** `[[176, "Jonathon", "Taylor"]]`

```sql
SELECT e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID WHERE d.DEPARTMENT_NAME = 'Sales'
```

## departments_with_multiple_employees — FAIL

**Pergunta:** Quais departamentos têm mais de um funcionário? Retorne DEPARTMENT_NAME e EMPLOYEE_COUNT.

**Esperado:** `[["Executive", 2], ["IT", 2]]`
**Obtido:** `[]`

```sql
DEPARTMENTS, EMPLOYEES
```

**Falhas:**
- SQL rejeitada ou inválida: A instrucao gerada nao e um SELECT valido: DEPARTMENTS, EMPLOYEES

## department_with_highest_average — FAIL

**Pergunta:** Qual departamento tem a maior média salarial? Retorne DEPARTMENT_NAME e AVG_SALARY; inclua todos em caso de empate.

**Esperado:** `[["Executive", 17000]]`
**Obtido:** `[]`

```sql
DEPARTMENTS, EMPLOYEES, JOBS
```

**Falhas:**
- SQL rejeitada ou inválida: A instrucao gerada nao e um SELECT valido: DEPARTMENTS, EMPLOYEES, JOBS

## lowest_salary_employee — FAIL

**Pergunta:** Quem recebe o menor salário? Retorne EMPLOYEE_ID, FIRST_NAME, LAST_NAME e SALARY, incluindo empates.

**Esperado:** `[[200, "Jennifer", "Whalen", 4400]]`
**Obtido:** `[]`

```sql
EMPLOYEES e DEPARTMENTS
```

**Falhas:**
- SQL rejeitada ou inválida: A instrucao gerada nao e um SELECT valido: EMPLOYEES e DEPARTMENTS

## departments_without_employees — FAIL

**Pergunta:** Quais departamentos não têm funcionários? Retorne DEPARTMENT_NAME.

**Esperado:** `[]`
**Obtido:** `[]`

```sql
DEPARTMENTS LEFT JOIN EMPLOYEES ON e.DEPARTMENT_ID = d.DEPARTMENT_ID HAVING COUNT(e.EMPLOYEE_ID) = 0
```

**Falhas:**
- SQL rejeitada ou inválida: A instrucao gerada nao e um SELECT valido: DEPARTMENTS LEFT JOIN EMPLOYEES ON e.DEPARTMENT_ID = d.DEPARTMENT_ID HAVING COUNT(e.EMPLOYEE_ID) = 0
