import json
import os
HISTORY_FILE = "recovery_history.json"


def load_recovery_history():
    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE, "r") as file:
        return json.load(file)
payments = {

    "PAY1001": {
        "status": "success",
        "amount": 500,
        "customer": "Rahul",
        "attempts": 1,
        "payment_method": "UPI",
        "previous_successful_payments": 8,
        "previous_failed_payments": 0
    },

    "PAY1002": {
        "status": "failed",
        "amount": 1200,
        "customer": "Priya",
        "reason": "Insufficient funds",
        "attempts": 1,
        "payment_method": "UPI",
        "previous_successful_payments": 6,
        "previous_failed_payments": 1
    },

    "PAY1003": {
        "status": "failed",
        "amount": 750,
        "customer": "Arjun",
        "reason": "Card expired",
        "attempts": 2,
        "payment_method": "Credit Card",
        "previous_successful_payments": 12,
        "previous_failed_payments": 2
    },

    "PAY1004": {
        "status": "failed",
        "amount": 2000,
        "customer": "Sneha",
        "reason": "Bank declined the transaction",
        "attempts": 3,
        "payment_method": "Debit Card",
        "previous_successful_payments": 15,
        "previous_failed_payments": 3
    }

}


def get_payment_details(payment_id):
    """
    Look up payment information using a payment ID.
    """

    payment = payments.get(payment_id)

    if payment is None:
        return {
            "error": "Payment not found"
        }

    return payment

def get_recovery_strategy(
    payment_id,
    reason,
    amount,
    attempts,
    payment_method,
    previous_successful_payments,
    previous_failed_payments,
    recovery_score
):
    """
    Decide the best recovery strategy based on the payment failure reason.
    """

    strategies = {
        "Insufficient funds": {
            "strategy": "retry_later",
            "recommended_action": "Ask the customer to add sufficient funds and retry the payment.",
            "priority": "medium"
        },

        "Card expired": {
            "strategy": "update_payment_method",
            "recommended_action": "Ask the customer to update their expired card and try again.",
            "priority": "high"
        },

        "Bank declined the transaction": {
            "strategy": "alternate_payment_method",
            "recommended_action": "Ask the customer to try another payment method.",
            "priority": "high"
        }
    }

    return strategies.get(
        reason,
        {
            "strategy": "manual_review",
            "recommended_action": "Review the payment manually before taking action.",
            "priority": "medium"
        }
    )

def generate_payment_link(payment_id):
    """
    Simulate creating a payment recovery link.
    """

    payment = payments.get(payment_id)

    if payment is None:
        return {
            "status": "failed",
            "message": "Payment not found"
        }

    return {
        "status": "created",
        "payment_id": payment_id,
        "amount": payment["amount"],
        "customer": payment["customer"],
        "payment_link": f"https://pay.example.com/recover/{payment_id}"
    }

def create_recovery_decision(payment_id):
    """
    Create a structured recovery decision for a failed payment.
    """

    payment = payments.get(payment_id)

    if payment is None:
        return {
            "status": "error",
            "message": "Payment not found"
        }

    

    if payment["status"] == "success":
        return {
            "status": "not_required",
            "message": "Payment was successful. No recovery action is required."
        }

    reason = payment["reason"]

    strategy = get_recovery_strategy(
    payment_id=payment_id,
    reason=reason,
    amount=payment["amount"],
    attempts=payment.get("attempts", 1),
    payment_method=payment.get("payment_method", "Unknown"),
    previous_successful_payments=payment.get("previous_successful_payments", 0),
    previous_failed_payments=payment.get("previous_failed_payments", 0),
    recovery_score=calculate_recovery_score(payment_id)["recovery_score"]
)

    strategy_history = get_strategy_history(strategy["strategy"])

    log_activity(
        payment_id,
        "recovery_decision",
        f"Strategy: {strategy['strategy']}, "
        f"Priority: {strategy['priority']}, "
        f"Confidence: high"
    )

    return {
        "status": "recovery_required",
        "payment_id": payment_id,
        "customer": payment["customer"],
        "amount": payment["amount"],
        "failure_reason": reason,
        "strategy": strategy["strategy"],
        "priority": strategy["priority"],
        "recommended_action": strategy["recommended_action"],
        "confidence": "high",
        "historical_performance": strategy_history
    }

