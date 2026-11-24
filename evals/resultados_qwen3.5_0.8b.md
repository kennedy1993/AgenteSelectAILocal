# Avaliação Text-to-SQL — Execução local

- Data/hora: 2026-11-24T12:58:34-04:00
- Modelo: `qwen3.5:0.8b`
- Endpoint Ollama: `http://localhost:11434`
- Casos aprovados: **8/15 (53.3%)**
- SQL executável: **13/15**.
- Tabelas requeridas mencionadas: **14/15**.
- Resultados equivalentes: **9/15** (ordem das linhas ignorada; números comparados com duas casas decimais e aliases alternativos explicitamente listados aceitos).
- Nomes de colunas exatos: **12/15**.
- Aprovação estrita exige SQL executável somente leitura, tabelas requeridas, nomes de colunas solicitados e resultado esperado.
- Escopo: uma execução com temperatura 0 sobre o conjunto fictício local; não é uma avaliação estatística nem uma certificação para produção.

| Caso | Resultado | Tempo (s) |
|---|---:|---:|
| `total_employees` | PASS | 3.76 |
| `total_departments` | PASS | 3.11 |
| `it_employees` | PASS | 4.24 |
| `highest_salary_ties` | FAIL | 5.35 |
| `department_salary_averages` | FAIL | 5.17 |
| `multiple_historical_jobs` | FAIL | 4.81 |
| `hired_since_2021` | PASS | 4.70 |
| `overall_average_salary` | PASS | 4.37 |
| `job_history_row_count` | PASS | 2.94 |
| `employees_by_current_job` | FAIL | 4.64 |
| `sales_employees` | FAIL | 4.23 |
| `departments_with_multiple_employees` | PASS | 5.08 |
| `department_with_highest_average` | FAIL | 7.28 |
| `lowest_salary_employee` | PASS | 5.72 |
| `departments_without_employees` | FAIL | 3.11 |

## total_employees — PASS

**Pergunta:** Quantos funcionários existem em EMPLOYEES? Retorne uma única coluna chamada TOTAL_EMPLOYEES.

**Esperado:** `[[8]]`
**Obtido:** `[[8]]`

```sql
SELECT COUNT(*) AS TOTAL_EMPLOYEES FROM EMPLOYEES
```

## total_departments — PASS

**Pergunta:** Quantos departamentos existem? Retorne uma única coluna chamada TOTAL_DEPARTMENTS.

**Esperado:** `[[6]]`
**Obtido:** `[[6]]`

```sql
SELECT COUNT(*) AS TOTAL_DEPARTMENTS FROM DEPARTMENTS
```

## it_employees — PASS

**Pergunta:** Liste EMPLOYEE_ID, FIRST_NAME e LAST_NAME dos funcionários do departamento de TI (IT).

**Esperado:** `[[103, "Alexander", "Hunold"], [104, "Bruce", "Ernst"]]`
**Obtido:** `[[103, "Alexander", "Hunold"], [104, "Bruce", "Ernst"]]`

```sql
SELECT e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID WHERE UPPER(d.DEPARTMENT_NAME) = 'IT'
```

## highest_salary_ties — FAIL

**Pergunta:** Quais funcionários recebem o maior salário? Retorne EMPLOYEE_ID, FIRST_NAME, LAST_NAME e SALARY, incluindo empates.

**Esperado:** `[[101, "Neena", "Yang", 17000], [102, "Lex", "De Haan", 17000]]`
**Obtido:** `[]`

```sql
SELECT e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME, e.SALARY FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID WHERE e.SALARY > (SELECT MAX(e2.SALARY) FROM EMPLOYEES e2)
```

**Falhas:**
- Resultado diferente do esperado. Esperado: [(101, 'Neena', 'Yang', 17000), (102, 'Lex', 'De Haan', 17000)]; obtido: []

## department_salary_averages — FAIL

