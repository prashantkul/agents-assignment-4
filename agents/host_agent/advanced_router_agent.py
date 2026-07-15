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
        'customer', 'ticket', 'id', 'list', 'search', 'account',
        'statistics', 'stats', 'show me',
    ]
    support_keywords = [
        'help', 'issue', 'problem', 'reset', 'fix', 'login', 'password',
        'billing', 'payment', 'cancel', 'trouble', 'error', "can't",
        'broken', 'slow', 'resolve',
    ]
    urgency_keywords = [
        'urgent', 'immediately', 'asap', 'critical', 'right now',
        'emergency',
    ]

    needs_data = any(kw in query_lower for kw in data_keywords)
    needs_support = any(kw in query_lower for kw in support_keywords)

    # Ambiguous query: fall back to running both rather than silently
    # dropping information the user may have wanted.
    if not needs_data and not needs_support:
        needs_data = True
        needs_support = True

    if any(kw in query_lower for kw in urgency_keywords):
        urgency = 'high'
    elif needs_data and needs_support:
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


def _extract_query_text(content: Optional[types.Content]) -> str:
    """Extract the plain-text query from an A2A/GenAI Content object."""
    if content is None:
        return ''
    parts = getattr(content, 'parts', None) or []
    return ' '.join(p.text for p in parts if getattr(p, 'text', None))


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
    if routing_decision.get('needs_data', True) is False:
        logger.info("[ROUTER] Skipping Customer Data Agent (not needed for this query)")
        return types.Content(
            parts=[types.Part(
                text="(Customer Data Agent skipped — this query does not require account/ticket lookup.)"
            )]
        )
    return None


def should_run_support_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Callback to determine if Support Agent should run.

    TODO: Similar to should_run_customer_data_agent but checks needs_support.
    """
    routing_decision = callback_context.state.get('routing_decision', {})
    if routing_decision.get('needs_support', True) is False:
        logger.info("[ROUTER] Skipping Support Agent (not needed for this query)")
        return types.Content(
            parts=[types.Part(
                text="(Support Agent skipped — this query does not require troubleshooting guidance.)"
            )]
        )
    return None


def set_routing_decision(callback_context: CallbackContext) -> Optional[types.Content]:
    """Before-agent callback on the router agent: analyzes the query and
    persists the routing decision to session state.

    This exists because the router's dynamic *instruction* function only
    receives a ReadonlyContext (its `.state` is a read-only MappingProxyType
    in this ADK version — item assignment raises TypeError). A
    before_agent_callback, by contrast, receives a real CallbackContext whose
    `.state` is writable and durably persisted via event state-deltas. Doing
    the state write here (rather than in create_router_instruction) is what
    makes should_run_customer_data_agent / should_run_support_agent actually
    see the routing decision on the next steps of the SequentialAgent.
    """
    query = _extract_query_text(callback_context.user_content)
    routing_decision = analyze_query_intent(query)
    callback_context.state['routing_decision'] = routing_decision
    logger.info(f"[ROUTER] Query analysis: {routing_decision}")
    return None


# =============================================================================
# TODO BONUS: Router Agent with Dynamic Instruction
# =============================================================================

def create_router_instruction(readonly_context) -> str:
    """
    Dynamic instruction for router agent based on query analysis.

    TODO: Implement this function to:
      1. Get the user's query from readonly_context.latest_user_message
      2. Call analyze_query_intent(query)
      3. Store routing_decision in readonly_context.state
      4. Return a dynamic instruction string based on the analysis

    NOTE: readonly_context.state is read-only in this ADK version (see
    set_routing_decision's docstring for why) — the actual state write that
    the callbacks depend on happens in the router's before_agent_callback.
    This function independently re-runs the same pure analysis to build its
    instruction text, which keeps it correct without relying on a write that
    would raise TypeError here.
    """
    query = _extract_query_text(readonly_context.user_content)
    routing_decision = analyze_query_intent(query)

    lines = [
        "You are the Router Agent for a customer support system.",
        f'Analyzing the user\'s query: "{query}"',
        "",
    ]

    if routing_decision['execution_mode'] == 'data_only':
        lines.append(
            "This query only needs customer/ticket data — no support "
            "troubleshooting is required."
        )
    elif routing_decision['execution_mode'] == 'support_only':
        lines.append(
            "This query only needs support/troubleshooting guidance — no "
            "data lookup is required."
        )
    else:
        lines.append(
            "This query needs both customer/ticket data AND support "
            "guidance, in that order."
        )

    if routing_decision['urgency'] == 'high':
        lines.append(
            "This query has been flagged as HIGH URGENCY — prioritize a "
            "fast, direct response."
        )

    lines.append(
        "Acknowledge the routing decision in one brief sentence. Do not "
        "attempt to answer the query yourself — the downstream specialist "
        "agents will handle the actual data lookup and support guidance."
    )

    return "\n".join(lines)


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
    router_agent = Agent(
        model=GEMINI_MODEL,
        name='router_agent',
        instruction=create_router_instruction,
        before_agent_callback=set_routing_decision,
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
        name='advanced_router_host',
        sub_agents=[router_agent, sequential_execution_agent],
    )
