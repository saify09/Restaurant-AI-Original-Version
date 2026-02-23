from src.utils.rag_pipeline import RAGPipeline
import os

def init_rag():
    rag = RAGPipeline()
    docs = [
        "data/terms_and_conditions.md",
        "data/privacy_policy.md",
        "data/menu.md"
    ]
    
    print("Ingesting documents into RAG...")
    for doc in docs:
        if os.path.exists(doc):
            print(f"Ingesting {doc}...")
            rag.ingest_document(doc)
        else:
            print(f"Missing {doc}")
    print("RAG initialization complete.")

if __name__ == "__main__":
    init_rag()
