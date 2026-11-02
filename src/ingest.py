import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH")
DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")
EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL")


def ingest_pdf():
    for name in ("PDF_PATH", "DATABASE_URL", "PG_VECTOR_COLLECTION_NAME", "GOOGLE_EMBEDDING_MODEL", "GOOGLE_API_KEY"):
        if not os.getenv(name):
            raise SystemExit(f"Variável {name} não definida no arquivo .env")

    reader = PdfReader(PDF_PATH)
    docs = [
        Document(
            page_content=page.extract_text(),
            metadata={"source": PDF_PATH, "page": i},
        )
        for i, page in enumerate(reader.pages)
    ]

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)

    store = PGVector(
        embeddings=GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL),
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
        pre_delete_collection=True,
    )
    store.add_documents(chunks)

    print(f"{len(docs)} páginas lidas, {len(chunks)} chunks salvos na coleção '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    ingest_pdf()
