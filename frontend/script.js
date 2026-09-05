const payments = {

    PAY1002: {
        customer: "Priya",
        amount: 1200,
        reason: "Insufficient funds",
        strategy: "retry_later",
        priority: "MEDIUM",
        score: 60,
        history: "100%"
    },

    PAY1003: {
        customer: "Arjun",
        amount: 750,
        reason: "Card expired",
        strategy: "update_payment_method",
        priority: "HIGH",
        score: 68,
        history: "100%"
    },

    PAY1004: {
        customer: "Sneha",
        amount: 2000,
        reason: "Bank declined the transaction",
        strategy: "alternate_payment_method",
        priority: "HIGH",
        score: 67,
        history: "0%"
    }

};


function showPayment(paymentId) {

    const payment = payments[paymentId];

    if (!payment) {
        return;
    }

    document.getElementById("detailTitle").innerText =
        paymentId;

    document.getElementById("detailSubtitle").innerText =
        `${payment.customer} • ₹${payment.amount}`;

    document.getElementById("detailsContent").innerHTML = `

        <div class="detail-grid">

            <div class="detail-item">
                <span>Customer</span>
                <strong>${payment.customer}</strong>
            </div>

            <div class="detail-item">
                <span>Amount</span>
                <strong>₹${payment.amount}</strong>
            </div>

            <div class="detail-item">
                <span>Failure Reason</span>
                <strong>${payment.reason}</strong>
            </div>

            <div class="detail-item">
                <span>Priority</span>
                <strong>${payment.priority}</strong>
            </div>

            <div class="detail-item">
                <span>Recovery Strategy</span>
                <strong>${payment.strategy}</strong>
            </div>

            <div class="detail-item">
                <span>Recovery Score</span>
                <strong>${payment.score}/100</strong>
            </div>

            <div class="detail-item">
                <span>Historical Recovery</span>
                <strong>${payment.history}</strong>
            </div>

            <div class="detail-item">
                <span>Recommended Action</span>
                <strong>
                    Try recommended recovery strategy
                </strong>
            </div>

        </div>
    `;
}


function handleEnter(event) {

    if (event.key === "Enter") {
        askAgent();
    }

}


async function askAgent() {

    const input = document.getElementById("userInput");

    const question = input.value.trim();

    if (!question) {
        return;
    }

    const chat = document.getElementById("chatBox");


    // Show user's message

    chat.innerHTML += `

        <div class="message user-message">

            <p>${question}</p>

        </div>

    `;


    input.value = "";


    // Show thinking message

    chat.innerHTML += `

        <div class="message agent-message" id="thinkingMessage">

            <div class="message-icon">
                AI
            </div>

            <div>
                <p>Thinking...</p>
            </div>

        </div>

    `;


    chat.scrollTop = chat.scrollHeight;


    try {

        const response = await fetch("/api/ask", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: question
            })

        });


        const data = await response.json();


        // Remove thinking message

        const thinkingMessage =
            document.getElementById("thinkingMessage");

        if (thinkingMessage) {
            thinkingMessage.remove();
        }


        if (data.error) {

            chat.innerHTML += `

                <div class="message agent-message">

                    <div class="message-icon">
                        AI
                    </div>

                    <div>
                        <p>Error: ${data.error}</p>
                    </div>

                </div>

            `;

            return;
        }


        // Show actual agent response

        chat.innerHTML += `

            <div class="message agent-message">

                <div class="message-icon">
                    AI
                </div>

                <div>
                    <p>${data.response}</p>
                </div>

            </div>

        `;


        chat.scrollTop = chat.scrollHeight;


    } catch (error) {

        const thinkingMessage =
            document.getElementById("thinkingMessage");

        if (thinkingMessage) {
            thinkingMessage.remove();
        }


        chat.innerHTML += `

            <div class="message agent-message">

                <div class="message-icon">
                    AI
                </div>

                <div>
                    <p>
                        Could not connect to the AI agent.
                        Make sure the Python server is running.
                    </p>
                </div>

            </div>

        `;
    }

}


function refreshDashboard() {

    const button =
        document.querySelector(".refresh-btn");

    button.innerText = "Refreshing...";

    setTimeout(() => {

        button.innerText = "↻ Refresh";

    }, 700);

}