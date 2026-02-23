import os
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json

class RAGPipeline:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", vector_dir: str = "data/vectors"):
        self.model = SentenceTransformer(model_name)
        self.vector_dir = vector_dir
        self.index_path = os.path.join(vector_dir, "faiss.index")
        self.metadata_path = os.path.join(vector_dir, "metadata.json")
        self.index = None
        self.metadata = []
        os.makedirs(vector_dir, exist_ok=True)
        self._load_index()

    def _load_index(self):
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, 'r') as f:
                    self.metadata = json.load(f)

    def ingest_document(self, file_path: str):
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Chunking strategy: split by double newlines (paragraphs/sections)
        chunks = [c.strip() for c in content.split("\n\n") if len(c.strip()) > 10]
        
        embeddings = self.model.encode(chunks)
        
        if self.index is None:
            self.index = faiss.IndexFlatL2(embeddings.shape[1])
        
        self.index.add(np.array(embeddings).astype('float32'))
        
        for chunk in chunks:
            self.metadata.append({
                "source": os.path.basename(file_path),
                "content": chunk
            })
        
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=4)

    def query(self, text: str, k: int = 3) -> List[Dict[str, Any]]:
        if self.index is None:
            return []
        
        embedding = self.model.encode([text])
        distances, indices = self.index.search(np.array(embedding).astype('float32'), k)
        
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.metadata):
                results.append(self.metadata[idx])
        return results
