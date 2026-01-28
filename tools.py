"""
Simple tools for the agent to use.
Each tool is decorated with @observe() for automatic Langfuse tracing.
"""

from datetime import datetime
import random
from langfuse import observe


@observe(as_type="tool")
def calculate(expression: str) -> dict:
    """
    Evaluates a mathematical expression and returns the result.
    
    Args:
        expression: A string containing a mathematical expression (e.g., "25 * 4", "100 / 5")
    
    Returns:
        A dictionary with the result or error message
    """
    try:
        # Using eval with restricted globals for safety (POC only - don't use in production)
        allowed_names = {"__builtins__": {}}
        result = eval(expression, allowed_names)
        return {
            "success": True,
            "expression": expression,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "expression": expression,
            "error": str(e)
        }


@observe(as_type="tool")
def get_current_time(timezone: str = "UTC") -> dict:
    """
    Gets the current date and time.
    
    Args:
        timezone: Timezone name (default: UTC). For POC, only UTC is supported.
    
    Returns:
        A dictionary with the current datetime information
    """
    now = datetime.now()
    return {
        "success": True,
        "timezone": timezone,
        "datetime": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "formatted": now.strftime("%B %d, %Y at %I:%M:%S %p")
    }


@observe(as_type="tool")
def get_random_fact(category: str = "general") -> dict:
    """
    Returns a random interesting fact from a predefined list.
    
    Args:
        category: Category of fact (general, science, history, tech)
    
    Returns:
        A dictionary with a random fact
    """
    facts = {
        "general": [
            "Honey never spoils. Archaeologists have found 3000-year-old honey in Egyptian tombs that was still edible.",
            "A group of flamingos is called a 'flamboyance'.",
            "Bananas are berries, but strawberries aren't.",
            "The shortest war in history lasted 38 minutes between Britain and Zanzibar in 1896."
        ],
        "science": [
            "Water can boil and freeze at the same time in a phenomenon called the triple point.",
            "A single bolt of lightning contains enough energy to toast 100,000 slices of bread.",
            "Your body contains about 37.2 trillion cells.",
            "Sound travels 4.3 times faster in water than in air."
        ],
        "history": [
            "Cleopatra lived closer in time to the moon landing than to the construction of the Great Pyramid.",
            "Oxford University is older than the Aztec Empire.",
            "The Great Wall of China is not visible from space with the naked eye.",
            "Nintendo was founded in 1889 as a playing card company."
        ],
        "tech": [
            "The first computer mouse was made of wood in 1964.",
            "The first 1GB hard drive weighed over 500 pounds and cost $40,000 in 1980.",
            "Email existed before the World Wide Web.",
            "The first webcam was created to monitor a coffee pot at Cambridge University."
        ]
    }
    
    # Default to general if category not found
    category = category.lower()
    if category not in facts:
        category = "general"
    
    fact = random.choice(facts[category])
    
    return {
        "success": True,
        "category": category,
        "fact": fact
    }


# Tool definitions for OpenAI function calling
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluates a mathematical expression and returns the result. Supports basic arithmetic operations: addition (+), subtraction (-), multiplication (*), division (/), and parentheses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate (e.g., '25 * 4', '(100 + 50) / 2')"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Gets the current date and time. Returns datetime in various formats including ISO format, date, time, and human-readable format.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "The timezone name (default: UTC). For this POC, only UTC is supported.",
                        "default": "UTC"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_random_fact",
            "description": "Returns a random interesting fact from a predefined collection. Facts are categorized by topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "The category of fact to retrieve",
                        "enum": ["general", "science", "history", "tech"],
                        "default": "general"
                    }
                },
                "required": []
            }
        }
    }
]


# Map tool names to functions for execution
TOOL_FUNCTIONS = {
    "calculate": calculate,
    "get_current_time": get_current_time,
    "get_random_fact": get_random_fact
}