**Pergunta:** Para cada departamento, retorne DEPARTMENT_NAME, AVG_SALARY (média salarial arredondada para duas casas) e EMPLOYEE_COUNT.

**Esperado:** `[["Accounting", 12008, 1], ["Administration", 4400, 1], ["Executive", 17000, 2], ["IT", 7500, 2], ["Sales", 8600, 1], ["Shipping", 7900, 1]]`
**Obtido:** `[["Executive", 17000, 2], ["Accounting", 12008, 1], ["Sales", 8600, 1], ["Shipping", 7900, 1], ["IT", 7500, 2], ["Administration", 4400, 1]]`

```sql
SELECT d.DEPARTMENT_NAME, ROUND(AVG(e.SALARY), 2) AS AVG_SALARIAL, COUNT(e.EMPLOYEE_ID) AS EMPLOYEE_COUNT FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID GROUP BY d.DEPARTMENT_NAME ORDER BY AVG_SALARIAL DESC
```

**Falhas:**
- Colunas esperadas ausentes no resultado: AVG_SALARY

## multiple_historical_jobs — FAIL

**Pergunta:** Liste EMPLOYEE_ID, FIRST_NAME e LAST_NAME dos funcionários com pelo menos dois JOB_ID diferentes em JOB_HISTORY.

**Esperado:** `[[101, "Neena", "Yang"], [176, "Jonathon", "Taylor"], [200, "Jennifer", "Whalen"]]`
**Obtido:** `[]`

```sql
SELECT e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME FROM EMPLOYEES e JOIN JOB_HISTORY jh ON e.EMPLOYEE_ID = jh.EMPLOYEE_ID WHERE jh.JOB_ID NOT IN (SELECT DISTINCT JOB_ID FROM JOB_HISTORY) GROUP BY e.EMPLOYEE_ID
```

**Falhas:**
- Resultado diferente do esperado. Esperado: [(101, 'Neena', 'Yang'), (176, 'Jonathon', 'Taylor'), (200, 'Jennifer', 'Whalen')]; obtido: []

## hired_since_2021 — PASS

**Pergunta:** Liste EMPLOYEE_ID, FIRST_NAME, LAST_NAME e HIRE_DATE dos funcionários contratados em ou após 2021-01-01.

**Esperado:** `[[102, "Lex", "De Haan", "2021-01-13"], [103, "Alexander", "Hunold", "2021-01-03"], [104, "Bruce", "Ernst", "2022-05-21"], [122, "Payam", "Kaufling", "2022-05-01"]]`
**Obtido:** `[[102, "Lex", "De Haan", "2021-01-13"], [103, "Alexander", "Hunold", "2021-01-03"], [104, "Bruce", "Ernst", "2022-05-21"], [122, "Payam", "Kaufling", "2022-05-01"]]`

