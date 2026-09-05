from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

from tools import (get_payment_details, calculate_recovery_score, get_recovery_strategy, generate_payment_link, create_recovery_decision, get_recovery_queue, execute_recovery_action, record_recovery_outcome, get_recovery_analytics, get_recovery_insights, get_strategy_history)

load_dotenv()


class PaymentRecoveryAgent:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        self.client = genai.Client(api_key=api_key)

        self.tools = [
            types.Tool(
                function_declarations=[

                    types.FunctionDeclaration(
                        name="get_payment_details",
                        description="Get the details of a payment using its payment ID.",
                        parameters=types.Schema(
                            type="OBJECT",
                            properties={
                                "payment_id": types.Schema(
                                    type="STRING",
                                    description="The payment ID, for example PAY1002"
                                )
                            },
                            required=["payment_id"]
                        )
                    ),

                    types.FunctionDeclaration(
                        name="calculate_recovery_score",
                        description="Calculate the recovery score and priority for a failed payment using payment value, customer history, failure reason, attempts, and payment method.",
                        parameters=types.Schema(
                            type="OBJECT",
                            properties={
                                "payment_id": types.Schema(
                                    type="STRING",
                                    description="The payment ID for which the recovery score should be calculated."
                                )
                            },
                            required=["payment_id"]
                        )
                    ),

                    types.FunctionDeclaration(
    name="get_recovery_strategy",
    description="Determine the best recovery strategy for a failed payment using the complete payment context.",
    parameters=types.Schema(
        type="OBJECT",
        properties={
            "payment_id": types.Schema(
                type="STRING",
                description="The ID of the failed payment."
            ),
            "reason": types.Schema(
                type="STRING",
                description="The reason why the payment failed."
            ),
            "amount": types.Schema(
                type="NUMBER",
                description="The payment amount."
            ),
            "attempts": types.Schema(
                type="INTEGER",
                description="Number of payment attempts."
            ),
            "payment_method": types.Schema(
                type="STRING",
                description="Payment method used."
            ),
            "previous_successful_payments": types.Schema(
                type="INTEGER",
                description="Number of previous successful payments by the customer."
            ),
            "previous_failed_payments": types.Schema(
                type="INTEGER",
                description="Number of previous failed payments by the customer."
            ),
            "recovery_score": types.Schema(
                type="INTEGER",
                description="Recovery score from 0 to 100."
            )
        },
        required=[
            "payment_id",
            "reason",
            "amount",
            "attempts",
            "payment_method",
            "previous_successful_payments",
            "previous_failed_payments",
            "recovery_score"
        ]
    )
),

                    types.FunctionDeclaration(
                        name="generate_payment_link",
                        description="Generate a payment recovery link for a payment so the customer can retry the payment.",
                        parameters=types.Schema(
                            type="OBJECT",
                            properties={
                             "payment_id": types.Schema(
                                 type="STRING",
                                    description="The payment ID for which the recovery link should be generated."
            )
        },
        required=["payment_id"]
    )
),

                    types.FunctionDeclaration(
                        name="create_recovery_decision",
                        description="Create a structured recovery decision for a failed payment, including priority, strategy, confidence, and recommended action.",
                        parameters=types.Schema(
                            type="OBJECT",
                            properties={
                                "payment_id": types.Schema(
                                    type="STRING",
                                    description="The payment ID for which the recovery decision should be created."
            )
        },
        required=["payment_id"]
    )
),

                    types.FunctionDeclaration(
                        name="get_recovery_queue",
                        description="Get all failed payments prioritized by recovery score, with the highest-priority payments first.",
                        parameters=types.Schema(
                            type="OBJECT",
                            properties={}
                        )
),


                    types.FunctionDeclaration(
                        name="execute_recovery_action",
                        description="Execute the appropriate recovery action for a failed payment based on its recovery strategy.",
                        parameters=types.Schema(
                            type="OBJECT",
                            properties={
                                "payment_id": types.Schema(
                                    type="STRING",
                                    description="The payment ID for which the recovery action should be executed."
            )
        },
        required=["payment_id"]
    )
),

                    types.FunctionDeclaration(
    name="record_recovery_outcome",
    description="Record the outcome of a recovery action for a payment.",
    parameters=types.Schema(
        type="OBJECT",
        properties={
            "payment_id": types.Schema(
                type="STRING",
                description="The payment ID whose recovery outcome should be recorded."
            ),
            "outcome": types.Schema(
                type="STRING",
                description="The recovery outcome. Must be recovered, failed, or pending."
            )
        },
        required=["payment_id", "outcome"]
    )
),

                    types.FunctionDeclaration(
    name="get_recovery_analytics",
    description="Analyze historical payment recovery outcomes and show the performance of each recovery strategy.",
    parameters=types.Schema(
        type="OBJECT",
        properties={}
    )
),

                    types.FunctionDeclaration(
    name="get_recovery_insights",
    description="Generate human-readable insights from historical payment recovery performance.",
    parameters=types.Schema(
        type="OBJECT",
        properties={}
    )
),

                    types.FunctionDeclaration(
    name="get_strategy_history",
    description="Check the historical recovery performance of a specific recovery strategy.",
    parameters=types.Schema(
        type="OBJECT",
        properties={
            "strategy": types.Schema(
                type="STRING",
                description="The recovery strategy to check, for example retry_later or alternate_payment_method."
            )
        },
        required=["strategy"]
    )
),



                ]
            )
        ]

    def ask(self, user_message):
        contents = [types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)]
)]


        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                tools=self.tools,
                system_instruction="""
You are an AI payment recovery agent.

Your job is to investigate failed payments and recommend
the most appropriate recovery action.

When the user asks why a payment failed or asks for
a recovery recommendation:

1. Use get_payment_details to retrieve the payment information.

2. If the payment failed, use calculate_recovery_score.

3. Use get_recovery_strategy with the complete payment context.

4. After determining a recovery strategy, use get_strategy_history
   to check the historical performance of that specific strategy.

5. When recommending a recovery strategy, ALWAYS mention the
   historical performance returned by get_strategy_history,
   including the recovery rate, number of cases, recovered cases,
   failed cases, and pending cases when available.

6. If the historical recovery rate is low or zero, clearly warn
   the user that the strategy has weak historical performance
   and may require additional review.

7. Use get_recovery_analytics when the user asks for overall
   recovery statistics or strategy performance across all strategies.

8. Use get_recovery_insights when the user asks what we have
   learned from previous recovery attempts or asks for a
   human-readable summary of recovery performance.

9. Do not invent historical results. Only use information
   returned by the available tools.

10. Do not claim that historical data changed the strategy unless
    the tool actually selected a different strategy.

11. Do not execute a recovery action unless the user explicitly
    asks you to take or execute the action.

12. Give the user a concise explanation of the failure, recovery
    score, recommended strategy, priority, recommended action,
    and relevant historical performance.

Use the available tools instead of guessing payment information.
"""
    )
)

        while response.function_calls:

            function_call = response.function_calls[0]

            if function_call.name == "get_payment_details":

                payment_id = function_call.args["payment_id"]

                result = get_payment_details(payment_id)
                print("🔧 Agent called: get_payment_details")

            elif function_call.name == "calculate_recovery_score":

                print("🔧 Agent called: calculate_recovery_score")

                payment_id = function_call.args["payment_id"]

                result = calculate_recovery_score(payment_id)

            elif function_call.name == "get_recovery_strategy":

                print("🔧 Agent called: get_recovery_strategy")

                payment_id = function_call.args["payment_id"]
                reason = function_call.args["reason"]
                amount = function_call.args["amount"]
                attempts = function_call.args["attempts"]
                payment_method = function_call.args["payment_method"]
                previous_successful_payments = function_call.args[
                 "previous_successful_payments"
                ]
                previous_failed_payments = function_call.args[
                    "previous_failed_payments"
                ]
                recovery_score = function_call.args["recovery_score"]

                result = get_recovery_strategy(
                                payment_id=payment_id,
                                reason=reason,
                                amount=amount,
                                attempts=attempts,
                                payment_method=payment_method,
                                previous_successful_payments=previous_successful_payments,
                                previous_failed_payments=previous_failed_payments,
                                recovery_score=recovery_score
            ) 

                strategy = result["strategy"]

                history_result = get_strategy_history(strategy)

                print("🔧 Agent called: get_strategy_history")

                # Get the recovery score again so the final tool response
                # contains all important information needed for the answer.
                score_result = calculate_recovery_score(payment_id)

                result["recovery_score"] = score_result["recovery_score"]
                result["priority"] = score_result["priority"]
                result["historical_performance"] = history_result 
                
                    
                

            elif function_call.name == "generate_payment_link":

                print("🔧 Agent called: generate_payment_link")

                payment_id = function_call.args["payment_id"]

                result = generate_payment_link(payment_id)   

            elif function_call.name == "create_recovery_decision":

                print("🔧 Agent called: create_recovery_decision")

                payment_id = function_call.args["payment_id"]

                result = create_recovery_decision(payment_id)

            elif function_call.name == "get_recovery_queue":

                print("🔧 Agent called: get_recovery_queue")

                result = get_recovery_queue()  

            elif function_call.name == "execute_recovery_action":

                print("🔧 Agent called: execute_recovery_action")

                payment_id = function_call.args["payment_id"]

                result = execute_recovery_action(payment_id)

            elif function_call.name == "record_recovery_outcome":

                print("🔧 Agent called: record_recovery_outcome")

                payment_id = function_call.args["payment_id"]
                outcome = function_call.args["outcome"]

                result = record_recovery_outcome(
                    payment_id,
                    outcome
             )

            elif function_call.name == "get_recovery_analytics":

                print("🔧 Agent called: get_recovery_analytics")

                result = get_recovery_analytics()

            elif function_call.name == "get_recovery_insights":

                print("🔧 Agent called: get_recovery_insights")

                result = get_recovery_insights()

            elif function_call.name == "get_strategy_history":

                print("🔧 Agent called: get_strategy_history")

                strategy = function_call.args["strategy"]

                result = get_strategy_history(strategy)         

            else:

                return "I don't know how to use that tool."

            contents.append(response.candidates[0].content)

            contents.append(
                types.Content(
                    role="tool",
                    parts=[
                        types.Part.from_function_response(
                         name=function_call.name,
                            response=result
                        )
                 ]
             )
            )

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    tools=self.tools
                )
            )

                
            

            return response.text