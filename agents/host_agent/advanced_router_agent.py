"""
BONUS Part A: Advanced Router Agent with Dynamic Routing (+10 points)

This is an OPTIONAL bonus implementation that adds intelligent routing:
  - Analyzes query intent to determine which agents to invoke
  - Uses before_agent_callback to conditionally skip agents
  - Includes a router LLM agent for task decomposition

Architecture:
  Orchestrator (SequentialAgent)
    -> Router Agent (LLM Agent) -- analyzes query, sets routing decision
    -> Sequential Executor (SequentialAgent)
         -> RemoteA2aAgent("customer_data") with before_agent_callback
         -> RemoteA2aAgent("support_specialist") with before_agent_callback

Requirements for bonus points:
  - analyze_query_intent function works correctly (3 pts)
  - Callback functions properly skip/run agents (3 pts)
  - Router agent with dynamic instruction (2 pts)
  - Full orchestrator assembled correctly (2 pts)
"""

import sys
import os
import logging
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# IMPORTANT: Apply A2A compatibility patch BEFORE importing RemoteA2aAgent
from shared import a2a_compat  # noqa: F401

from google.adk.agents import Agent, SequentialAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH
from shared.agents_config import (
    CUSTOMER_DATA_AGENT_URL,
    SUPPORT_AGENT_URL,
    GEMINI_MODEL,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [ROUTER_AGENT] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# =============================================================================
# Routing Logic Functions
# =============================================================================

DATA_KEYWORDS = [
    'customer', 'ticket', 'id', 'list', 'search', 'account',
    'status', 'stats', 'statistics', 'history',
]
SUPPORT_KEYWORDS = [
    'help', 'issue', 'problem', 'reset', 'fix', 'trouble',
    'cannot', "can't", 'error', 'broken', 'support', 'cancel',
    'refund', 'billing',
]
HIGH_URGENCY_KEYWORDS = ['urgent', 'immediately', 'asap', 'critical', 'right now']
MEDIUM_URGENCY_KEYWORDS = ['soon', 'important', 'please help']


def analyze_query_intent(query: str) -> dict:
    """
    Analyze query to determine routing strategy.

    Returns:
        dict with keys:
          - needs_data: bool (does the query need customer/ticket data?)
          - needs_support: bool (does the query need support/help?)
          - urgency: str ('low', 'medium', 'high')
          - execution_mode: str ('sequential', 'data_only', 'support_only')
    """
    query_lower = query.lower()

    needs_data = any(keyword in query_lower for keyword in DATA_KEYWORDS)
    needs_support = any(keyword in query_lower for keyword in SUPPORT_KEYWORDS)

    # If intent is ambiguous, default to running both agents rather than
    # silently dropping capability the user may need.
    if not needs_data and not needs_support:
        needs_data = True
        needs_support = True

    if any(keyword in query_lower for keyword in HIGH_URGENCY_KEYWORDS):
        urgency = 'high'
    elif any(keyword in query_lower for keyword in MEDIUM_URGENCY_KEYWORDS):
        urgency = 'medium'
    else:
        urgency = 'low'

    if needs_data and needs_support:
        execution_mode = 'sequential'
    elif needs_data:
        execution_mode = 'data_only'
    else:
        execution_mode = 'support_only'

    return {
        'needs_data': needs_data,
        'needs_support': needs_support,
        'urgency': urgency,
        'execution_mode': execution_mode,
    }


def _extract_query_text(context) -> str:
    """Extract the plain-text user query from a Readonly/Callback context."""
    user_content = context.user_content
    if user_content and user_content.parts:
        return ''.join(part.text or '' for part in user_content.parts)
    return ''


# =============================================================================
# Callback Functions for Dynamic Routing
# =============================================================================

def analyze_and_store_routing_decision(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """before_agent_callback for the router agent.

    Computes the routing decision from the user's query and stores it in
    session state (under 'routing_decision') so downstream skip-callbacks
    and the router's own dynamic instruction can read it.
    """
    query = _extract_query_text(callback_context)
    routing_decision = analyze_query_intent(query)
    callback_context.state['routing_decision'] = routing_decision
    logger.info(f"[ROUTER] Query analysis: {routing_decision}")
    return None  # Let the router agent's LLM turn run normally.


def should_run_customer_data_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    """Callback to determine if Customer Data Agent should run."""
    routing_decision = callback_context.state.get('routing_decision', {})
    if not routing_decision.get('needs_data', True):
        logger.info("[ROUTER] Skipping Customer Data Agent (not needed)")
        return types.Content(
            role='model',
            parts=[types.Part(text="Skipping customer data lookup — not needed for this request.")],
        )
    return None


def should_run_support_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    """Callback to determine if Support Agent should run."""
    routing_decision = callback_context.state.get('routing_decision', {})
    if not routing_decision.get('needs_support', True):
        logger.info("[ROUTER] Skipping Support Agent (not needed)")
        return types.Content(
            role='model',
            parts=[types.Part(text="Skipping support troubleshooting — not needed for this request.")],
        )
    return None


# =============================================================================
# Router Agent with Dynamic Instruction
# =============================================================================

def create_router_instruction(readonly_context) -> str:
    """
    Dynamic instruction for the router agent based on query analysis.

    The actual routing_decision is computed and stored in state by the
    before_agent_callback (analyze_and_store_routing_decision), which runs
    before this instruction is rendered. We fall back to computing it fresh
    here in case the state isn't populated yet (analyze_query_intent is a
    pure function, so recomputing is safe and cheap).
    """
    query = _extract_query_text(readonly_context)
    routing_decision = readonly_context.state.get('routing_decision') or analyze_query_intent(query)

    return f"""
You are the Router Agent for a customer support system. You analyze the
user's request and prepare it for the specialist agents that will run next.

User request: "{query}"

Query analysis:
  - Needs customer/ticket data: {routing_decision['needs_data']}
  - Needs support troubleshooting: {routing_decision['needs_support']}
  - Urgency: {routing_decision['urgency']}
  - Execution mode: {routing_decision['execution_mode']}

Briefly acknowledge the request in one sentence and state which specialists
will handle it (Customer Data, Support, or both). Do not attempt to answer
the request yourself — the specialist agents that run after you will do the
actual work.
""".strip()


# =============================================================================
# Create Advanced Agent
# =============================================================================

def create_agent():
    """
    Create the advanced router agent with dynamic routing capabilities.

    Returns:
        Configured SequentialAgent with router and conditional sub-agents
    """
    router_agent = Agent(
        model=GEMINI_MODEL,
        name='router_agent',
        instruction=create_router_instruction,
        before_agent_callback=analyze_and_store_routing_decision,
    )

    remote_customer_data = RemoteA2aAgent(
        name='customer_data',
        description='Access customer and ticket data from MCP server',
        agent_card=f'{CUSTOMER_DATA_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}',
        before_agent_callback=should_run_customer_data_agent,
    )

    remote_support = RemoteA2aAgent(
        name='support_specialist',
        description='Provide customer support and troubleshooting solutions',
        agent_card=f'{SUPPORT_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}',
        before_agent_callback=should_run_support_agent,
    )

    sequential_execution_agent = SequentialAgent(
        name='conditional_executor',
        sub_agents=[remote_customer_data, remote_support],
    )

    return SequentialAgent(
        name='customer_support_host_advanced',
        sub_agents=[router_agent, sequential_execution_agent],
    )
