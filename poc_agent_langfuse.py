"""
Agent implementation with Langfuse tracing.
Demonstrates how to trace an agentic workflow using OpenAI function calling.
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from langfuse import observe, get_client
from tools import TOOL_DEFINITIONS, TOOL_FUNCTIONS
from random import randint

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
langfuse = get_client()

# Verify Langfuse connection
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")


@observe(as_type="agent")
def call_llm(messages: list, tools: list = None, tool_choice: str = "auto") -> dict:
    """
    Calls the OpenAI LLM with the given messages and tools.
    This function is decorated with @observe() to trace each LLM call.
    
    Args:
        messages: List of message dictionaries for the conversation
        tools: List of tool definitions (optional)
        tool_choice: How the model should choose tools ("auto", "none", or specific tool)
    
    Returns:
        The API response as a dictionary
    """
    kwargs = {
        "model": "gpt-4o-mini",
        "messages": messages,
    }
    
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = tool_choice
    
    response = client.chat.completions.create(**kwargs)
    
    return response


@observe()
def execute_tool(tool_name: str, tool_arguments: dict) -> dict:
    """
    Executes a tool by name with the given arguments.
    This function is decorated with @observe() to trace tool executions.
    
    Args:
        tool_name: Name of the tool to execute
        tool_arguments: Dictionary of arguments to pass to the tool
    
    Returns:
        The result from the tool execution
    """
    if tool_name not in TOOL_FUNCTIONS:
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}"
        }
    
    tool_function = TOOL_FUNCTIONS[tool_name]
    
    try:
        result = tool_function(**tool_arguments)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"Tool execution failed: {str(e)}"
        }


@observe()
def run_agent(user_query: str, user_id: str = "test_user", session_id: str = None, max_iterations: int = 10) -> dict:
    """
    Runs the agent loop to answer a user query.
    This is the top-level function decorated with @observe() to trace the entire agent session.
    
    Args:
        user_query: The user's question or request
        user_id: Identifier for the user (for tracing)
        session_id: Identifier for the session (for tracing)
        max_iterations: Maximum number of agent iterations to prevent infinite loops
    
    Returns:
        A dictionary containing the final answer and trace information
    """
    # Update trace context with metadata
    if session_id is None:
        import uuid
        session_id = str(uuid.uuid4())[:8]
    
    langfuse.update_current_trace(
        user_id=user_id,
        session_id=session_id,
        tags=["poc", "agent", "openai"],
        metadata={
            "model": "gpt-4o-mini",
            "max_iterations": max_iterations
        }
    )
    
    # Initialize conversation with system message
    messages = [
        {
            "role": "system",
            "content": """You are a helpful AI assistant with access to tools. 
Use the available tools when needed to answer user questions accurately.
When you have enough information to answer the user's question, always be accurate. If you don't know the answer, say so."""
        },
        {
            "role": "user",
            "content": user_query
        }
    ]
    
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        # Call the LLM
        response = call_llm(messages=messages, tools=TOOL_DEFINITIONS)
        
        assistant_message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason
        
        # Add assistant's response to messages
        messages.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": assistant_message.tool_calls
        })
        
        # Check if the model wants to call tools
        if finish_reason == "tool_calls" and assistant_message.tool_calls:
            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_arguments = json.loads(tool_call.function.arguments)
                
                print(f"[Agent] Calling tool: {tool_name} with args: {tool_arguments}")
                
                # Execute the tool
                tool_result = execute_tool(tool_name, tool_arguments)
                
                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps(tool_result)
                })
            
            # Continue the loop to let the model process tool results
            continue
        
        # If we reach here, the model has provided a final answer
        if finish_reason == "stop":
            final_answer = assistant_message.content
            
            # Get trace ID and URL from Langfuse context
            trace_id = langfuse.get_current_trace_id()
            trace_url = langfuse.get_trace_url()
            
            return {
                "success": True,
                "answer": final_answer,
                "iterations": iteration,
                "trace_url": trace_url,
                "trace_id": trace_id,
                "session_id": session_id
            }
    
    # Max iterations reached
    return {
        "success": False,
        "error": "Maximum iterations reached without conclusive answer",
        "iterations": iteration,
        "trace_url": langfuse.get_trace_url(),
        "trace_id": langfuse.get_current_trace_id(),
        "session_id": session_id
    }


if __name__ == "__main__":
    
    user_prompts = [
        "What is 25 multiplied by 4?",
        "What time is it right now? Also, can you calculate what 100 divided by 5 is?",
        "Tell me an interesting science fact, then calculate how many hours are in a week (7 * 24)."
    ]
    
    # Quick test
    print("Running a quick test of the agent...")
    print("-" * 60)
    
    random_index_user_prompts = randint(0, len(user_prompts) - 1)
    result = run_agent(user_prompts[random_index_user_prompts])  # Random prompt from the list
    
    print(f"\n[Result] Success: {result['success']}")
    print(f"[Result] Answer: {result['answer']}")
    print(f"[Result] Iterations: {result['iterations']}")
    print(f"[Result] Trace URL: {result['trace_url']}")
    print(f"[Result] Trace ID: {result['trace_id']}")
    print(f"[Result] Session ID: {result['session_id']}")

    print("-" * 60)
    print("Printing full result for testing purposes:")
    print(result)
