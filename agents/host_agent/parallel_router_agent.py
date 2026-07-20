"""
BONUS Part B: Parallel Router Agent (+10 points)

This is an OPTIONAL bonus implementation that executes agents in parallel.

Architecture:
  Orchestrator (SequentialAgent)
    -> Parallel Worker (ParallelAgent)
         -> RemoteA2aAgent("customer_data") with after_agent_callback saving output
         -> RemoteA2aAgent("support_specialist") with after_agent_callback saving output
    -> Summary Agent (LLM Agent) -- synthesizes parallel results

Key concepts:
  - ParallelAgent runs sub-agents concurrently (faster than sequential)
  - Each remote agent's after_agent_callback stores its own response text in
    session state for later access (RemoteA2aAgent doesn't support the
    LlmAgent-only `output_key` field, so we save it manually)
  - Summary agent reads state and combines outputs into cohesive response

Requirements for bonus points:
  - Each remote agent's output captured into state (3 pts)
  - ParallelAgent correctly assembled (2 pts)
  - Summary agent with dynamic instruction reading state (3 pts)
  - Full orchestrator assembled correctly (2 pts)
"""

import sys
import os
import logging
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# IMPORTANT: Apply A2A compatibility patch
from shared import a2a_compat  # noqa: F401

from google.adk.agents import Agent, SequentialAgent, ParallelAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.genai import types
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH
from shared.agents_config import (
    CUSTOMER_DATA_AGENT_URL,
    SUPPORT_AGENT_URL,
    GEMINI_MODEL,
)

logger = logging.getLogger(__name__)

CUSTOMER_DATA_OUTPUT_KEY = 'customer_data_output'
SUPPORT_OUTPUT_KEY = 'support_specialist_output'


def _make_output_saver(agent_name: str, state_key: str):
    """Build an after_agent_callback that saves `agent_name`'s last response
    text into session state under `state_key`.

    RemoteA2aAgent has no built-in output_key (that field only exists on
    LlmAgent), so we capture the agent's final response ourselves by
    scanning the session's events for the most recent one it authored.
    """

    def save_output(callback_context: CallbackContext) -> Optional[types.Content]:
        for event in reversed(callback_context.session.events):
            if event.author != agent_name or not event.content:
                continue
            text = ''.join(
                part.text for part in event.content.parts or [] if part.text
            )
            if text:
                callback_context.state[state_key] = text
                break
        return None

    return save_output


# =============================================================================
# Summary Instruction Function
# =============================================================================

def create_summary_instruction(readonly_context: ReadonlyContext) -> str:
    """
    Create instruction for summary agent that combines parallel results.
    """
    data_output = readonly_context.state.get(CUSTOMER_DATA_OUTPUT_KEY, "")
    support_output = readonly_context.state.get(SUPPORT_OUTPUT_KEY, "")

    return f"""
You are the Summary Agent for a customer support system. Two specialist
agents just ran in parallel to answer the user's request. Combine their
results into one clear, cohesive response.

Customer Data Agent output:
---
{data_output or "(no output — this agent did not produce a response)"}
---

Support Agent output:
---
{support_output or "(no output — this agent did not produce a response)"}
---

Synthesize both outputs into a single natural response. Do not mention that
the information came from separate agents or that they ran in parallel —
just present the combined answer as one coherent reply to the user.
""".strip()


# =============================================================================
# Create Parallel Agent
# =============================================================================

def create_agent():
    """
    Create a parallel router agent that executes agents concurrently.

    Returns:
        Configured SequentialAgent with parallel execution and synthesis
    """
    remote_customer_data = RemoteA2aAgent(
        name='customer_data',
        description='Access customer and ticket data from MCP server',
        agent_card=f'{CUSTOMER_DATA_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}',
        after_agent_callback=_make_output_saver('customer_data', CUSTOMER_DATA_OUTPUT_KEY),
    )

    remote_support = RemoteA2aAgent(
        name='support_specialist',
        description='Provide customer support and troubleshooting solutions',
        agent_card=f'{SUPPORT_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}',
        after_agent_callback=_make_output_saver('support_specialist', SUPPORT_OUTPUT_KEY),
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
        name='customer_support_host_parallel',
        sub_agents=[parallel_worker_agent, summary_agent],
    )
