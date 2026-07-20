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
# Summary Instruction
# =============================================================================

def create_summary_instruction(readonly_context: ReadonlyContext) -> str:
    """Build an instruction that synthesizes both parallel worker outputs."""
    data_output = readonly_context.state.get("customer_data_output", "")
    support_output = readonly_context.state.get(
        "support_specialist_output", ""
    )

    return f"""
    You are the final response synthesizer for a customer-support workflow.
    Combine the two worker results below into one accurate, empathetic, and
    concise response to the user's original request.

    Customer Data Agent result:
    {data_output or "No customer data result was returned."}

    Support Agent result:
    {support_output or "No support result was returned."}

    Reconcile duplication, preserve useful customer and ticket identifiers,
    and organize next steps clearly. Do not invent facts or claim an action
    succeeded unless a worker result confirms it. If a worker failed or
    returned no result, acknowledge the limitation gracefully.
    """


# =============================================================================
# Parallel Agent Factory
# =============================================================================

def create_agent() -> SequentialAgent:
    """Create a parallel worker orchestrator with response synthesis."""
    remote_customer_data = RemoteA2aAgent(
        name="customer_data",
        description="Access customer and ticket data from MCP server",
        agent_card=(
            f"{CUSTOMER_DATA_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}"
        ),
        output_key="customer_data_output",
    )

    remote_support = RemoteA2aAgent(
        name="support_specialist",
        description="Provide customer support and troubleshooting solutions",
        agent_card=f"{SUPPORT_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
        output_key="support_specialist_output",
    )

    parallel_worker_agent = ParallelAgent(
        name="parallel_support_workers",
        description="Runs customer data and support specialists concurrently",
        sub_agents=[remote_customer_data, remote_support],
    )

    summary_agent = Agent(
        model=GEMINI_MODEL,
        name="support_response_synthesizer",
        description="Combines parallel worker results into a single response",
        instruction=create_summary_instruction,
        include_contents="none",
    )

    return SequentialAgent(
        name="parallel_customer_support_host",
        description=(
            "Runs remote support workers concurrently and synthesizes results"
        ),
        sub_agents=[parallel_worker_agent, summary_agent],
    )
