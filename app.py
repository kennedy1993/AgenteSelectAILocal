"""
Assistente Select AI Local — Text-to-SQL (Schema HR Oracle)
- Streamlit (interface conversacional e visualizacao de dados)
- LangChain com LCEL (orquestracao de prompts e chains)
- SQLite Local (banco relacional com schema HR: EMPLOYEES, JOB_HISTORY, DEPARTMENTS, JOBS)
- Ollama na Docker (LLM local qwen3.5:0.8b sem custo de API)
"""

import os
import streamlit as st
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from sql_generation import criar_chain_sql
from database import (
    inicializar_banco,
    obter_schema_ddl,
    limpar_query_sql,
    executar_consulta_sql,
    obter_resumo_banco,
)

load_dotenv()

st.set_page_config(
    page_title="Select AI Local — Text-to-SQL (Schema HR)",
    page_icon=":material/database:",
    layout="wide",
)

# 1. Inicializa o banco SQLite local com o schema HR da Oracle
inicializar_banco()


# 2. Logica do Agente de IA com LangChain (LCEL) — seguindo a mesma arquitetura do projeto RAG
@st.cache_resource
def criar_chains_select_ai(modelo_ollama: str, ollama_url: str):
    llm = ChatOllama(
        model=modelo_ollama,
        base_url=ollama_url,
        reasoning=False,
        temperature=0,
    )

    # Chain 2: Narrativa em linguagem natural (usada na etapa 2 do modo narrate)
    prompt_narrate = ChatPromptTemplate.from_template(
        """Você é um assistente analítico de RH do Select AI.
Com base na pergunta do usuário e nos dados reais retornados pelo banco de dados abaixo, explique o resultado em Português do Brasil de forma clara, direta e executiva.
Use APENAS os dados fornecidos no resultado da consulta.

Pergunta do usuário: {question}
Consulta SQL executada: {sql}
Resultado retornado pelo banco:
{resultado}

Resposta narrada em Português do Brasil:"""
    )

    # Chain 3: Conversa livre sobre Banco de Dados, SQL e Select AI (usada no modo chat)
    prompt_chat = ChatPromptTemplate.from_template(
        """Você é um assistente especialista em Banco de Dados, SQL, Recursos Humanos e na funcionalidade Select AI (Text-to-SQL).
Responda à pergunta do usuário em Português do Brasil, de forma clara, didática e objetiva.

Neste aplicativo local, os modos funcionam assim:
- runsql: gera SQL, executa no SQLite local e exibe os resultados.
- showsql: gera e exibe o SQL correspondente à pergunta, sem executar a consulta.
- narrate: gera e executa SQL no SQLite local e explica os resultados retornados.
- chat: conversa livre; não executa consultas nem acessa dados além do schema abaixo.
Não confunda showsql com a exibição do schema. Este projeto é uma demonstração local inspirada no Select AI e não se conecta ao Oracle Database.

Contexto das tabelas disponíveis no projeto:
{schema}

Pergunta: {question}

Resposta:"""
    )

    chain_sql = criar_chain_sql(llm)
    chain_narrate = prompt_narrate | llm | StrOutputParser()
    chain_chat = prompt_chat | llm | StrOutputParser()

    return chain_sql, chain_narrate, chain_chat


def processar_pergunta_select_ai(pergunta: str, modo: str, modelo: str, ollama_url: str) -> dict:
    """Executa o pipeline correspondente ao modo do Select AI escolhido (runsql, showsql, narrate, chat)."""
    schema_ddl = obter_schema_ddl()
    chain_sql, chain_narrate, chain_chat = criar_chains_select_ai(modelo, ollama_url)
    comando_oracle = f"SELECT AI {modo} {pergunta};"

    if modo == "chat":
        texto_resposta = chain_chat.invoke({"schema": schema_ddl, "question": pergunta})
        return {
            "role": "assistant",
            "modo": modo,
            "comando_oracle": comando_oracle,
            "content": texto_resposta,
            "sql": None,
            "dados": None,
        }

    # Para showsql, runsql e narrate: primeiro gera a query SQL via LCEL
    sql_bruto = chain_sql.invoke({"schema": schema_ddl, "question": pergunta})
    sql_limpo = limpar_query_sql(sql_bruto)

    if modo == "showsql":
        return {
            "role": "assistant",
            "modo": modo,
            "comando_oracle": comando_oracle,
            "content": "Consulta SQL gerada pelo modelo local:",
            "sql": sql_limpo,
            "dados": None,
        }

    # Para runsql e narrate: executa a query SQL gerada no banco SQLite local
    df_resultado = executar_consulta_sql(sql_limpo)
    registros = df_resultado.to_dict(orient="records")

    if modo == "runsql":
        return {
            "role": "assistant",
            "modo": modo,
            "comando_oracle": comando_oracle,
            "content": f"Consulta executada com sucesso ({len(registros)} registro(s) encontrado(s)):",
            "sql": sql_limpo,
            "dados": registros,
        }

    # Modo narrate: executa o SQL e envia os dados para a chain_narrate explicar em portugues
    resumo_tabela = (
        df_resultado.to_string(index=False)
        if not df_resultado.empty
        else "Nenhum registro encontrado."
    )
    narrativa = chain_narrate.invoke(
        {"question": pergunta, "sql": sql_limpo, "resultado": resumo_tabela}
    )
    return {
        "role": "assistant",
        "modo": modo,
        "comando_oracle": comando_oracle,
        "content": narrativa,
        "sql": sql_limpo,
        "dados": registros,
    }


