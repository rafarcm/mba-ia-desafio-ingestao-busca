import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")
EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL")
LLM_MODEL = os.getenv("GOOGLE_LLM_MODEL")

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""


def search_prompt():
    for name in ("DATABASE_URL", "PG_VECTOR_COLLECTION_NAME", "GOOGLE_EMBEDDING_MODEL", "GOOGLE_LLM_MODEL", "GOOGLE_API_KEY"):
        if not os.getenv(name):
            print(f"Variável {name} não definida no arquivo .env")
            return None

    try:
        store = PGVector(
            embeddings=GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL),
            collection_name=COLLECTION_NAME,
            connection=DATABASE_URL,
            use_jsonb=True,
        )
    except Exception as e:
        print(f"Erro ao conectar no banco de dados: {e}")
        return None

    def buscar_contexto(pergunta):
        resultados = store.similarity_search_with_score(pergunta, k=10)
        return "\n\n".join(doc.page_content for doc, _score in resultados)

    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0)

    return (
        {"contexto": RunnableLambda(buscar_contexto), "pergunta": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