def calculate_recovery_score(payment_id):
    """
    Calculate how likely and valuable a failed payment is to recover.
    Score ranges from 0 to 100.
    """

    payment = payments.get(payment_id)

    if payment is None:
        return {
            "status": "error",
            "message": "Payment not found"
        }

    if payment["status"] == "success":
        return {
            "status": "not_required",
            "message": "Payment was successful. No recovery needed."
        }

    score = 0

    # Factor 1: Transaction value (maximum 25 points)
    amount = payment["amount"]

    if amount >= 50000:
        score += 25
    elif amount >= 10000:
        score += 20
    elif amount >= 5000:
        score += 15
    elif amount >= 1000:
        score += 10
    else:
        score += 5

    # Factor 2: Customer history (maximum 25 points)
    successful_payments = payment.get(
        "previous_successful_payments", 0
    )

    failed_payments = payment.get(
        "previous_failed_payments", 0
    )

    if successful_payments >= 15:
        score += 25
    elif successful_payments >= 10:
        score += 20
    elif successful_payments >= 5:
        score += 15
    elif successful_payments >= 1:
        score += 10
    else:
        score += 5

    # Reduce score slightly if the customer has many failures
    if failed_payments >= 5:
        score -= 5
    elif failed_payments >= 3:
        score -= 2

    # Factor 3: Failure recoverability (maximum 25 points)
    reason = payment.get("reason", "").lower()

    if "expired" in reason:
        score += 25
    elif "insufficient" in reason:
        score += 20
    elif "declined" in reason or "bank" in reason:
        score += 15
    else:
        score += 10

    # Factor 4: Attempt pattern (maximum 15 points)
    attempts = payment.get("attempts", 1)

    if attempts == 1:
        score += 15
    elif attempts == 2:
        score += 10
    elif attempts == 3:
        score += 5
    else:
        score += 2

    # Factor 5: Payment method (maximum 10 points)
    payment_method = payment.get("payment_method", "").lower()

    if payment_method == "upi":
        score += 10
    elif payment_method == "credit card":
        score += 8
    elif payment_method == "debit card":
        score += 7
    else:
        score += 5

    # Keep score between 0 and 100
    score = max(0, min(score, 100))

    # Determine priority
    if score >= 75:
        priority = "high"
    elif score >= 50:
        priority = "medium"
    else:
        priority = "low"

    return {
        "status": "scored",
        "payment_id": payment_id,
        "amount": payment["amount"],
        "customer": payment["customer"],
        "attempts": attempts,
        "payment_method": payment.get("payment_method"),
        "failure_reason": payment.get("reason"),
        "previous_successful_payments": successful_payments,
        "previous_failed_payments": failed_payments,
        "recovery_score": score,
        "priority": priority
    }

def get_recovery_queue():
    """
    Create a prioritized queue of failed payments.
    """

    queue = []

    for payment_id, payment in payments.items():

        if payment["status"] != "failed":
            continue

        result = calculate_recovery_score(payment_id)

        if result["status"] == "scored":
            queue.append(result)

    queue.sort(
        key=lambda payment: payment["recovery_score"],
        reverse=True
    )

    return {
    "status": "success",
    "count": len(queue),
    "payments": queue
    }

def execute_recovery_action(payment_id):
    """
    Execute the appropriate recovery action for a failed payment.
    """

    decision = create_recovery_decision(payment_id)

    if decision["status"] != "recovery_required":
        return decision

    strategy = decision["strategy"]
    priority = decision["priority"]

    if strategy == "retry_later":

        message = "Customer should add sufficient funds and retry the payment."

        log_activity(
            payment_id,
            "action_planned",
            message
        )

        return {
            "status": "action_planned",
            "payment_id": payment_id,
            "action": "retry_later",
            "priority": priority,
            "message": message
        }

    elif strategy == "update_payment_method":

        message = "Customer should update their payment method."

        log_activity(
            payment_id,
            "action_planned",
            message
        )

        return {
            "status": "action_planned",
            "payment_id": payment_id,
            "action": "update_payment_method",
            "priority": priority,
            "message": message
        }

    elif strategy == "contact_customer":

        message = "Customer should be contacted regarding the failed payment."

        log_activity(
            payment_id,
            "action_planned",
            message
        )

        return {
            "status": "action_planned",
            "payment_id": payment_id,
            "action": "contact_customer",
            "priority": priority,
            "message": message
        }

    else:

        message = "Payment requires manual review."

        log_activity(
            payment_id,
            "action_planned",
            message
        )

        return {
            "status": "action_planned",
            "payment_id": payment_id,
            "action": "manual_review",
            "priority": priority,
            "message": message
        }


