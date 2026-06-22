import os
import numpy as np
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class LocalVectorStore:

    def __init__(self):
        self.chunks = []
        self.embeddings = []

    def populate_from_file(self, filepath: str):

        if not os.path.exists(filepath):

            os.makedirs(
                os.path.dirname(filepath),
                exist_ok=True
            )

            with open(
                filepath,
                "w",
                encoding="utf-8"
            ) as f:

                f.write("""
Muthoot Gold Loan Policy

Gold loans are available against eligible gold ornaments.

Maximum tenure is 12 months.

Interest rates start from 9.5%.

Customers can repay through UPI, Net Banking, Cash and Branch Payments.

KYC verification is mandatory before loan approval.
""")

        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        paragraphs = [
            p.strip()
            for p in text.split("\n\n")
            if p.strip()
        ]

        self.chunks.clear()
        self.embeddings.clear()

        for paragraph in paragraphs:

            try:

                response = client.models.embed_content(
                    model="gemini-embedding-2",
                    contents=paragraph,
                    config={"task_type": "RETRIEVAL_DOCUMENT"}
                )

                embedding = response.embeddings[0].values

                self.chunks.append(paragraph)
                self.embeddings.append(embedding)

            except Exception as e:

                print(f"Embedding Error: {e}")

    def semantic_search(
        self,
        query: str,
        top_k: int = 2
    ) -> str:

        if not self.embeddings:
            return ""

        try:

            response = client.models.embed_content(
                model="gemini-embedding-2",
                contents=query,
                config={"task_type": "RETRIEVAL_QUERY"}
            )

            query_embedding = response.embeddings[0].values

            scores = []

            for embedding in self.embeddings:

                similarity = (
                    np.dot(query_embedding, embedding)
                    /
                    (
                        np.linalg.norm(query_embedding)
                        * np.linalg.norm(embedding)
                    )
                )

                scores.append(similarity)

            top_indices = np.argsort(scores)[-top_k:][::-1]

            return "\n\n".join(
                self.chunks[i]
                for i in top_indices
            )

        except Exception as e:

            print(f"Vector Search Error: {e}")
            return ""