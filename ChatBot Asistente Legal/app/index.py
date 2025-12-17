import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from typing import List, Dict

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "legal-assistant")

def init_pinecone():
    pc = Pinecone(api_key=PINECONE_API_KEY)

    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        print(f"✅ Índice '{INDEX_NAME}' creado en Pinecone.")

    return pc.Index(INDEX_NAME)

def build_embeddings_model():
    # Modelo optimizado para QA
    return SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")

def build_text_for_embedding(article: Dict) -> str:
    title = article.get("title", "")
    body = article.get("body", "")
    return f"Artículo {article['article_number']}: {title}\n{body}"

def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> List[str]:
    """
    Divide un texto largo en chunks de tamaño fijo con solapamiento.
    Esto evita superar el límite de metadata en Pinecone.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def upsert_articles(index, model, articles: List[Dict], source_name: str):
    to_upsert = []
    for a in articles:
        text = build_text_for_embedding(a)

        # 🔹 Dividir en chunks si es demasiado largo
        chunks = chunk_text(text, chunk_size=3000, overlap=300)

        for i, chunk in enumerate(chunks):
            vec = model.encode(chunk).tolist()
            metadata = {
                "article_number": a["article_number"],
                "title": a.get("title", ""),
                "text": chunk,  # ✅ cada chunk limitado
                "source": source_name,
            }
            # ID único por chunk
            vector_id = f"{a['id']}_chunk{i}"
            to_upsert.append((vector_id, vec, metadata))

    index.upsert(vectors=to_upsert)
    print(f"✅ {source_name} insertada en Pinecone con {len(to_upsert)} vectores")