```sql
SELECT e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME, e.HIRE_DATE FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID WHERE e.HIRE_DATE >= '2021-01-01'
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

## employees_by_current_job — FAIL

**Pergunta:** Para cada JOB_ID atualmente presente em EMPLOYEES, retorne JOB_ID e EMPLOYEE_COUNT, ordenados por JOB_ID.

**Esperado:** `[["AC_MGR", 1], ["AD_ASST", 1], ["AD_VP", 2], ["IT_PROG", 2], ["SA_REP", 1], ["ST_MAN", 1]]`
**Obtido:** `[]`

```sql
SELECT j.JOB_ID, e.EMPLOYEE_COUNT FROM JOBS j JOIN EMPLOYEES e ON e.JOB_ID = j.JOB_ID ORDER BY j.JOB_ID
```

**Falhas:**
- SQL rejeitada ou inválida: Execution failed on sql 'SELECT j.JOB_ID, e.EMPLOYEE_COUNT FROM JOBS j JOIN EMPLOYEES e ON e.JOB_ID = j.JOB_ID ORDER BY j.JOB_ID': no such column: e.EMPLOYEE_COUNT

## sales_employees — FAIL

**Pergunta:** Liste EMPLOYEE_ID, FIRST_NAME e LAST_NAME dos funcionários do departamento Sales.

**Esperado:** `[[176, "Jonathon", "Taylor"]]`
**Obtido:** `[]`

```sql
SELECT e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID WHERE UPPER(d.DEPARTMENT_NAME) = 'Sales'
```

**Falhas:**
- Resultado diferente do esperado. Esperado: [(176, 'Jonathon', 'Taylor')]; obtido: []

## departments_with_multiple_employees — PASS

**Pergunta:** Quais departamentos têm mais de um funcionário? Retorne DEPARTMENT_NAME e EMPLOYEE_COUNT.

**Esperado:** `[["Executive", 2], ["IT", 2]]`
**Obtido:** `[["Executive", 2], ["IT", 2]]`

```sql
SELECT DISTINCT d.DEPARTMENT_NAME, COUNT(e.EMPLOYEE_ID) AS EMPLOYEE_COUNT FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID GROUP BY d.DEPARTMENT_NAME HAVING COUNT(e.EMPLOYEE_ID) > 1
```

## department_with_highest_average — FAIL

**Pergunta:** Qual departamento tem a maior média salarial? Retorne DEPARTMENT_NAME e AVG_SALARY; inclua todos em caso de empate.

**Esperado:** `[["Executive", 17000]]`
**Obtido:** `[]`

```sql
SELECT d.DEPARTMENT_NAME, ROUND(AVG(e.SALARY), 2) AS AVG_SALARIAL
FROM EMPLOYEES e
JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID
GROUP BY d.DEPARTMENT_NAME
HAVING COUNT(*) > (SELECT COUNT(*) FROM EMPLOYEES WHERE SALARY < AVG(e.SALARY) FROM EMPLOYEES e JOIN DEPARTMENTS d2 ON e.DEPARTMENT_ID = d2.DEPARTMENT_ID GROUP BY d2.DEPARTMENT_NAME)
```

**Falhas:**
- SQL rejeitada ou inválida: Execution failed on sql 'SELECT d.DEPARTMENT_NAME, ROUND(AVG(e.SALARY), 2) AS AVG_SALARIAL
FROM EMPLOYEES e
JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID
GROUP BY d.DEPARTMENT_NAME
HAVING COUNT(*) > (SELECT COUNT(*) FROM EMPLOYEES WHERE SALARY < AVG(e.SALARY) FROM EMPLOYEES e JOIN DEPARTMENTS d2 ON e.DEPARTMENT_ID = d2.DEPARTMENT_ID GROUP BY d2.DEPARTMENT_NAME)': near "FROM": syntax error

## lowest_salary_employee — PASS

**Pergunta:** Quem recebe o menor salário? Retorne EMPLOYEE_ID, FIRST_NAME, LAST_NAME e SALARY, incluindo empates.

**Esperado:** `[[200, "Jennifer", "Whalen", 4400]]`
**Obtido:** `[[200, "Jennifer", "Whalen", 4400]]`

```sql
SELECT e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME, e.SALARY FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID WHERE e.SALARY = (SELECT MIN(e2.SALARY) FROM EMPLOYEES e2)
```

## departments_without_employees — FAIL

**Pergunta:** Quais departamentos não têm funcionários? Retorne DEPARTMENT_NAME.

**Esperado:** `[]`
**Obtido:** `[["Administration"], ["Shipping"], ["IT"], ["Sales"], ["Executive"], ["Accounting"]]`

```sql
SELECT DISTINCT d.DEPARTMENT_NAME FROM DEPARTMENTS d
```

**Falhas:**
- Tabelas esperadas ausentes na SQL: EMPLOYEES
- Resultado diferente do esperado. Esperado: []; obtido: [('Administration',), ('Shipping',), ('IT',), ('Sales',), ('Executive',), ('Accounting',)]
