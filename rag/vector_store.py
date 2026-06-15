import os
import google.generativeai as genai
import numpy as np
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class LocalVectorStore:
    def __init__(self):
        self.chunks = []
        self.embeddings = []

    def populate_from_file(self, filepath: str):
        if self.chunks:
            return

        if not os.path.exists(filepath):
            # Create a placeholder if policy file is missing
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("Muthoot Gold Loan Policy:\nMax tenure is 12 months. Interest rate starts at 9.5%.\nRepayment channels include UPI and netbanking.")
        
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
            
        # Chunk text by paragraphs
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        for p in paragraphs:
            try:
                response = genai.embed_content(
                    model="models/text-embedding-004",
                    content=p,
                    task_type="retrieval_document",
                    request_options={"timeout": 10},
                )
                self.chunks.append(p)
                self.embeddings.append(response['embedding'])
            except Exception as e:
                print(f"Skipping paragraph chunk embedding creation error: {e}")

    def semantic_search(self, query: str, top_k: int = 2) -> str:
        if not self.embeddings:
            return ""
        try:
            query_resp = genai.embed_content(
                model="models/text-embedding-004",
                content=query,
                task_type="retrieval_query",
                request_options={"timeout": 10},
            )
            query_emb = query_resp['embedding']
            
            scores = []
            for emb in self.embeddings:
                # Cosine Similarity metric check
                dot_prod = np.dot(query_emb, emb)
                norm_q = np.linalg.norm(query_emb)
                norm_e = np.linalg.norm(emb)
                scores.append(dot_prod / (norm_q * norm_e))
                
            top_indices = np.argsort(scores)[-top_k:][::-1]
            return "\n".join([self.chunks[idx] for idx in top_indices])
        except Exception as e:
            print(f"Vector search failure: {e}")
            return ""
