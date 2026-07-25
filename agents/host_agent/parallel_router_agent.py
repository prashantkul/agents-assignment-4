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
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [PARALLEL_ROUTER] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

CUSTOMER_DATA_OUTPUT_KEY = 'customer_data_output'
SUPPORT_OUTPUT_KEY = 'support_specialist_output'


def _extract_agent_output(callback_context: CallbackContext, agent_name: str) -> str:
    """Extract the latest text response from an agent's events."""
    for event in reversed(callback_context.session.events):
        if event.author != agent_name or not event.content or not event.content.parts:
            continue
        parts = [
            part.text for part in event.content.parts
            if part.text and not getattr(part, 'thought', False)
        ]
        if parts:
            return ''.join(parts)
    return ''


def _make_output_key_callback(output_key: str):
    """Store agent output in session state under output_key after execution."""
    def store_output(callback_context: CallbackContext) -> Optional[types.Content]:
        output_text = _extract_agent_output(callback_context, callback_context.agent_name)
        if output_text:
            callback_context.state[output_key] = output_text
            logger.info("Stored output in state key '%s'", output_key)
        return None

    return store_output


def _create_parallel_remote_agent(
    name: str,
    description: str,
    agent_card: str,
    output_key: str,
) -> RemoteA2aAgent:
    """Create RemoteA2aAgent with output_key state storage.

    Uses output_key when supported by the ADK version; otherwise stores output
    via after_agent_callback under the same state key.
    """
    common_kwargs = {
        'name': name,
        'description': description,
        'agent_card': agent_card,
    }
    try:
        return RemoteA2aAgent(**common_kwargs, output_key=output_key)
    except Exception:
        return RemoteA2aAgent(
            **common_kwargs,
            after_agent_callback=_make_output_key_callback(output_key),
        )


def create_summary_instruction(readonly_context: ReadonlyContext) -> str:
    """Create instruction for summary agent that combines parallel results."""
    data_output = readonly_context.state.get(CUSTOMER_DATA_OUTPUT_KEY, '')
    support_output = readonly_context.state.get(SUPPORT_OUTPUT_KEY, '')

    return f"""You are the Summary Agent for the customer support orchestrator.

Two specialist agents ran in parallel to handle the user's request:
1. Customer Data Agent — retrieved customer records, tickets, and statistics
2. Support Agent — provided troubleshooting guidance and support solutions

Customer Data Agent output:
{data_output}

Support Agent output:
{support_output}

Synthesize both outputs into a single cohesive, customer-friendly response.
Integrate factual data with actionable support guidance naturally.
Lead with the most relevant answer to the user's question.
Avoid repeating redundant information between the two outputs.
If one agent produced no output, rely on the available output alone.
Maintain a professional and empathetic tone throughout.
"""


def create_agent() -> SequentialAgent:
    """Create a parallel router agent that executes agents concurrently.

    Returns:
        SequentialAgent with parallel worker and summary synthesis agent.
    """
    logger.info("Creating Parallel Router Agent orchestrator")

    remote_customer_data = _create_parallel_remote_agent(
        name='customer_data',
        description='Access customer and ticket data from MCP server',
        agent_card=f'{CUSTOMER_DATA_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}',
        output_key=CUSTOMER_DATA_OUTPUT_KEY,
    )

    remote_support = _create_parallel_remote_agent(
        name='support_specialist',
        description='Provide customer support and troubleshooting solutions',
        agent_card=f'{SUPPORT_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}',
        output_key=SUPPORT_OUTPUT_KEY,
    )

    parallel_worker_agent = ParallelAgent(
        name='parallel_worker',
        sub_agents=[remote_customer_data, remote_support],
    )

    summary_agent = Agent(
        model=GEMINI_MODEL,
        name='summary_agent',
        description='Synthesizes parallel agent outputs into a unified response',
        instruction=create_summary_instruction,
        include_contents='none',
    )

    return SequentialAgent(
        name='parallel_customer_support_host',
        sub_agents=[parallel_worker_agent, summary_agent],
    )
