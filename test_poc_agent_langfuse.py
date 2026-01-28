"""
Enhanced test scenarios with trace inspection capabilities using unittest framework.
Run with: python -m unittest improved_test_traces.py
Or with verbose output: python -m unittest improved_test_traces.py -v
"""

import unittest
from unittest.mock import Mock, MagicMock
import time
import os
from dotenv import load_dotenv
from langfuse import Langfuse
from poc_agent_langfuse import run_agent

# Load environment variables
load_dotenv()

# Configuration: Set to True to use mocks, False to use real run_agent
USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"


# To complete the mocks, just run the poc_agent_langufuse and save the result
mocked_result_test_1 = {'success': True, 
                        'answer': '25 multiplied by 4 is 100.', 
                        'iterations': 2, 
                        'trace_url': '',
                        'trace_id': '',
                        'session_id': '' }


mocked_result_test_2 = {'success': True, 
                        'answer': 'The current time is **1:21:04 PM** (UTC) on **January 27, 2026**. \n\nAdditionally, the result of \\( 100 \\div 5 \\) is **20**.', 
                        'iterations': 2, 
                        'trace_url': '',
                        'trace_id': '',
                        'session_id': '' }

mocked_result_test_3 = {'success': True, 
                        'answer': 'Quantum computing is a type of computing that uses the principles of quantum mechanics to process information in ways that are fundamentally different from classical computers, allowing it to solve certain problems much faster. It uses quantum bits, or qubits, which can represent multiple states simultaneously.',
                        'iterations': 1, 
                        'trace_url': '',
                        'trace_id': '',
                        'session_id': '' }


# Initialize Langfuse client for trace inspection
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
)


def inspect_trace(trace_id: str, max_wait: int = 30):
    """
    Inspects a trace and returns detailed information about its structure.
    
    Args:
        trace_id: The ID of the trace to inspect
        max_wait: Maximum seconds to wait for trace to be available
    
    Returns:
        Dictionary with trace inspection results or None if trace not available
    """
    # Wait for trace to be available (async processing)
    for i in range(max_wait):
        try:
            trace = langfuse.api.trace.get(trace_id=trace_id)
            # print(trace)
            break
        except Exception as e:
            #print exception for information
            print(f"Waiting for trace {trace_id} to be available... ({i+1}/{max_wait})")
            if i < max_wait - 1:
                time.sleep(1)
            else:
                return None
    
    # Extract observations (spans) from the trace
    observations = trace.observations if hasattr(trace, 'observations') else []
    
    inspection = {
        "trace_id": trace_id,
        "total_observations": len(observations),
        "observation_types": {},
        "llm_calls": [],
        "tool_calls": []
        
    }
    
    for obs in observations:
        obs_type = obs.type if hasattr(obs, 'type') else 'unknown'
        obs_name = obs.name if hasattr(obs, 'name') else 'unnamed'
        
        # Count by type
        inspection["observation_types"][obs_type] = inspection["observation_types"].get(obs_type, 0) + 1
        
        # Categorize by type
        if obs_type == "AGENT":
            inspection["llm_calls"].append({
                "id": obs.id,
                "name": obs_name,
                "type": obs_type
            })
        elif obs_type == "TOOL":
            inspection["tool_calls"].append({
                "id": obs.id,
                "name": obs_name,
                "type": obs_type
            })
    
    if inspection:
            print(f"✓ Total observations: {inspection['total_observations']}")
            print(f"✓ LLM calls: {len(inspection['llm_calls'])}")
            print(f"✓ Tool calls: {len(inspection['tool_calls'])}")
            
    else:
        print("⚠️  Trace not yet available (check dashboard later)")
    
    return inspection


