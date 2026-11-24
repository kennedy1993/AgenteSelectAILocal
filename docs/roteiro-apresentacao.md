# Roteiro de demonstração — Select AI Local

Material de apoio para apresentar o protótipo ao gestor e a clientes. A demonstração usa somente dados fictícios locais.

## Resumo executivo

O projeto demonstra como uma pergunta em Português pode ser convertida em SQL e apresentada em uma interface conversacional, sem enviar a pergunta a uma API de IA na nuvem. O fluxo combina Streamlit, LangChain (LCEL), Ollama e um banco SQLite de demonstração baseado em um subconjunto do schema HR.

**Importante:** é um protótipo inspirado no Select AI. Não é um produto Oracle, não se conecta ao Oracle Database e não foi preparado ou certificado para processar dados reais ou uso em produção.

## Pré-requisitos para a apresentação

- Docker Desktop em execução.
- Python e dependências do projeto instalados.
- Container Ollama iniciado e modelo `qwen3.5:0.8b` disponível.
- Aplicação iniciada com `streamlit run app.py`.
- Navegador aberto em `http://localhost:8501`.

## Roteiro sugerido (5 minutos)

1. **Apresentar a tela inicial:** mostrar as métricas e o explorador das tabelas `EMPLOYEES`, `JOB_HISTORY`, `DEPARTMENTS` e `JOBS`.
2. **Demonstrar `showsql`:** perguntar “Mostre quais funcionários mudaram de cargo pelo menos duas vezes” e destacar que o modo mostra a SQL sem executá-la.
3. **Demonstrar `runsql`:** repetir a pergunta e mostrar a consulta e os três resultados esperados: Neena Yang, Jonathon Taylor e Jennifer Whalen.
4. **Demonstrar `narrate`:** repetir a pergunta e mostrar a explicação em linguagem natural baseada nos resultados da consulta.
5. **Demonstrar `chat`:** perguntar “Qual é a diferença entre SELECT e JOIN?” e explicar que esse modo é uma conversa geral, não uma consulta aos dados do banco.

## Validação técnica realizada

- Aplicação Streamlit inicializada e página carregada com status `ready` em execução local.
- Ollama respondeu localmente e tinha o modelo `qwen3.5:0.8b` disponível (Python 3.12.8, Streamlit 1.67.0, Docker 29.9.2).
- `showsql`, `runsql`, `narrate` e `chat` foram acionados com perguntas de demonstração.
- A consulta de mudanças de cargo retornou os três nomes esperados em `runsql`; `narrate` mencionou os mesmos nomes.
- O teste inicial identificou uma resposta incorreta de `chat` sobre `showsql`. O prompt foi esclarecido e o reteste descreveu corretamente que `showsql` gera SQL sem executá-lo.
- Os quatro testes automatizados do banco passaram com `python -m unittest discover -s tests -v`.
- A primeira matriz Text-to-SQL contém 15 perguntas e obteve 8 aprovações (53,3%) com `qwen3.5:0.8b`, em uma única execução a temperatura 0. Consulte o [relatório detalhado](../evals/resultados_qwen3.5_0.8b.md); esse resultado é uma linha de base, não uma avaliação estatística.

## Mensagens-chave e limites

- A inferência do modelo ocorre no Ollama local; a primeira instalação ainda precisa baixar a imagem Docker e o modelo.
- O SQLite contém dados fictícios e um schema demonstrativo reduzido, não uma cópia integral de uma instalação Oracle HR.
- A geração de SQL por um LLM pode variar. Revise as consultas e os resultados; os guardrails de demonstração não substituem controles de segurança de produção.
- O repositório não deve ser apresentado como software open source até que uma licença seja escolhida e publicada.

## Próximos passos antes de uma demonstração externa

1. Escolher uma licença com o gestor antes de anunciar o repositório como open source.
2. `hr_oracle.db` foi removido do índice do Git e incluído no `.gitignore`; a cópia local foi preservada. A remoção só chegará ao GitHub quando for revisada e commitada.
3. Não conectar dados, credenciais ou ambientes de clientes a este protótipo.
