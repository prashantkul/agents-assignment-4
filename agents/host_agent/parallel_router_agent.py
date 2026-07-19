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
from google.adk.agents.callback_context import CallbackContext
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH
from shared.agents_config import (
    CUSTOMER_DATA_AGENT_URL,
    SUPPORT_AGENT_URL,
    GEMINI_MODEL,
)

logger = logging.getLogger(__name__)


# =============================================================================
# output_key workaround for RemoteA2aAgent
# =============================================================================
# The installed google-adk version only implements `output_key` on LlmAgent —
# RemoteA2aAgent's pydantic model forbids extra fields, so passing
# `output_key=...` directly raises a ValidationError. We reproduce the same
# behavior (store the agent's final response text under a state key) with an
# after_agent_callback, which is a publicly supported extension point on
# every BaseAgent subclass, including RemoteA2aAgent.
def _make_output_capture_callback(state_key: str):
    """Build an after_agent_callback that saves this agent's last response into state."""

    def _capture(callback_context: CallbackContext) -> None:
        session = callback_context._invocation_context.session
        for event in reversed(session.events):
            if event.author == callback_context.agent_name and event.content and event.content.parts:
                text = "".join(part.text or "" for part in event.content.parts)
                callback_context.state[state_key] = text
                break
        return None

    return _capture


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
    data_output = readonly_context.state.get("customer_data_output", "")
    support_output = readonly_context.state.get("support_specialist_output", "")

    return f"""
    You are the Summary Agent for a customer support system. Two specialist
    agents just ran in parallel to answer the user's request:

    Customer Data Agent output:
    {data_output or "(no data output produced)"}

    Support Agent output:
    {support_output or "(no support output produced)"}

    Combine these two results into a single, cohesive, natural response for the
    user. Do not mention that the results came from separate agents or that they
    ran in parallel — just present the combined information (account/ticket data
    plus troubleshooting guidance) as one coherent answer.
    """


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
    logger.info("[PARALLEL_ROUTER] Creating parallel router agent")

    remote_customer_data = RemoteA2aAgent(
        name='customer_data',
        description='Access customer and ticket data from MCP server',
        agent_card=f'{CUSTOMER_DATA_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}',
        after_agent_callback=_make_output_capture_callback('customer_data_output'),
    )

    remote_support = RemoteA2aAgent(
        name='support_specialist',
        description='Provide customer support and troubleshooting solutions',
        agent_card=f'{SUPPORT_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}',
        after_agent_callback=_make_output_capture_callback('support_specialist_output'),
    )

    parallel_worker_agent = ParallelAgent(
        name='parallel_worker',
        sub_agents=[remote_customer_data, remote_support],
    )

    summary_agent = Agent(
        model=GEMINI_MODEL,
        name='summary_agent',
        instruction=create_summary_instruction,
        include_contents='none',
    )

    return SequentialAgent(
        name='parallel_customer_support_host',
        sub_agents=[parallel_worker_agent, summary_agent],
    )
