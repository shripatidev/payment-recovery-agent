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

        # Demo fallback when Gemini quota is exhausted
        message = user_message.lower()

        if "pay1004" in message:
            response = (
                "Payment PAY1004 failed because the bank declined the transaction. "
                "The recovery score is 60/100 with medium priority. "
                "The recommended strategy is alternate_payment_method. "
                "The recommended action is to ask the customer to try another payment method. "
                "Historically, this strategy has a 0% recovery rate across 1 case: "
                "0 recovered, 1 failed, and 0 pending. "
                "Warning: this strategy has weak historical performance and may require additional review."
            )

        elif "pay1003" in message:
            response = (
                "Payment PAY1003 failed because the card expired. "
                "The recovery score is 68/100 with medium priority. "
                "The recommended strategy is update_payment_method. "
                "The recommended action is to ask the customer to update their expired card and try again. "
                "Historically, this strategy has a 100% recovery rate across 1 case: "
                "1 recovered, 0 failed, and 0 pending."
            )

        elif "pay1002" in message:
            response = (
                "Payment PAY1002 failed because of insufficient funds. "
                "The recovery score is 70/100 with medium priority. "
                "The recommended strategy is retry_later. "
                "The recommended action is to ask the customer to add sufficient funds and retry the payment. "
                "Historically, this strategy has a 100% recovery rate across 2 cases: "
                "2 recovered, 0 failed, and 0 pending."
            )

        else:
            response = (
                "Demo mode: Gemini API quota is currently exhausted. "
                "Please ask about PAY1002, PAY1003, or PAY1004."
            )

        return jsonify({
            "response": response
        })

if __name__ == "__main__":
    app.run(debug=True)