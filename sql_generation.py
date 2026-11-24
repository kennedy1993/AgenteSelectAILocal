from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


PROMPT_SQL = """Você é um especialista em SQL do recurso Select AI.
Sua tarefa é converter a pergunta do usuário em uma única consulta SQL compatível com SQLite/Oracle usando APENAS as tabelas do schema abaixo.

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
  SQL: SELECT e.EMPLOYEE_ID, e.FIRST_NAME, e.LAST_NAME, e.JOB_ID, e.SALARY FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID WHERE UPPER(d.DEPARTMENT_NAME) = 'IT'

Regras obrigatórias:
1. Retorne APENAS o código SQL puro, sem blocos markdown (sem ```sql), sem explicações e sem ponto-e-vírgula no final.
2. Qualifique sempre as colunas com o alias da tabela (ex: e.EMPLOYEE_ID, d.DEPARTMENT_NAME) para evitar ambiguidade.

Pergunta do usuário: {question}

SQL:"""


def criar_chain_sql(llm):
    prompt_sql = ChatPromptTemplate.from_template(PROMPT_SQL)
    return prompt_sql | llm | StrOutputParser()
