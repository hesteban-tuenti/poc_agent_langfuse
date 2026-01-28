# Langfuse Tracing POC for Agentic AI Solutions

A proof-of-concept (POC) demonstrating how to implement and test traces in an agentic AI architecture using **Langfuse** and how to validate the information within the traces. This project showcases hierarchical tracing across multi-step agent interactions with tool calling.

## 🎯 Project Overview

This POC demonstrates:
- ✅ **Hierarchical trace capture** across agent sessions, LLM calls, and tool executions
- ✅ **OpenAI function calling** integration with simple, functional tools
- ✅ **Langfuse Cloud** integration for trace visualization and analysis
- ✅ **Multiple test scenarios** covering single-tool, multi-tool, and reasoning-only interactions
- ✅ **Trace metadata** including user IDs, session IDs, and custom tags

## 🏗️ Architecture

```
User Query
    ↓
run_agent() [@observe - Top Level Trace]
    ↓
    ├─→ call_llm() [@observe - LLM Interaction]
    │       ↓
    │   OpenAI API (gpt-4o-mini)
    │
    ├─→ execute_tool() [@observe - Tool Execution]
    │       ↓
    │   Tool Functions (calculate, get_current_time, get_random_fact)
    │
    └─→ Final Answer + Trace URL
```

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Langfuse Cloud account ([Sign up here](https://cloud.langfuse.com))

## 🚀 Setup Instructions

### 1. Clone and Navigate to the Project

```bash
cd <WORKSPACE>/agent-trace-langfuse
```

### 2. Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your actual API keys:

```bash
# OpenAI API Key
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-actual-openai-key

# Langfuse API Keys
# Sign up and get your keys from: https://cloud.langfuse.com
LANGFUSE_PUBLIC_KEY=pk-lf-your-actual-public-key
LANGFUSE_SECRET_KEY=sk-lf-your-actual-secret-key
LANGFUSE_HOST=https://cloud.langfuse.com
```


## 🧪 Running the Tests

### Run All Test Scenarios with Unittest

```bash
# Run all tests with live API calls
python test_poc_agent_langfuse.py

# Or using unittest directly
python -m unittest test_poc_agent_langfuse.py -v
```

### Test Modes

The test suite supports two modes via the `USE_MOCK` environment variable:

```bash
# Live mode (default) - Uses real OpenAI and Langfuse API calls
USE_MOCK=false python test_poc_agent_langfuse.py

# Mock mode - Uses predefined responses, no API calls but mocked LLM results are needed 
USE_MOCK=true python test_poc_agent_langfuse.py
```

### Test Scenarios Covered

1. **test_01_single_tool_usage** - Simple calculation (25 × 4)
   - Validates: 1 LLM call, 1 tool execution (`calculate`)
   
2. **test_02_multi_tool_usage** - Time + calculation (current time + 100 ÷ 5)
   - Validates: 2+ LLM calls, 2 tool executions (`get_current_time`, `calculate`)
   
3. **test_03_reasoning_without_tools** - Pure reasoning (explain quantum computing)
   - Validates: 1+ LLM call, 0 tool executions

### Trace Inspection

Each test automatically inspects traces using `inspect_trace()` which:
- Waits for traces to be available in Langfuse (up to 30 seconds)
- Extracts and categorizes observations by type (`AGENT`, `TOOL`)
- Validates expected LLM calls and tool executions
- Prints trace structure and URLs for manual inspection

### Run Specific Tests

```bash
# Run a single test
python -m unittest test_poc_agent_langfuse.TestLangfuseTracing.test_01_single_tool_usage

# Run with mock mode
USE_MOCK=true python -m unittest test_poc_agent_langfuse.TestLangfuseTracing.test_01_single_tool_usage
```

### Quick Agent Test

Test the agent directly without unittest:

```bash
python poc_agent.py
```

## 📊 Viewing Traces in Langfuse

After running tests:

1. Open [Langfuse Cloud Dashboard](https://cloud.langfuse.com)
2. Navigate to **"Traces"** in the sidebar
3. You'll see your test runs with metadata:
   - User ID: `test_user_1`, `test_user_2`, etc.
   - Session IDs: `test_single_tool`, `test_multi_tool`, etc.
   - Tags: `poc`, `agent`, `openai`

4. Click on any trace to inspect:
   - **Hierarchical structure** of the agent execution
   - **LLM inputs/outputs** at each step
   - **Tool calls** with arguments and results
   - **Timing and latency** for each operation
   - **Token usage** and costs

### Example Trace Structure

```
📊 run_agent (session trace)
   ├─ 🤖 call_llm (initial user query)
   ├─ 🔧 execute_tool (calculate: "25 * 4")
   ├─ 🤖 call_llm (process tool result)
   └─ ✅ Final Answer: "100"
```

## 📁 Project Structure

```
agent-trace-langfuse/
├── .env                          # Environment variables (not in git)
├── .env.example                  # Template for environment variables
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── README.md                     # This file
│
├── tools.py                      # Tool definitions and implementations
│   ├── calculate()              # Mathematical expression evaluator
│   ├── get_current_time()       # Current datetime retriever
│   ├── get_random_fact()        # Random fact generator
│   └── TOOL_DEFINITIONS         # OpenAI function calling schemas
│
├── poc_agent.py                  # Main agent implementation
│   ├── call_llm()               # LLM interaction with tracing
│   ├── execute_tool()           # Tool execution with tracing
│   └── run_agent()              # Top-level agent loop with tracing
│
└── test_traces.py                # Test scenarios
    ├── test_single_tool_usage()
    ├── test_multi_tool_usage()
    ├── test_reasoning_without_tools()
    └── test_complex_multi_step()
```

## 🔧 Tools Available

### 1. `calculate(expression: str)`
Evaluates mathematical expressions.

**Example:**
```python
calculate("25 * 4")  # Returns: 100
calculate("(100 + 50) / 2")  # Returns: 75
```

### 2. `get_current_time(timezone: str = "UTC")`
Returns current date and time in multiple formats.

**Example:**
```python
get_current_time()  
# Returns: ISO datetime, date, time, formatted string
```

### 3. `get_random_fact(category: str = "general")`
Returns a random fact from predefined categories.

**Categories:** `general`, `science`, `history`, `tech`

**Example:**
```python
get_random_fact("science")
# Returns: A random science fact
```


## 🔄 Next Steps / Enhancements

This POC can be extended with:

- ✨ **More complex tools** (API calls, database queries, file operations)
- ✨ **Error handling traces** (failed tool calls, API errors, timeouts)
- ✨ **Nested agent calls** (agents calling other agents)
- ✨ **LiteLLM integration** (multi-provider support)
- ✨ **Async execution** (parallel tool calls, improved performance)
- ✨ **Evaluation metrics** (response quality, tool selection accuracy)
- ✨ **Cost tracking** (per-session cost analysis in Langfuse)
- ✨ **A/B testing** (compare different prompts or models)

## 📚 Resources

- [Langfuse Documentation](https://langfuse.com/docs)
- [Langfuse Python SDK](https://langfuse.com/docs/sdk/python)
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [OpenAI Python SDK](https://github.com/openai/openai-python)

