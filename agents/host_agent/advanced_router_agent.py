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

from google.adk.agents import Agent, SequentialAgent, ParallelAgent
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
# TODO BONUS: Routing Logic Functions
# =============================================================================

def analyze_query_intent(query: str) -> dict:
    """
    Analyze query to determine routing strategy.

    TODO: Implement query analysis that returns:
      - needs_data: bool (does the query need customer/ticket data?)
      - needs_support: bool (does the query need support/help?)
      - urgency: str ('low', 'medium', 'high')
      - execution_mode: str ('sequential', 'data_only', 'support_only')

    Hints:
      - Check for data keywords: 'customer', 'ticket', 'id', 'list', 'search'
      - Check for support keywords: 'help', 'issue', 'problem', 'reset', 'fix'
      - Check for urgency keywords: 'urgent', 'immediately', 'asap', 'critical'

    Example return:
        {
            'needs_data': True,
            'needs_support': True,
            'urgency': 'medium',
            'execution_mode': 'sequential'
        }
    """
    query_lower = query.lower()

    data_keywords = [
        'customer', 'ticket', 'account', 'id', 'list', 'search',
        'record', 'stats', 'statistics',
    ]
    support_keywords = [
        'help', 'issue', 'problem', 'reset', 'fix', 'login', 'password',
        'payment', 'billing', 'slow', 'error', 'trouble', 'support',
    ]
    urgency_keywords_high = ['urgent', 'immediately', 'asap', 'critical', 'emergency']
    urgency_keywords_medium = ['soon', 'important', 'priority']

    needs_data = any(keyword in query_lower for keyword in data_keywords)
    needs_support = any(keyword in query_lower for keyword in support_keywords)

    if any(keyword in query_lower for keyword in urgency_keywords_high):
        urgency = 'high'
    elif any(keyword in query_lower for keyword in urgency_keywords_medium):
        urgency = 'medium'
    else:
        urgency = 'low'

    # Default to running both agents when intent is unclear, since a
    # combined data + support response is always safe to give.
    if not needs_data and not needs_support:
        needs_data = True
        needs_support = True

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


# =============================================================================
# TODO BONUS: Callback Functions for Dynamic Routing
# =============================================================================

def should_run_customer_data_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Callback to determine if Customer Data Agent should run.

    TODO: Check callback_context.state for routing_decision.
      - If needs_data is False, return Content to skip the agent
      - If needs_data is True (or missing), return None to run it

    Hints:
      - routing_decision = callback_context.state.get('routing_decision', {})
      - Return None to run the agent
      - Return types.Content(parts=[types.Part(text="...")]) to skip
    """
    routing_decision = callback_context.state.get('routing_decision', {})
    if routing_decision.get('needs_data', True):
        return None

    logger.info("[ROUTER_AGENT] Skipping Customer Data Agent (not needed for this query)")
    return types.Content(
        parts=[types.Part(text="Skipping customer data lookup — not needed for this query.")]
    )


def should_run_support_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Callback to determine if Support Agent should run.

    TODO: Similar to should_run_customer_data_agent but checks needs_support.
    """
    routing_decision = callback_context.state.get('routing_decision', {})
    if routing_decision.get('needs_support', True):
        return None

    logger.info("[ROUTER_AGENT] Skipping Support Agent (not needed for this query)")
    return types.Content(
        parts=[types.Part(text="Skipping support troubleshooting — not needed for this query.")]
    )


# =============================================================================
# TODO BONUS: Router Agent with Dynamic Instruction
# =============================================================================

def _extract_query_text(readonly_context) -> str:
    """Extract the plain-text user query from the context's user_content."""
    user_content = readonly_context.user_content
    if not user_content or not user_content.parts:
        return ""
    return " ".join(part.text for part in user_content.parts if part.text)


def create_router_instruction(readonly_context) -> str:
    """
    Dynamic instruction for router agent based on query analysis.

    TODO: Implement this function to:
      1. Get the user's query from readonly_context.latest_user_message
      2. Call analyze_query_intent(query)
      3. Store routing_decision in readonly_context.state
      4. Return a dynamic instruction string based on the analysis
    """
    query = _extract_query_text(readonly_context)
    routing_decision = analyze_query_intent(query)

    # CallbackContext.state is delta-aware and mutable in place; ReadonlyContext.state
    # is a read-only mapping, so this only persists when invoked as part of a live
    # agent run (where the underlying context is actually a CallbackContext).
    try:
        readonly_context.state['routing_decision'] = routing_decision
    except TypeError:
        pass

    return f"""
    You are the Routing Agent for a customer support system. Analyze the user's
    query and briefly confirm the routing plan before the specialist agents run.

    Query analysis:
    - Needs customer/ticket data lookup: {routing_decision['needs_data']}
    - Needs support troubleshooting: {routing_decision['needs_support']}
    - Urgency: {routing_decision['urgency']}
    - Execution mode: {routing_decision['execution_mode']}

    Briefly state which specialist agent(s) will handle this request and why,
    then let the routing proceed. Keep your response to one or two sentences.
    """


# =============================================================================
# TODO BONUS: Create Advanced Agent
# =============================================================================

def create_agent():
    """
    Create the advanced router agent with dynamic routing capabilities.

    TODO: Assemble the full orchestrator:
      1. Create router_agent (Agent with dynamic instruction)
      2. Create remote_customer_data (RemoteA2aAgent with before_agent_callback)
      3. Create remote_support (RemoteA2aAgent with before_agent_callback)
      4. Create sequential_execution_agent (SequentialAgent with both remotes)
      5. Create orchestrator (SequentialAgent with router + executor)

    Returns:
        Configured SequentialAgent with router and conditional sub-agents
    """
    logger.info("[ROUTER_AGENT] Creating advanced router agent with dynamic routing")

    router_agent = Agent(
        model=GEMINI_MODEL,
        name='query_router',
        instruction=create_router_instruction,
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

    orchestrator = SequentialAgent(
        name='advanced_customer_support_host',
        sub_agents=[router_agent, sequential_execution_agent],
    )

    return orchestrator
