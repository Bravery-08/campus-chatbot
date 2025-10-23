from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from groq import Groq
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, CrossEncoder
from pinecone import Pinecone

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize retrieval/reranking models once to avoid per-request overhead
# Keep the dense embedder consistent with the index dimension (384 for MiniLM-L6)
EMBEDDER = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
# Lightweight cross-encoder for MS MARCO-style reranking
RERANKER = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')


class ResponseGenerator:
    def __init__(self, query):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.query = query

    def retrieve_context(self, top_k=5):

        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index_name = os.getenv("PINECONE_INDEX_NAME", "ai-index")
        index = pc.Index(index_name)

        # Retrieve a larger pool of candidates for better reranking
        candidate_k = max(20, top_k * 6)

        query_embedding = EMBEDDER.encode(self.query).tolist()

        results = index.query(
            vector=query_embedding,
            top_k=candidate_k,
            include_values=False,
            include_metadata=True
        )

        candidate_texts = [m.get('metadata', {}).get('text', '') for m in results.get('matches', []) if m.get('metadata', {}).get('text')]

        if not candidate_texts:
            self.contexts = []
            return

        # Cross-encoder reranking
        pairs = [(self.query, text) for text in candidate_texts]
        scores = RERANKER.predict(pairs)
        scored = sorted(zip(candidate_texts, scores), key=lambda x: x[1], reverse=True)

        # Optional: filter out very weak matches
        min_score = float(os.getenv("RERANK_MIN_SCORE", 0.2))
        filtered = [text for text, score in scored if score >= min_score]

        self.contexts = (filtered[:top_k] if filtered else [t for t, _ in scored[:top_k]])

    def get_response(self, temperature=0.1, max_tokens=512):

        sys_prompt = (
            "You are an informative chatbot for VIT Chennai University that "
            "answers accurately and concisely based on internal knowledge."
        )

        # Build a grounded prompt that does not expose the word "context" to users
        context_block = "\n\n".join(f"• {c}" for c in (self.contexts or []))
        user_prompt = (
            "Answer the question using the following background information if relevant.\n"
            f"Background:\n{context_block}\n\n"
            f"Question: {self.query}\n\n"
            "Guidelines:\n"
            "- Do not mention background or sources explicitly.\n"
            "- If the query is not related to VIT Chennai, say you only cover VIT Chennai.\n"
            "- If information is missing, state that it is unavailable.\n"
            "- Be friendly and concise. No emojis."
        )

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content.strip()


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"response": "Please enter a question."}), 400
    bot = ResponseGenerator(query)
    bot.retrieve_context(top_k=5)
    return jsonify({"response": bot.get_response(temperature=0.1, max_tokens=512)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
