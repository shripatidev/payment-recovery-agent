from agent import PaymentRecoveryAgent

agent = PaymentRecoveryAgent()

while True:
    user_message = input("You: ")

    if user_message.lower() == "exit":
        break

    answer = agent.ask(user_message)

    print("Agent:", answer)