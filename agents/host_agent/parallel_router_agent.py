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

from typing import Optional

from google.adk.agents import Agent, SequentialAgent, ParallelAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
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

    Reads each parallel agent's captured output from session state and returns
    an instruction that asks the LLM to merge them into one cohesive reply.
    """
    data_output = readonly_context.state.get("customer_data_output", "") or "(no data returned)"
    support_output = readonly_context.state.get("support_specialist_output", "") or "(no support response)"

    return (
        "You are the response synthesizer for a customer support system. Two "
        "specialist agents ran in parallel on the same request. Combine their "
        "outputs into a single, cohesive, well-organized reply for the "
        "customer. Lead with the account/data context, then the support "
        "guidance. Remove redundancy, keep a warm and professional tone, and "
        "do not mention that separate agents produced these parts.\n\n"
        f"--- CUSTOMER DATA AGENT OUTPUT ---\n{data_output}\n\n"
        f"--- SUPPORT AGENT OUTPUT ---\n{support_output}\n\n"
        "Now write the unified response:"
    )


def _make_output_capture(state_key: str):
    """Build an after_agent_callback that stores a sub-agent's output in state.

    RemoteA2aAgent has no `output_key` field (it subclasses BaseAgent, not
    LlmAgent), so we capture the agent's final text from the session events it
    just produced and write it to state under `state_key`. This is the working
    equivalent of output_key for a remote A2A agent, and it lets the downstream
    summary agent read both parallel results from state.
    """
    def after_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
        text = ""
        try:
            for event in reversed(callback_context.session.events or []):
                if getattr(event, "author", None) != callback_context.agent_name:
                    continue
                content = getattr(event, "content", None)
                parts = getattr(content, "parts", None) if content else None
                if parts:
                    text = " ".join((getattr(p, "text", None) or "") for p in parts).strip()
                    if text:
                        break
            callback_context.state[state_key] = text
            logger.info("[PARALLEL] captured %s (%d chars)", state_key, len(text))
        except Exception as e:  # never let capture crash the run
            logger.warning("[PARALLEL] capture failed for %s: %s", state_key, e)
            callback_context.state[state_key] = ""
        return None

    return after_agent_callback


# =============================================================================
# TODO BONUS: Create Parallel Agent
# =============================================================================

def create_agent():
    """
    Create a parallel router agent that executes agents concurrently.

    Structure:
        orchestrator (SequentialAgent)
          - parallel_worker (ParallelAgent): runs both remotes concurrently,
            each capturing its output into state via an after_agent_callback
            (the working stand-in for output_key on a RemoteA2aAgent).
          - summary_agent (LlmAgent): reads both outputs from state (via
            create_summary_instruction) and synthesizes one reply.

    Returns:
        Configured SequentialAgent with parallel execution and synthesis.
    """
    remote_customer_data = RemoteA2aAgent(
        name="customer_data",
        description="Access customer and ticket data from MCP server",
        agent_card=f"{CUSTOMER_DATA_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
        after_agent_callback=_make_output_capture("customer_data_output"),
    )

    remote_support = RemoteA2aAgent(
        name="support_specialist",
        description="Provide customer support and troubleshooting solutions",
        agent_card=f"{SUPPORT_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
        after_agent_callback=_make_output_capture("support_specialist_output"),
    )

    parallel_worker_agent = ParallelAgent(
        name="parallel_worker",
        description="Runs the data and support agents concurrently.",
        sub_agents=[remote_customer_data, remote_support],
    )

    # include_contents='none': the summary agent should synthesize ONLY from the
    # two captured outputs we inject via its instruction, not from the raw
    # conversation history.
    summary_agent = Agent(
        model=GEMINI_MODEL,
        name="summary",
        description="Synthesizes the parallel agents' outputs into one reply.",
        instruction=create_summary_instruction,
        include_contents="none",
    )

    logger.info("Creating PARALLEL router agent (parallel worker -> summary)")
    return SequentialAgent(
        name="parallel_customer_support_host",
        description=(
            "Parallel orchestrator: runs the data and support agents at the "
            "same time over A2A, then synthesizes their results."
        ),
        sub_agents=[parallel_worker_agent, summary_agent],
    )