def record_recovery_outcome(payment_id, outcome):
    """
    Record the outcome of a recovery action.
    """

    valid_outcomes = ["recovered", "failed", "pending"]

    if outcome not in valid_outcomes:
        return {
            "status": "error",
            "message": "Invalid outcome. Use recovered, failed, or pending."
        }

    payment = payments.get(payment_id)

    if payment is None:
        return {
            "status": "error",
            "message": "Payment not found"
        }
    decision = create_recovery_decision(payment_id)

    log_activity(
        payment_id,
        "recovery_outcome",
        f"Recovery outcome: {outcome}"
    )

    history = load_recovery_history()

    history.append({
    "payment_id": payment_id,
    "amount": payment["amount"],
    "failure_reason": payment["reason"],
    "strategy": decision["strategy"],
    "outcome": outcome
})

    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=4)

    return {
        "status": "outcome_recorded",
        "payment_id": payment_id,
        "outcome": outcome
    }

activity_log = []


def log_activity(payment_id, action, details):
    """
    Record an action performed by the recovery agent.
    """

    activity = {
        "payment_id": payment_id,
        "action": action,
        "details": details
    }

    activity_log.append(activity)

    return activity

def get_recovery_analytics():
    """
    Analyze historical recovery outcomes and strategy performance.
    """

    history = load_recovery_history()

    if not history:
        return {
            "status": "success",
            "total_recovery_cases": 0,
            "recovered": 0,
            "failed": 0,
            "pending": 0,
            "recovery_rate": 0,
            "strategy_performance": {}
        }

    total = len(history)

    recovered = sum(
        1 for record in history
        if record["outcome"] == "recovered"
    )

    failed = sum(
        1 for record in history
        if record["outcome"] == "failed"
    )

    pending = sum(
        1 for record in history
        if record["outcome"] == "pending"
    )

    recovery_rate = round(
        (recovered / total) * 100,
        2
    )

    # Analyze performance of each recovery strategy
    strategy_performance = {}

    for record in history:

        strategy = record.get("strategy", "unknown")

        if strategy not in strategy_performance:
            strategy_performance[strategy] = {
                "total": 0,
                "recovered": 0,
                "failed": 0,
                "pending": 0
            }

        strategy_performance[strategy]["total"] += 1

        if record["outcome"] == "recovered":
            strategy_performance[strategy]["recovered"] += 1

        elif record["outcome"] == "failed":
            strategy_performance[strategy]["failed"] += 1

        elif record["outcome"] == "pending":
            strategy_performance[strategy]["pending"] += 1

    # Calculate recovery rate for each strategy
    for strategy, data in strategy_performance.items():

        if data["total"] > 0:
            data["recovery_rate"] = round(
                (data["recovered"] / data["total"]) * 100,
                2
            )
        else:
            data["recovery_rate"] = 0

    return {
        "status": "success",
        "total_recovery_cases": total,
        "recovered": recovered,
        "failed": failed,
        "pending": pending,
        "recovery_rate": recovery_rate,
        "strategy_performance": strategy_performance
    }

def get_strategy_history(strategy):
    """
    Check how a recovery strategy has performed historically.
    """

    history = load_recovery_history()

    total = 0
    recovered = 0
    failed = 0
    pending = 0

    for record in history:

        if record.get("strategy") == strategy:

            total += 1

            if record.get("outcome") == "recovered":
                recovered += 1

            elif record.get("outcome") == "failed":
                failed += 1

            elif record.get("outcome") == "pending":
                pending += 1

    if total == 0:
        return {
            "status": "no_history",
            "strategy": strategy,
            "message": "No historical data is available for this strategy."
        }

    recovery_rate = round((recovered / total) * 100, 2)

    return {
        "status": "success",
        "strategy": strategy,
        "total_cases": total,
        "recovered": recovered,
        "failed": failed,
        "pending": pending,
        "recovery_rate": recovery_rate
    }

def get_recovery_insights():
    """
    Generate useful insights from historical recovery performance.
    """

    analytics = get_recovery_analytics()

    if analytics["total_recovery_cases"] == 0:
        return {
            "status": "success",
            "insights": [
                "No recovery history is available yet."
            ]
        }

    insights = []

    total = analytics["total_recovery_cases"]
    recovered = analytics["recovered"]
    failed = analytics["failed"]
    recovery_rate = analytics["recovery_rate"]

    insights.append(
        f"{recovered} of {total} recovery cases were successful, "
        f"giving an overall recovery rate of {recovery_rate}%."
    )

    if failed > 0:
        insights.append(
            f"{failed} recovery case(s) were unsuccessful."
        )

    strategy_performance = analytics["strategy_performance"]

    for strategy, data in strategy_performance.items():

        insights.append(
            f"The {strategy} strategy has been used in "
            f"{data['total']} case(s), with a "
            f"{data['recovery_rate']}% recovery rate."
        )

    return {
        "status": "success",
        "insights": insights
    }