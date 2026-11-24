# Avaliação Text-to-SQL — Execução local

- Data/hora: 2026-11-24T13:48:18-04:00
- Modelo: `qwen3.5:2b`
- Endpoint Ollama: `http://localhost:11434`
- Casos aprovados: **13/15 (86.7%)**
- SQL executável: **15/15**.
- Tabelas requeridas mencionadas: **15/15**.
- Resultados equivalentes: **13/15** (ordem das linhas ignorada; números comparados com duas casas decimais e aliases alternativos explicitamente listados aceitos).
- Nomes de colunas exatos: **15/15**.
- Aprovação estrita exige SQL executável somente leitura, tabelas requeridas, nomes de colunas solicitados e resultado esperado.
- Escopo: uma execução com temperatura 0 sobre o conjunto fictício local; não é uma avaliação estatística nem uma certificação para produção.

| Caso | Resultado | Tempo (s) |
|---|---:|---:|
| `total_employees` | PASS | 186.86 |
| `total_departments` | PASS | 6.90 |
| `it_employees` | PASS | 9.38 |
| `highest_salary_ties` | FAIL | 14.95 |
| `department_salary_averages` | PASS | 10.64 |
| `multiple_historical_jobs` | PASS | 10.33 |
| `hired_since_2021` | PASS | 11.23 |
| `overall_average_salary` | FAIL | 9.01 |
| `job_history_row_count` | PASS | 6.34 |
| `employees_by_current_job` | PASS | 9.08 |
| `sales_employees` | PASS | 9.89 |
| `departments_with_multiple_employees` | PASS | 11.09 |
| `department_with_highest_average` | PASS | 14.14 |
| `lowest_salary_employee` | PASS | 14.41 |
| `departments_without_employees` | PASS | 11.23 |

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
SELECT COUNT(DISTINCT d.DEPARTMENT_ID) AS TOTAL_DEPARTMENTS FROM DEPARTMENTS d
```

## it_employees — PASS

**Pergunta:** Liste EMPLOYEE_ID, FIRST_NAME e LAST_NAME dos funcionários do departamento de TI (IT).

**Esperado:** `[[103, "Alexander", "Hunold"], [104, "Bruce", "Ernst"]]`
**Obtido:** `[[103, "Alexander", "Hunold"], [104, "Bruce", "Ernst"]]`

```sql
SELECT e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID WHERE d.DEPARTMENT_NAME = 'IT' COLLATE NOCASE
```

## highest_salary_ties — FAIL

**Pergunta:** Quais funcionários recebem o maior salário? Retorne EMPLOYEE_ID, FIRST_NAME, LAST_NAME e SALARY, incluindo empates.

**Esperado:** `[[101, "Neena", "Yang", 17000], [102, "Lex", "De Haan", 17000]]`
**Obtido:** `[[101, "Neena", "Yang", 17000], [102, "Lex", "De Haan", 17000], [103, "Alexander", "Hunold", 9000], [104, "Bruce", "Ernst", 6000], [122, "Payam", "Kaufling", 7900], [176, "Jonathon", "Taylor", 8600], [200, "Jennifer", "Whalen", 4400], [205, "Shelley", "Higgins", 12008]]`

```sql
WITH salaries AS (
    SELECT e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME, e.SALARY
    FROM EMPLOYEES e
)
SELECT e1.EMPLOYEE_ID, e1.FIRST_NAME, e1.LAST_NAME, e1.SALARY
FROM salaries e1
JOIN (
    SELECT EMPLOYEE_ID, MAX(SALARY) AS MAX_SALARY
    FROM EMPLOYEES
    GROUP BY EMPLOYEE_ID
) e2 ON e1.EMPLOYEE_ID = e2.EMPLOYEE_ID AND e1.SALARY = e2.MAX_SALARY
```

**Falhas:**
- Resultado diferente do esperado. Esperado: [(101, 'Neena', 'Yang', 17000), (102, 'Lex', 'De Haan', 17000)]; obtido: [(101, 'Neena', 'Yang', 17000), (102, 'Lex', 'De Haan', 17000), (103, 'Alexander', 'Hunold', 9000), (104, 'Bruce', 'Ernst', 6000), (122, 'Payam', 'Kaufling', 7900), (176, 'Jonathon', 'Taylor', 8600), (200, 'Jennifer', 'Whalen', 4400), (205, 'Shelley', 'Higgins', 12008)]

## department_salary_averages — PASS

**Pergunta:** Para cada departamento, retorne DEPARTMENT_NAME, AVG_SALARY (média salarial arredondada para duas casas) e EMPLOYEE_COUNT.

**Esperado:** `[["Accounting", 12008, 1], ["Administration", 4400, 1], ["Executive", 17000, 2], ["IT", 7500, 2], ["Sales", 8600, 1], ["Shipping", 7900, 1]]`
**Obtido:** `[["Executive", 17000, 2], ["Accounting", 12008, 1], ["Sales", 8600, 1], ["Shipping", 7900, 1], ["IT", 7500, 2], ["Administration", 4400, 1]]`

```sql
SELECT d.DEPARTMENT_NAME, ROUND(AVG(e.SALARY), 2) AS AVG_SALARY, COUNT(e.EMPLOYEE_ID) AS EMPLOYEE_COUNT FROM DEPARTMENTS d LEFT JOIN EMPLOYEES e ON d.DEPARTMENT_ID = e.DEPARTMENT_ID GROUP BY d.DEPARTMENT_NAME ORDER BY AVG_SALARY DESC
```

## multiple_historical_jobs — PASS

**Pergunta:** Liste EMPLOYEE_ID, FIRST_NAME e LAST_NAME dos funcionários com pelo menos dois JOB_ID diferentes em JOB_HISTORY.

**Esperado:** `[[101, "Neena", "Yang"], [176, "Jonathon", "Taylor"], [200, "Jennifer", "Whalen"]]`
**Obtido:** `[[101, "Neena", "Yang"], [176, "Jonathon", "Taylor"], [200, "Jennifer", "Whalen"]]`

```sql
SELECT e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME FROM EMPLOYEES e JOIN (SELECT EMPLOYEE_ID, COUNT(DISTINCT JOB_ID) AS JOB_CHANGE_COUNT FROM JOB_HISTORY GROUP BY EMPLOYEE_ID HAVING COUNT(DISTINCT JOB_ID) >= 2) jh ON e.EMPLOYEE_ID = jh.EMPLOYEE_ID
```

## hired_since_2021 — PASS

**Pergunta:** Liste EMPLOYEE_ID, FIRST_NAME, LAST_NAME e HIRE_DATE dos funcionários contratados em ou após 2021-01-01.

**Esperado:** `[[102, "Lex", "De Haan", "2021-01-13"], [103, "Alexander", "Hunold", "2021-01-03"], [104, "Bruce", "Ernst", "2022-05-21"], [122, "Payam", "Kaufling", "2022-05-01"]]`
**Obtido:** `[[102, "Lex", "De Haan", "2021-01-13"], [103, "Alexander", "Hunold", "2021-01-03"], [104, "Bruce", "Ernst", "2022-05-21"], [122, "Payam", "Kaufling", "2022-05-01"]]`

```sql
SELECT e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME, e.HIRE_DATE FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID WHERE e.HIRE_DATE >= '2021-01-01' COLLATE NOCASE
```

## overall_average_salary — FAIL

**Pergunta:** Qual é a média salarial de todos os funcionários? Retorne uma coluna chamada AVG_SALARY, arredondada para duas casas.

**Esperado:** `[[10238.5]]`
**Obtido:** `[[12008], [4400], [17000], [7500], [8600], [7900]]`

```sql
SELECT ROUND(AVG(e.SALARY), 2) AS AVG_SALARY FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID GROUP BY d.DEPARTMENT_NAME
```

**Falhas:**
- Resultado diferente do esperado. Esperado: [(10238.5,)]; obtido: [(12008,), (4400,), (17000,), (7500,), (8600,), (7900,)]

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
**Obtido:** `[["AC_MGR", 1], ["AD_ASST", 1], ["AD_VP", 2], ["IT_PROG", 2], ["SA_REP", 1], ["ST_MAN", 1]]`

```sql
SELECT e.JOB_ID, COUNT(e.EMPLOYEE_ID) AS EMPLOYEE_COUNT FROM EMPLOYEES e JOIN JOBS j ON e.JOB_ID = j.JOB_ID GROUP BY e.JOB_ID ORDER BY e.JOB_ID
```

## sales_employees — PASS

**Pergunta:** Liste EMPLOYEE_ID, FIRST_NAME e LAST_NAME dos funcionários do departamento Sales.

**Esperado:** `[[176, "Jonathon", "Taylor"]]`
**Obtido:** `[[176, "Jonathon", "Taylor"]]`

```sql
SELECT e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID WHERE d.DEPARTMENT_NAME = 'Sales' COLLATE NOCASE
```

## departments_with_multiple_employees — PASS

**Pergunta:** Quais departamentos têm mais de um funcionário? Retorne DEPARTMENT_NAME e EMPLOYEE_COUNT.

**Esperado:** `[["Executive", 2], ["IT", 2]]`
**Obtido:** `[["Executive", 2], ["IT", 2]]`

```sql
SELECT d.DEPARTMENT_NAME, COUNT(e.EMPLOYEE_ID) AS EMPLOYEE_COUNT FROM DEPARTMENTS d LEFT JOIN EMPLOYEES e ON d.DEPARTMENT_ID = e.DEPARTMENT_ID GROUP BY d.DEPARTMENT_NAME HAVING COUNT(e.EMPLOYEE_ID) > 1
```

## department_with_highest_average — PASS

**Pergunta:** Qual departamento tem a maior média salarial? Retorne DEPARTMENT_NAME e AVG_SALARY; inclua todos em caso de empate.

**Esperado:** `[["Executive", 17000]]`
**Obtido:** `[["Executive", 17000]]`

```sql
WITH department_averages AS (
    SELECT d.DEPARTMENT_NAME, ROUND(AVG(e.SALARY), 2) AS AVG_SALARY
    FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID
    GROUP BY d.DEPARTMENT_NAME
)
SELECT DEPARTMENT_NAME, AVG_SALARY
FROM department_averages
WHERE AVG_SALARY = (SELECT MAX(AVG_SALARY) FROM department_averages)
```

## lowest_salary_employee — PASS

**Pergunta:** Quem recebe o menor salário? Retorne EMPLOYEE_ID, FIRST_NAME, LAST_NAME e SALARY, incluindo empates.

**Esperado:** `[[200, "Jennifer", "Whalen", 4400]]`
**Obtido:** `[[200, "Jennifer", "Whalen", 4400]]`

```sql
SELECT e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME, e.SALARY FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID WHERE e.SALARY = (SELECT MIN(SALARY) FROM EMPLOYEES e2 JOIN DEPARTMENTS d2 ON e2.DEPARTMENT_ID = d2.DEPARTMENT_ID) ORDER BY e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME, e.SALARY
```

## departments_without_employees — PASS

**Pergunta:** Quais departamentos não têm funcionários? Retorne DEPARTMENT_NAME.

**Esperado:** `[]`
**Obtido:** `[]`

```sql
SELECT d.DEPARTMENT_NAME FROM DEPARTMENTS d LEFT JOIN EMPLOYEES e ON d.DEPARTMENT_ID = e.DEPARTMENT_ID GROUP BY d.DEPARTMENT_NAME HAVING COUNT(e.EMPLOYEE_ID) = 0
```
