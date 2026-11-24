# Contexto do Projeto: AgenteSelectAILocal (Text-to-SQL com Streamlit, LangChain LCEL, SQLite e Ollama na Docker)

## 1. Visão Geral
Este projeto é uma implementação **100% local e gratuita** inspirada no recurso **Select AI** do **Oracle AI Database 26ai**, construída para portfólio profissional no GitHub.
Ele permite consultar um banco de dados relacional com o schema clássico **HR da Oracle** (`EMPLOYEES`, `JOB_HISTORY`, `DEPARTMENTS`, `JOBS`) usando **linguagem natural em Português do Brasil (Text-to-SQL / NL2SQL)**.

## 2. Arquitetura e Stack Tecnológica
- **Interface Web (`app.py`):** Streamlit (`>=1.57`, atualmente `1.67.0`). Usa `st.segmented_control` para selecionar os 4 modos do Select AI, cards de métricas (`st.metric`), explorador de schema na barra lateral e chat interativo (`st.chat_message`, `st.chat_input`).
- **Orquestração de IA (`app.py`):** LangChain com **LCEL (`LangChain Expression Language`)** usando `ChatPromptTemplate | ChatOllama | StrOutputParser()`.
  - `chain_sql`: Converte a pergunta em Português + DDL do schema HR em uma query SQL compatível com SQLite/Oracle.
  - `chain_narrate`: Recebe a pergunta, a query SQL e os dados retornados pelo banco e gera uma explicação executiva em Português do Brasil.
  - `chain_chat`: Conversa livre sobre SQL, Banco de Dados, RH e Select AI.
- **Banco de Dados Local (`database.py`):** SQLite (`hr_oracle.db`) criado e populado automaticamente na inicialização (`inicializar_banco()`).
  - Contém *guardrails* de segurança (`executar_consulta_sql()`) que bloqueiam comandos DML/DDL (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`) e permitem apenas consultas `SELECT`/`WITH`.
- **LLM Local (`docker-compose.yml`):** Ollama rodando em container Docker na porta `11434` (`http://localhost:11434`) utilizando o modelo `qwen3.5:0.8b` com `reasoning=False` e `temperature=0`.

## 3. Os 4 Modos do Select AI
1. **`runsql`**: Gera o SQL, executa no banco SQLite `hr_oracle.db` e exibe o código SQL + tabela interativa (`st.dataframe`).
2. **`showsql`**: Gera e exibe apenas a query SQL correspondente à pergunta.
3. **`narrate`**: Gera o SQL, executa no banco e narra o resultado em Português do Brasil.
4. **`chat`**: Bate-papo livre com o LLM local.

## 4. Diretrizes de Código para o Copilot
- Manter o código limpo, didático e no mesmo padrão de `LangChain LCEL` (`prompt | llm | StrOutputParser()`).
- No Streamlit, não utilizar o parâmetro depreciado `use_container_width`; utilizar `width="stretch"` ou o comportamento padrão.
- Preservar os *guardrails* de segurança somente-leitura (`SELECT`) no `database.py`.
