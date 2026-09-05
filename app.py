from flask import Flask, request, jsonify, send_from_directory
from agent import PaymentRecoveryAgent

app = Flask(__name__)

agent = PaymentRecoveryAgent()


@app.route("/")
def home():
    return send_from_directory("frontend", "index.html")


@app.route("/frontend/<path:filename>")
def frontend_files(filename):
    return send_from_directory("frontend", filename)


@app.route("/api/ask", methods=["POST"])
def ask_agent():

    data = request.get_json()

    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({
            "error": "Message cannot be empty."
        }), 400

    try:

        print("🚀 Calling agent.ask()...")

        response = agent.ask(user_message)

        print("✅ Agent returned a response")

        return jsonify({
            "response": response
        })

    except Exception as e:

        print("❌ ERROR:", e)

        return jsonify({
            "error": str(e)
    }), 500

if __name__ == "__main__":
    app.run(debug=True)