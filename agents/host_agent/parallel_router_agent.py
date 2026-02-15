"""
BONUS Part B: Parallel Router Agent (+10 points)

This is an OPTIONAL bonus implementation that executes agents in parallel.

Architecture:
  Orchestrator (SequentialAgent)
    -> Parallel Worker (ParallelAgent)
         -> RemoteA2aAgent("customer_data") with output_key
         -> RemoteA2aAgent("support_specialist") with output_key
    -> Summary Agent (LLM Agent) -- synthesizes parallel results

Key concepts:
  - ParallelAgent runs sub-agents concurrently (faster than sequential)
  - output_key stores each agent's output in state for later access
  - Summary agent reads state and combines outputs into cohesive response

Requirements for bonus points:
  - RemoteA2aAgent with output_key configured (3 pts)
  - ParallelAgent correctly assembled (2 pts)
  - Summary agent with dynamic instruction reading state (3 pts)
  - Full orchestrator assembled correctly (2 pts)
"""

import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# IMPORTANT: Apply A2A compatibility patch
from shared import a2a_compat  # noqa: F401

from google.adk.agents import Agent, SequentialAgent, ParallelAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.agents.readonly_context import ReadonlyContext
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH
from shared.agents_config import (
    CUSTOMER_DATA_AGENT_URL,
    SUPPORT_AGENT_URL,
    GEMINI_MODEL,
)

logger = logging.getLogger(__name__)


# =============================================================================
# TODO BONUS: Summary Instruction Function
# =============================================================================

def create_summary_instruction(readonly_context: ReadonlyContext) -> str:
    """
    Create instruction for summary agent that combines parallel results.

    TODO: Implement this function to:
      1. Read customer_data_output from readonly_context.state
      2. Read support_specialist_output from readonly_context.state
      3. Return an instruction telling the LLM to synthesize both outputs

    Hints:
      - data_output = readonly_context.state.get("customer_data_output", "")
      - support_output = readonly_context.state.get("support_specialist_output", "")
      - Instruction should tell the LLM to combine outputs naturally
    """
    raise NotImplementedError("BONUS TODO: Implement create_summary_instruction")


# =============================================================================
# TODO BONUS: Create Parallel Agent
# =============================================================================

def create_agent():
    """
    Create a parallel router agent that executes agents concurrently.

    TODO: Assemble the full orchestrator:

      1. Create remote_customer_data (RemoteA2aAgent):
         - output_key='customer_data_output'

      2. Create remote_support (RemoteA2aAgent):
         - output_key='support_specialist_output'

      3. Create parallel_worker_agent (ParallelAgent):
         - sub_agents=[remote_customer_data, remote_support]

      4. Create summary_agent (Agent):
         - instruction=create_summary_instruction
         - include_contents='none'

      5. Create orchestrator (SequentialAgent):
         - sub_agents=[parallel_worker_agent, summary_agent]

    Returns:
        Configured SequentialAgent with parallel execution and synthesis
    """
    raise NotImplementedError(
        "BONUS TODO: Create the parallel router agent. "
        "See the docstring above for the architecture."
    )
