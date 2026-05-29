import argparse
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_postgres.vectorstores import PGVector
from dotenv import load_dotenv

load_dotenv()

COLLECTION_MAP = {
    "benin": "legal_docs_benin",
    "madagascar": "legal_docs_madagascar",
}

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=["\n\n", "\n", ".", " "],
)

def load_document(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return PyPDFLoader(str(path)).load()
    elif suffix in [".txt", ".md"]:
        return TextLoader(str(path), encoding="utf-8").load()
    elif suffix in [".docx"]:
        return Docx2txtLoader(str(path)).load()
    elif suffix in [".doc"]:
        print(f"  ⚠️  .doc format not supported: {path.name} — convert to .docx and retry.")
        return []
    else:
        print(f"  ⚠️  Unsupported format: {path.name}, skipping.")
        return []

def ingest(country: str, data_path: str):
    print(f"\n🚀 Ingesting documents for: {country.upper()}")

    all_chunks = []
    docs_path = Path(data_path)

    for file_path in docs_path.rglob("*"):
        if file_path.is_file():
            print(f"  📄 Loading: {file_path.name}")
            try:
                raw_docs = load_document(file_path)
                chunks = splitter.split_documents(raw_docs)
                for chunk in chunks:
                    chunk.metadata["source"] = file_path.name
                    chunk.metadata["country"] = country
                all_chunks.extend(chunks)
                print(f"     ✅ {len(chunks)} chunks")
            except Exception as e:
                print(f"     ❌ Error: {e} — skipping")

    print(f"\n  📦 Total: {len(all_chunks)} chunks ready")
    print(f"  🔄 Uploading to Supabase (this may take a few minutes)...")

    database_url = os.getenv("DATABASE_URL")
    collection_name = COLLECTION_MAP[country]

    batch_size = 50
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i+batch_size]
        PGVector.from_documents(
            documents=batch,
            embedding=embeddings,
            collection_name=collection_name,
            connection=database_url,
            use_jsonb=True,
            pre_delete_collection=False,
        )
        print(f"  ⬆️  Uploaded {min(i+batch_size, len(all_chunks))}/{len(all_chunks)} chunks")

    print(f"\n  🎉 Done! {len(all_chunks)} chunks stored for {country}.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", required=True, choices=["benin", "madagascar"])
    parser.add_argument("--path", required=True)
    args = parser.parse_args()
    ingest(args.country, args.path)