class TestLangfuseTracing(unittest.TestCase):
    """
    Test suite for validating Langfuse tracing in agentic workflows.
    Each test demonstrates different agent behaviors and trace patterns.
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up test suite - runs once before all tests."""
        # Configure whether to use mock or real run_agent
        if USE_MOCK:
            cls.run_agent = MagicMock()
            cls.use_mock = True
            print("\n" + "🧪" + "*" * 35)
            print("  LANGFUSE TRACING POC - UNITTEST SUITE (MOCK MODE)")
            print("🧪" + "*"  * 35)
            print("\nRunning tests with mocked agent responses...\n")
        else:
            cls.run_agent = staticmethod(run_agent)
            cls.use_mock = False
            print("\n" + "🚀" + "*" * 35)
            print("  LANGFUSE TRACING POC - UNITTEST SUITE (LIVE MODE)")
            print("🚀" + "*"  * 35)
            print("\nValidating Langfuse trace instrumentation in agentic workflows...\n")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests - runs once after all tests."""
        print("\n" + "=" * 70)
        print("\n🎯 All tests completed!")
        print("  ✓ Traces validated for correct instrumentation")
        print("  ✓ Check Langfuse dashboard for detailed trace inspection")
        print(f"  ✓ Dashboard: https://cloud.langfuse.com")
        print("\n" + "=" * 70 + "\n")
        
        # Flush Langfuse to ensure all traces are sent
        langfuse.flush()
    
    def setUp(self):
        """Set up before each test."""
        # Small delay between tests to avoid rate limiting
        time.sleep(1)
    
    def _run_agent(self, query: str, user_id: str, session_id: str):
        """
        Helper method to run agent.
        
        Args:
            query: User query to send to agent
            user_id: User identifier
            session_id: Session identifier
        
        Returns:
            Tuple of (result, inspection)
        """
        
        # Run agent
        result = self.run_agent(
            user_query=query,
            user_id=user_id,
            session_id=session_id
        )
        # print(result)
        
        # Basic assertions
        self.assertTrue(result['success'], "Agent should complete successfully")
        self.assertIsNotNone(result['answer'], "Agent should provide an answer")
        self.assertIn('trace_id', result, "Result should contain trace_id")
        self.assertIn('trace_url', result, "Result should contain trace_url")
        
        print(f"\n✓ Query: {query}")
        print(f"✓ Answer: {result['answer'][:100]}...")
        print(f"✓ Iterations: {result['iterations']}")
        print(f"✓ Trace URL: {result['trace_url']}")
        

        return result
    
    def test_01_single_tool_usage(self):
        """
        Test Case 1: Single Tool Usage
        
        Validates that:
        - Agent correctly identifies when to use a tool
        - Single tool call is traced properly
        - Agent provides final answer based on tool results
        
        Expected: 1+ LLM call, 1 tool execution
        """
        print("\n **** TEST 1: Single Tool Usage - Simple Calculation")
        query = "What is 25 multiplied by 4?"

        if USE_MOCK:
            self.run_agent.return_value = mocked_result_test_1

        result = self._run_agent(
            query=query,
            user_id="test_user_1",
            session_id="test_single_tool",
        )

        inspection = inspect_trace(result["trace_id"])
        
        # Verify answer makes sense (should mention 100)
        self.assertIn("100", result['answer'], "Answer should contain the result 100")
        self.assertGreaterEqual(len(inspection['llm_calls']), 1, 
                                   "Should have at least 1 LLM call")
        self.assertEqual(len(inspection['tool_calls']), 1,
                                   "Should have exactly 1 tool execution")
        self.assertEqual(inspection["tool_calls"][0]["name"], "calculate", 
                                    "Executed tool should be 'calculate'")  
            
    
    def test_02_multi_tool_usage(self):
        """
        Test Case 2: Multi-Step Task with Multiple Tools
        
        Validates that:
        - Agent can use multiple tools in sequence
        - Each tool call is traced as a separate span
        - Agent synthesizes information from multiple tool results
        
        Expected: 2+ LLM calls, 2+ tool executions
        """
        print("\n **** TEST 2: Multi-Tool Usage - Time and Calculation")
        query = "What time is it right now? Also, can you calculate what 100 divided by 5 is?"
        
        if USE_MOCK:
            self.run_agent.return_value = mocked_result_test_2

        result = self._run_agent(
            query=query,
            user_id="test_user_2",
            session_id="test_multi_tool",
        )

        inspection = inspect_trace(result["trace_id"])
        
        
        # Verify answer addresses both questions
        self.assertTrue(
            "January" in result['answer'] and "20" in result['answer'],
            "Answer should contain date and calculation result"
        )

        self.assertGreaterEqual(len(inspection['llm_calls']), 2, 
                                   "Should have at least 2 LLM call")
        self.assertEqual(len(inspection['tool_calls']), 2,
                                   "Should have exactly 2 tool execution")
        
        
        tools_called = [item["name"] for item in inspection["tool_calls"] ]

        self.assertCountEqual(tools_called, ["calculate", "get_current_time"])

    
    def test_03_reasoning_without_tools(self):
        """
        Test Case 3: Pure Reasoning (No Tools)
        
        Validates that:
        - Agent can answer questions without using tools
        - Traces still capture the LLM interaction
        - Agent knows when tools are not necessary
        
        Expected: 1+ LLM call, 0 tool executions
        """
        print("\n **** TEST 3: No Tool Usage ")
        query = "Explain what quantum computing is in simple terms. No more than 2 lines"

        if USE_MOCK:
            self.run_agent.return_value = mocked_result_test_3

        result = self._run_agent(
            query=query,
            user_id="test_user_3",
            session_id="test_no_tools",
        )

        inspection = inspect_trace(result["trace_id"])

        
        # Verify answer mentions quantum computing
        self.assertTrue(
            "quantum" in result['answer'].lower(),
            "Answer should mention quantum computing"
        )

        self.assertEqual(len(inspection['tool_calls']), 0,
                                   "Should have exactly 0 tool execution")



def print_test_summary():
    """Custom test runner with summary."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestLangfuseTracing))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"\n📊 Test Results Summary:")
    print(f"  • Tests run: {result.testsRun}")
    print(f"  • Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  • Failures: {len(result.failures)}")
    print(f"  • Errors: {len(result.errors)}")
    print("\n" + "=" * 70)
    
    return result


if __name__ == "__main__":
    # Run with custom summary
    print_test_summary()