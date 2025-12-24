"""
Tools definition for OpenAI Function Calling.
This file defines what functions the AI agent can call and how to use them.
"""

tools = [
    # Tool 1: Check if medication exists
    {
        "type": "function",
        "function": {
            "name": "medication_exists",
            "description": "Check if a medication exists in the pharmacy database by searching its name in English or Hebrew. Returns the medication details including its ID if found.",
            "parameters": {
                "type": "object",
                "properties": {
                    "medication_name": {
                        "type": "string",
                        "description": "The name of the medication to search for. Can be in English (e.g., 'Acamol') or Hebrew (e.g., 'אקמול')."
                    }
                },
                "required": ["medication_name"]
            }
        }
    },

    # Tool 2: Get medication availability (stock + price)
    {
        "type": "function",
        "function": {
            "name": "get_medication_availability",
            "description": "Get the availability and price of a medication using its database ID. Use this AFTER calling medication_exists to get the ID. Returns: 'found' (bool), 'in_stock' (bool), 'stock_quantity' (int), and 'price' (float in Israeli Shekels ₪). Does NOT return medication ID or names - the agent already has this information from medication_exists.",
            "parameters": {
                "type": "object",
                "properties": {
                    "medication_id": {
                        "type": "integer",
                        "description": "The unique database ID of the medication (obtained from medication_exists function)."
                    }
                },
                "required": ["medication_id"]
            }
        }
    },

    # Tool 3: Get medication profile (leaflet info)
    {
        "type": "function",
        "function": {
            "name": "get_medication_profile",
            "description": "Get detailed medical information from the medication leaflet using its database ID. Use this AFTER calling medication_exists to get the ID. Returns: 'found' (bool), 'requires_prescription' (bool), 'can_access' (bool), and if accessible: 'active_ingredients', 'dosage_instructions', 'usage_instructions', 'factual_info'. For prescription medications, automatically checks user's prescription status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "medication_id": {
                        "type": "integer",
                        "description": "The unique database ID of the medication (obtained from medication_exists function)."
                    }
                },
                "required": ["medication_id"]
            }
        }
    }
]

# Helper function to get tool by name
def get_tool_by_name(tool_name):
    """
    Retrieve a tool definition by its name.

    Args:
        tool_name (str): Name of the tool function

    Returns:
        dict: Tool definition or None if not found
    """
    for tool in tools:
        if tool["function"]["name"] == tool_name:
            return tool
    return None


# Display available tools (for debugging)
if __name__ == "__main__":
    print("Available Tools:\n")
    for i, tool in enumerate(tools, 1):
        func = tool["function"]
        print(f"{i}. {func['name']}")
        print(f"   Description: {func['description']}")
        print(f"   Parameters: {list(func['parameters']['properties'].keys())}")
        print()