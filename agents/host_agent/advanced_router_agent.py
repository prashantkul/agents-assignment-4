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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import a2a_compat  # noqa: F401

from google.adk.agents import Agent, SequentialAgent
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
    format='[%(asctime)s] [ROUTER_AGENT] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

DATA_KEYWORDS = [
    'customer', 'ticket', 'id', 'list', 'search', 'account', 'record',
    'stats', 'statistics', 'database', 'lookup', 'show me', 'find',
]
SUPPORT_KEYWORDS = [
    'help', 'issue', 'problem', 'reset', 'fix', 'login', 'password',
    'billing', 'payment', 'slow', 'timeout', 'error', 'broken',
    'cannot', "can't", 'unable', 'troubleshoot', 'support',
]
URGENCY_HIGH_KEYWORDS = ['urgent', 'immediately', 'asap', 'critical', 'emergency']
URGENCY_MEDIUM_KEYWORDS = ['soon', 'important', 'priority']


def _extract_user_query(readonly_context: ReadonlyContext) -> str:
    """Extract the user's query text from the invocation context."""
    if hasattr(readonly_context, 'latest_user_message'):
        message = getattr(readonly_context, 'latest_user_message', None)
        if message:
            return str(message)

    user_content = readonly_context.user_content
    if user_content and user_content.parts:
        texts = [part.text for part in user_content.parts if part.text]
        if texts:
            return ' '.join(texts)

    return ''


def analyze_query_intent(query: str) -> dict:
    """Analyze query to determine routing strategy.

    Args:
        query: The inbound user query text.

    Returns:
        Dict with needs_data, needs_support, urgency, and execution_mode.
    """
    query_lower = query.lower()

    needs_data = any(keyword in query_lower for keyword in DATA_KEYWORDS)
    needs_support = any(keyword in query_lower for keyword in SUPPORT_KEYWORDS)

    if not needs_data and not needs_support:
        needs_data = True
        needs_support = True

    if any(keyword in query_lower for keyword in URGENCY_HIGH_KEYWORDS):
        urgency = 'high'
    elif any(keyword in query_lower for keyword in URGENCY_MEDIUM_KEYWORDS):
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


def should_run_customer_data_agent(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """Skip Customer Data Agent when the query does not need data lookup."""
    routing_decision = callback_context.state.get('routing_decision', {})
    if not routing_decision.get('needs_data', True):
        logger.info("Skipping Customer Data Agent — needs_data is False")
        return types.Content(
            parts=[types.Part(
                text='Customer Data Agent skipped: query does not require data lookup.'
            )]
        )
    return None


def should_run_support_agent(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """Skip Support Agent when the query does not need support guidance."""
    routing_decision = callback_context.state.get('routing_decision', {})
    if not routing_decision.get('needs_support', True):
        logger.info("Skipping Support Agent — needs_support is False")
        return types.Content(
            parts=[types.Part(
                text='Support Agent skipped: query does not require support guidance.'
            )]
        )
    return None


def create_router_instruction(readonly_context: ReadonlyContext) -> str:
    """Dynamic instruction for router agent based on query analysis."""
    query = _extract_user_query(readonly_context)
    routing_decision = analyze_query_intent(query)

    if isinstance(readonly_context, CallbackContext):
        readonly_context.state['routing_decision'] = routing_decision
    else:
        readonly_context.session.state['routing_decision'] = routing_decision

    logger.info(
        "Routing decision: mode=%s, needs_data=%s, needs_support=%s, urgency=%s",
        routing_decision['execution_mode'],
        routing_decision['needs_data'],
        routing_decision['needs_support'],
        routing_decision['urgency'],
    )

    return f"""You are the Router Agent for the customer support orchestrator.

Your job is to analyze the user's query and confirm the routing strategy for
downstream agents. You do NOT answer the user's question directly.

User query: "{query}"

Routing analysis:
- needs_data: {routing_decision['needs_data']}
- needs_support: {routing_decision['needs_support']}
- urgency: {routing_decision['urgency']}
- execution_mode: {routing_decision['execution_mode']}

Execution plan:
- Customer Data Agent: {'RUN' if routing_decision['needs_data'] else 'SKIP'}
- Support Agent: {'RUN' if routing_decision['needs_support'] else 'SKIP'}

Briefly summarize the routing decision and which agents will handle this request.
Keep your response concise — the executor agents will do the actual work.
"""


def create_agent() -> SequentialAgent:
    """Create the advanced router agent with dynamic routing capabilities.

    Returns:
        SequentialAgent orchestrator with router and conditional sub-agents.
    """
    logger.info("Creating Advanced Router Agent orchestrator")

    router_agent = Agent(
        model=GEMINI_MODEL,
        name='router_agent',
        description='Analyzes user queries and determines agent routing strategy',
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
        name='sequential_executor',
        sub_agents=[remote_customer_data, remote_support],
    )

    return SequentialAgent(
        name='advanced_customer_support_host',
        sub_agents=[router_agent, sequential_execution_agent],
    )
