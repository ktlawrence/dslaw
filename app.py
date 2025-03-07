import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import openai

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Get API key securely
API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not API_KEY:
    raise ValueError("❌ ERROR: Missing DeepSeek API Key. Please set DEEPSEEK_API_KEY in .env")

# Initialize OpenAI client
client = openai.OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message")
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Enable streaming response
        def generate():
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_message}
                ],
                stream=True  # Enable streaming
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        return Response(generate(), content_type="text/plain")

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
