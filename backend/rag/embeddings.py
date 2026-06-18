from sentence_transformers import SentenceTransformer
import numpy as np

from backend.config import settings


class EmbeddingModel:

    def __init__(self):

        print("Loading embedding model...")

        self.model = SentenceTransformer(
            settings.EMBEDDING_MODEL
        )

        print("Embedding model loaded.")

    def encode(
        self,
        text: str
    ) -> np.ndarray:

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
            convert_to_numpy=True
        )

        return embedding.astype("float32")


embedding_model = EmbeddingModel()