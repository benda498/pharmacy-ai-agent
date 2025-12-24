import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Import our tools and database functions
from tools import tools
from database import medication_exists, get_medication_availability, get_medication_profile, check_user_prescription

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# System prompt - defines the agent's role and behavior
SYSTEM_PROMPT = """You are a helpful pharmacy assistant for a retail pharmacy chain.

Your role:
- Check medication availability and prices
- Provide dosage, usage, and ingredient information
- Always provide factual information only
- Speak both Hebrew and English fluently

Critical safety rules:
- NEVER provide medical advice or diagnosis
- NEVER recommend purchasing medications
- NEVER suggest personalized dosage - always say: "General dosage is X, but consult your doctor for personalized advice"
- If asked for medical advice, redirect to a healthcare professional

Prescription medications:
- For prescription medications, dosage/usage information is only provided if the user has a valid prescription
- If user lacks prescription, inform them: "This medication requires a prescription. You don't have one in our system. Please consult your doctor."
- Non-prescription medications: provide information freely

Response style:
- Reply in the SAME LANGUAGE the user wrote (Hebrew/English)
- Keep answers SHORT and SIMPLE
- Use ₪ symbol for prices

Tool usage workflow:
1. First: use medication_exists to check if medication is in database
   - Not found - "We don't carry [medication]"
   - Found - proceed to step 2

2. Based on user's question:
   - AVAILABILITY/STOCK questions → use get_medication_availability
   - PRICE questions → use get_medication_availability  
   - DOSAGE/USAGE/INGREDIENTS questions → use get_medication_profile

3. Answer ONLY what was asked - don't volunteer extra information
   - If asked about price - provide price only (not stock status)
   - If asked about dosage - provide dosage only (not price)

4. When providing dosage, always add disclaimer: "This is general information. Consult your doctor or pharmacist for personalized advice."
"""

def execute_tool_call(tool_name, arguments, verified_user):
    """
    Execute the actual function based on the tool name.

    Args:
        tool_name (str): Name of the tool to execute
        arguments (dict): Arguments to pass to the function
        verified_user (dict): Current verified user information

    Returns:
        dict: Result from the function
    """
    if tool_name == "medication_exists":
        medication_name = arguments.get("medication_name")
        return medication_exists(medication_name)

    elif tool_name == "get_medication_availability":
        medication_id = arguments.get("medication_id")
        return get_medication_availability(medication_id)

    elif tool_name == "get_medication_profile":
        medication_id = arguments.get("medication_id")
        # Pass user's ID number for prescription check
        id_number = verified_user["id_number"] if verified_user else None
        return get_medication_profile(medication_id, id_number)

    else:
        return {"error": f"Unknown tool: {tool_name}"}


def run_agent(user_message, verified_user, conversation_history=[]):
    """
    Main agent function - handles the conversation flow with tool calling.

    Args:
        user_message (str): The user's message
        verified_user (dict): Current verified user information
        conversation_history (list): Previous conversation messages

    Returns:
        tuple: (response, updated_history, tool_calls_info)
            - response (str): The agent's final response
            - updated_history (list): Updated conversation messages
            - tool_calls_info (list): Tool calls made during conversation
    """

    # Build system message with user context
    system_message = SYSTEM_PROMPT
    if verified_user:
        system_message += f"\n\nCurrent user: {verified_user['first_name']} {verified_user['last_name']} (ID: {verified_user['id_number']})"

    messages = [{"role": "system", "content": system_message}]

    # Add previous conversation history
    messages.extend(conversation_history)

    # Add current user message
    messages.append({"role": "user", "content": user_message})

    # Main loop - allows multiple tool calls
    max_iterations = 5  # Prevent infinite loops
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Send request to OpenAI
        response = client.chat.completions.create(
            model="gpt-5",  # Use GPT-5 for better function calling
            messages=messages,
            tools=tools,
            tool_choice="auto"  # Let GPT decide when to use tools
        )

        # Get the assistant's message
        assistant_message = response.choices[0].message
        messages.append(assistant_message)  # Add to history

        # Check if GPT wants to call a tool
        if not assistant_message.tool_calls:
            # No more tool calls - return final answer
            # Extract tool calls from messages for display
            tool_calls_info = extract_tool_calls_from_messages(messages)
            return assistant_message.content, messages, tool_calls_info

        # GPT wants to call tools - process each one
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_arguments = json.loads(tool_call.function.arguments)

            # Execute the actual function
            tool_result = execute_tool_call(tool_name, tool_arguments, verified_user)

            # Add tool result to conversation
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": json.dumps(tool_result)
            })

    # If we exhausted max iterations without getting a final answer
    tool_calls_info = extract_tool_calls_from_messages(messages)
    return "I apologize, but I encountered an issue processing your request. Please try again.", messages, tool_calls_info


def extract_tool_calls_from_messages(messages):
    """
    Extract tool calls information from conversation messages for display.

    Args:
        messages (list): Conversation history

    Returns:
        list: List of tool call info dicts
    """
    tool_calls = []

    for msg in messages:
        # Convert to dict if it's an object (Pydantic model from OpenAI)
        if not isinstance(msg, dict):
            msg_dict = msg.model_dump() if hasattr(msg, 'model_dump') else {}
        else:
            msg_dict = msg

        # Look for assistant messages with tool_calls
        if msg_dict.get("role") == "assistant" and msg_dict.get("tool_calls"):
            for tool_call in msg_dict["tool_calls"]:
                # Convert tool_call to dict if needed
                if not isinstance(tool_call, dict):
                    tool_call_dict = tool_call.model_dump() if hasattr(tool_call, 'model_dump') else {}
                else:
                    tool_call_dict = tool_call

                tool_name = tool_call_dict.get("function", {}).get("name")
                tool_args_str = tool_call_dict.get("function", {}).get("arguments", "{}")

                try:
                    tool_args = json.loads(tool_args_str)
                except:
                    tool_args = {}

                # Find the corresponding tool result
                tool_result = None
                tool_id = tool_call_dict.get("id")

                # Search for the tool response
                for result_msg in messages:
                    # Convert to dict if needed
                    if not isinstance(result_msg, dict):
                        result_dict = result_msg.model_dump() if hasattr(result_msg, 'model_dump') else {}
                    else:
                        result_dict = result_msg

                    if result_dict.get("role") == "tool" and result_dict.get("tool_call_id") == tool_id:
                        tool_result = result_dict.get("content")
                        break

                tool_calls.append({
                    "name": tool_name,
                    "arguments": tool_args,
                    "result": tool_result
                })

    return tool_calls