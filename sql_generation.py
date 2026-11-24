from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


PROMPT_SQL = """Você é um especialista em SQL do recurso Select AI.
Sua tarefa é converter a pergunta do usuário em uma única consulta SQL válida para SQLite usando APENAS as tabelas e colunas declaradas no schema abaixo.

Schema do Banco de Dados (HR):
{schema}

Exemplos de referência:
- Pergunta: "Mostre quais funcionários mudaram de cargo pelo menos duas vezes"
  SQL: SELECT e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME FROM EMPLOYEES e JOIN (SELECT EMPLOYEE_ID, COUNT(DISTINCT JOB_ID) AS JOB_CHANGE_COUNT FROM JOB_HISTORY GROUP BY EMPLOYEE_ID HAVING COUNT(DISTINCT JOB_ID) >= 2) jh ON e.EMPLOYEE_ID = jh.EMPLOYEE_ID
- Pergunta: "Liste todos os funcionários e seus salários"
  SQL: SELECT e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME, e.JOB_ID, e.SALARY, d.DEPARTMENT_NAME FROM EMPLOYEES e LEFT JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID ORDER BY e.SALARY DESC
- Pergunta: "Qual a média salarial por departamento?"
  SQL: SELECT d.DEPARTMENT_NAME, ROUND(AVG(e.SALARY), 2) AS MEDIA_SALARIAL, COUNT(e.EMPLOYEE_ID) AS TOTAL_COLABORADORES FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID GROUP BY d.DEPARTMENT_NAME ORDER BY MEDIA_SALARIAL DESC
- Pergunta: "Quem são os funcionários do departamento de TI (IT)?"
  SQL: SELECT e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME, e.JOB_ID, e.SALARY FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID WHERE d.DEPARTMENT_NAME = 'IT' COLLATE NOCASE

Regras obrigatórias:
1. Use somente tabelas e colunas existentes no DDL. Não invente colunas; `EMPLOYEE_COUNT` é um alias calculado, não uma coluna de `EMPLOYEES`.
2. Preserve exatamente as colunas e aliases pedidos pelo usuário; não transforme os valores selecionados.
3. Use `COUNT(...)` com `GROUP BY` para totais por categoria. Agregações usadas como filtro devem ficar em `HAVING`, nunca em `WHERE`.
4. Para contar cargos diferentes no histórico, use `COUNT(DISTINCT JOB_ID)`, agrupado por funcionário.
5. Para maior/menor valor, preserve empates usando igualdade com `MAX`/`MIN`; não use `>` com `MAX` nem `<` com `MIN`.
6. Para filtrar texto sem diferenciar maiúsculas/minúsculas, use `coluna = 'valor' COLLATE NOCASE` no `WHERE`. Não aplique `UPPER` às colunas do resultado.
7. Para encontrar departamentos sem funcionários, use `DEPARTMENTS LEFT JOIN EMPLOYEES` e `HAVING COUNT(e.EMPLOYEE_ID) = 0`.
8. Não adicione filtros que não foram pedidos. Qualifique colunas com alias quando houver mais de uma tabela.
9. Retorne APENAS uma consulta `SELECT`/`WITH` compatível com SQLite, sem markdown, explicação ou ponto-e-vírgula no final.

Mais padrões SQL:
- Funcionários por cargo atual: SELECT e.JOB_ID, COUNT(e.EMPLOYEE_ID) AS EMPLOYEE_COUNT FROM EMPLOYEES e GROUP BY e.JOB_ID
- Média e total por departamento: SELECT d.DEPARTMENT_NAME, ROUND(AVG(e.SALARY), 2) AS AVG_SALARY, COUNT(e.EMPLOYEE_ID) AS EMPLOYEE_COUNT FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID GROUP BY d.DEPARTMENT_NAME
- Departamento com maior média, incluindo empates: WITH averages AS (SELECT d.DEPARTMENT_NAME, AVG(e.SALARY) AS AVG_SALARY FROM EMPLOYEES e JOIN DEPARTMENTS d ON d.DEPARTMENT_ID = e.DEPARTMENT_ID GROUP BY d.DEPARTMENT_NAME) SELECT DEPARTMENT_NAME, ROUND(AVG_SALARY, 2) AS AVG_SALARY FROM averages WHERE AVG_SALARY = (SELECT MAX(AVG_SALARY) FROM averages)

Pergunta do usuário: {question}

SQL:"""


def criar_chain_sql(llm):
    prompt_sql = ChatPromptTemplate.from_template(PROMPT_SQL)
    return prompt_sql | llm | StrOutputParser()
