import os
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer


class LocalVectorStore:

    def __init__(self): 

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2",
            local_files_only=True
        )

        self.index = None
        self.documents = []

    def populate_from_file(
        self,
        filepath: str
    ):

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

                f.write(
"""
Muthoot Gold Loan Policy

Gold loans are available against eligible gold ornaments.

Maximum tenure is 12 months.

Interest rates start from 9.5%.

Customers can repay through UPI, Net Banking, Cash and Branch Payments.

KYC verification is mandatory before loan approval.

Gold purity must generally be 18K or above.

Loans are subject to verification and approval.

Customers may close loans early without restrictions depending on the loan scheme.

EMI reminders are sent through SMS.

For assistance contact Muthoot Fincorp Customer Support.
"""
                )

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as f:

            text = f.read()

        chunks = [

            chunk.strip()

            for chunk in text.split("\n\n")

            if chunk.strip()

        ]

        self.documents = chunks

        embeddings = self.model.encode(
            chunks,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.index.add(
            embeddings.astype(np.float32)
        )

    def semantic_search(
        self,
        query: str,
        top_k: int = 3
    ):

        if self.index is None:

            return ""

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        scores, indices = self.index.search(
            query_embedding.astype(np.float32),
            top_k
        )

        results = []

        for idx in indices[0]:

            if idx != -1:

                results.append(
                    self.documents[idx]
                )

        return "\n".join(results)