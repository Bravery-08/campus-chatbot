from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import os
from hashlib import sha256
from dotenv import load_dotenv, find_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)


class Vectorize:
    def __init__(self):
        self.paragraphs = []
        self.embeddings = []
        return

    def vectorize(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            self.paragraphs = [line.strip() for line in f if line.strip()]
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.embeddings = model.encode(self.paragraphs)

    def upload_to_pinecone(self, index_name=None, batch_size=100):
        api_key = os.getenv("PINECONE_API_KEY")
        if index_name is None:
            index_name = os.getenv("PINECONE_INDEX_NAME", "ai-index")
        pc = Pinecone(api_key=api_key)
        if not pc.has_index(index_name):
            pc.create_index(
                name=index_name,
                dimension=384,
                metric="cosine",
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )

        index = pc.Index(index_name)

        total = len(self.paragraphs)
        for i in range(0, total, batch_size):
            batch_vectors = [
                {
                    "id": f"para-{sha256(self.paragraphs[j].encode('utf-8')).hexdigest()}",
                    "values": self.embeddings[j].tolist(),
                    "metadata": {"text": self.paragraphs[j]}
                }
                for j in range(i, min(i + batch_size, total))
            ]
            index.upsert(vectors=batch_vectors)


if __name__ == "__main__":
    vectorizer = Vectorize()
    vectorizer.vectorize('data.txt')
    vectorizer.upload_to_pinecone(os.getenv("PINECONE_INDEX_NAME", "ai-index"))

