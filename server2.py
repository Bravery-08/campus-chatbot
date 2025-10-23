from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from groq import Groq
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone

load_dotenv()

app = Flask(__name__)
CORS(app)


class ResponseGenerator:
    def __init__(self, query):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.query = query

    def retrieve_context(self, top_k=5):

        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index("ai-index")

        query_embedding = model.encode(self.query).tolist()

        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_values=False,
            include_metadata=True
        )
        self.contexts = [match['metadata']['text']
                         for match in results['matches']]

    def get_response(self, temperature=0.1, max_tokens=512):

        sys_prompt = f"""
                You are an informative chatbot for VIT Chennai University that gives suitable responses based on the provided contexts.
            """

        user_prompt = f"""Use the following contexts to suitably answer the question:
            {self.contexts}
            
            Query:
            {self.query}
            
            Guidelines:
            - Do not mention the presence of contexts in your response. Make it seem like the query is being answered from your own knowledge.
            - If the query is not related to VIT Chennai, politely inform the user that you are only knowledgeable about VIT Chennai.
            - If the answer is not found in the contexts or if it is not completely answered, respond suitably with the information not being available.
            - Use a cheerful and friendly tone, using suitable punctuation where appropriate.
            - Don't use emojis.

            """

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