# 3. Barra Lateral: Configuracao do Ollama na Docker e Explorador do Schema HR
with st.sidebar:
    st.header(":material/settings: Configuração Select AI")
    ollama_url = st.text_input(
        "Endpoint do Ollama (Docker)",
        value=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )
    modelo_ollama = st.text_input(
        "Modelo LLM no Ollama",
        value=os.getenv("OLLAMA_MODEL", "qwen3.5:0.8b"),
    )

    if st.button(":material/delete_sweep: Limpar histórico do chat", width="stretch"):
        st.session_state["messages"] = []
        st.rerun()

    st.divider()
    st.subheader(":material/schema: Explorador do schema HR")
    st.caption(
        "Tabelas locais em SQLite baseadas no schema oficial `HR` do Oracle Database 26ai:"
    )

    tabela_preview = st.selectbox(
        "Visualizar dados da tabela",
        options=["EMPLOYEES", "JOB_HISTORY", "DEPARTMENTS", "JOBS"],
    )
    df_preview = executar_consulta_sql(f"SELECT * FROM {tabela_preview}")
    st.dataframe(df_preview, hide_index=True)

    with st.expander(":material/code_blocks: Ver DDL (CREATE TABLE)"):
        st.code(obter_schema_ddl(), language="sql")


# 4. Cabecalho Principal e Cards de Resumo do Banco HR
st.title(":material/database: Assistente Select AI Local — Schema HR")
st.caption(
    "Consulte bancos de dados relacionais usando linguagem natural em Português (Text-to-SQL) "
    "com **Streamlit**, **LangChain (LCEL)**, **SQLite** e **Ollama na Docker**."
)

resumo = obter_resumo_banco()
col1, col2, col3, col4 = st.columns(4)
with col1:
    with st.container(border=True):
        st.metric("Colaboradores (EMPLOYEES)", resumo["employees"])
with col2:
    with st.container(border=True):
        st.metric("Departamentos (DEPARTMENTS)", resumo["departments"])
with col3:
    with st.container(border=True):
        st.metric("Cargos (JOBS)", resumo["jobs"])
with col4:
    with st.container(border=True):
        st.metric("Histórico (JOB_HISTORY)", resumo["job_history"])

# 5. Seletor dos 4 Modos do Select AI (inspirado no Oracle Database 26ai)
OPCOES_MODO = {
    "runsql": ":material/table_view: runsql (Executar SQL)",
    "showsql": ":material/code: showsql (Mostrar SQL)",
    "narrate": ":material/record_voice_over: narrate (Narrar resultado)",
    "chat": ":material/chat: chat (Conversa livre)",
}

modo_selecionado = st.segmented_control(
    "Modo de operação do Select AI",
    options=list(OPCOES_MODO.keys()),
    format_func=lambda m: OPCOES_MODO[m],
    default="runsql",
    key="modo_select_ai",
)
if not modo_selecionado:
    modo_selecionado = "runsql"

# 6. Botoes de Perguntas Rapidas para Demonstracao / Recrutadores
st.caption("Sugestões rápidas para testar (clique para executar):")
perguntas_exemplo = [
    "Mostre quais funcionários mudaram de cargo pelo menos duas vezes",
    "Liste todos os funcionários e seus salários",
    "Qual a média salarial por departamento?",
    "Quem são os funcionários do departamento de TI (IT)?",
]

pergunta_clicada = None
cols_exemplos = st.columns(len(perguntas_exemplo))
for idx, texto_exemplo in enumerate(perguntas_exemplo):
    with cols_exemplos[idx]:
        if st.button(texto_exemplo, key=f"btn_exemplo_{idx}", width="stretch"):
            pergunta_clicada = texto_exemplo

st.divider()

# 7. Historico de Mensagens do Chat
if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            if msg.get("comando_oracle"):
                st.caption(f"Comando equivalente Oracle 26ai: `{msg['comando_oracle']}`")
            st.markdown(msg["content"])
            if msg.get("sql"):
                st.code(msg["sql"], language="sql")
            if msg.get("dados") is not None:
                st.dataframe(msg["dados"], hide_index=True)

# 8. Entrada do Usuario no Chat (ou clique em sugestao rapida)
prompt_input = st.chat_input(
    "Faça uma pergunta em português para o banco de dados HR...",
    submit_mode="disable",
)
prompt_ativo = pergunta_clicada or prompt_input

if prompt_ativo:
    st.session_state["messages"].append({"role": "user", "content": prompt_ativo})
    with st.chat_message("user"):
        st.markdown(prompt_ativo)

    with st.chat_message("assistant"):
        with st.spinner(f"Executando Select AI ({modo_selecionado})..."):
            try:
                resposta = processar_pergunta_select_ai(
                    pergunta=prompt_ativo,
                    modo=modo_selecionado,
                    modelo=modelo_ollama,
                    ollama_url=ollama_url,
                )
                st.caption(
                    f"Comando equivalente Oracle 26ai: `{resposta['comando_oracle']}`"
                )
                st.markdown(resposta["content"])
                if resposta.get("sql"):
                    st.code(resposta["sql"], language="sql")
                if resposta.get("dados") is not None:
                    st.dataframe(resposta["dados"], hide_index=True)
                st.session_state["messages"].append(resposta)
            except Exception as erro:
                st.error(
                    f"Não foi possível processar a consulta: {erro}",
                    title="Erro na execução do Select AI",
                )
