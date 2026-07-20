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
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
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
# Routing Logic
# =============================================================================

def analyze_query_intent(query: str) -> dict:
    """Classify a query's worker requirements, urgency, and execution mode."""
    normalized_query = query.casefold()

    data_keywords = {
        "account",
        "customer",
        "customer id",
        "history",
        "id ",
        "list",
        "record",
        "search",
        "statistic",
        "status",
        "ticket",
    }
    support_keywords = {
        "billing",
        "can't",
        "cannot",
        "charged",
        "error",
        "failed",
        "fix",
        "help",
        "issue",
        "login",
        "password",
        "payment",
        "problem",
        "refund",
        "reset",
        "slow",
        "support",
        "timeout",
        "unable",
    }
    high_urgency_keywords = {
        "asap",
        "critical",
        "emergency",
        "immediately",
        "security breach",
        "urgent",
    }
    medium_urgency_keywords = {
        "charged",
        "duplicate",
        "failed",
        "locked",
        "outage",
        "refund",
        "unable",
    }

    needs_data = any(
        keyword in normalized_query for keyword in data_keywords
    )
    needs_support = any(
        keyword in normalized_query for keyword in support_keywords
    )

    # A query with no recognizable data vocabulary is safest to treat as a
    # general support request instead of skipping both worker agents.
    if not needs_data and not needs_support:
        needs_support = True

    if any(
        keyword in normalized_query for keyword in high_urgency_keywords
    ):
        urgency = "high"
    elif any(
        keyword in normalized_query for keyword in medium_urgency_keywords
    ):
        urgency = "medium"
    else:
        urgency = "low"

    if needs_data and needs_support:
        execution_mode = "sequential"
    elif needs_data:
        execution_mode = "data_only"
    else:
        execution_mode = "support_only"

    return {
        "needs_data": needs_data,
        "needs_support": needs_support,
        "urgency": urgency,
        "execution_mode": execution_mode,
    }


# =============================================================================
# Conditional Worker Callbacks
# =============================================================================

def should_run_customer_data_agent(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """Run the Customer Data Agent unless routing explicitly excludes it."""
    routing_decision = callback_context.state.get("routing_decision", {})
    if routing_decision.get("needs_data", True):
        return None

    logger.info("Skipping Customer Data Agent based on routing decision")
    return types.Content(
        parts=[
            types.Part(
                text=(
                    "Customer data lookup was skipped because this request "
                    "does not require customer or ticket data."
                )
            )
        ]
    )


def should_run_support_agent(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """Run the Support Agent unless routing explicitly excludes it."""
    routing_decision = callback_context.state.get("routing_decision", {})
    if routing_decision.get("needs_support", True):
        return None

    logger.info("Skipping Support Agent based on routing decision")
    return types.Content(
        parts=[
            types.Part(
                text=(
                    "Support troubleshooting was skipped because this "
                    "request only requires a data operation."
                )
            )
        ]
    )


# =============================================================================
# Dynamic Router Instruction
# =============================================================================

def create_router_instruction(readonly_context: ReadonlyContext) -> str:
    """Analyze the latest query, persist its route, and instruct the router."""
    latest_message = getattr(readonly_context, "latest_user_message", None)
    message_parts = getattr(latest_message, "parts", []) or []
    query = " ".join(
        part.text
        for part in message_parts
        if isinstance(getattr(part, "text", None), str)
    ).strip()

    routing_decision = analyze_query_intent(query)
    readonly_context.state["routing_decision"] = routing_decision

    return f"""
    You are the routing stage for a customer-support workflow. The current
    request has already been analyzed as follows:
    - needs customer or ticket data: {routing_decision["needs_data"]}
    - needs troubleshooting support: {routing_decision["needs_support"]}
    - urgency: {routing_decision["urgency"]}
    - execution mode: {routing_decision["execution_mode"]}

    Briefly state the routing plan for the worker agents. Do not answer the
    customer request, invent data, or attempt tool calls yourself. Preserve
    the original request in conversation context for the selected workers.
    """


# =============================================================================
# Advanced Agent Factory
# =============================================================================

def create_agent() -> SequentialAgent:
    """Create a routed orchestrator with conditionally executed workers."""
    router_agent = Agent(
        model=GEMINI_MODEL,
        name="query_router",
        description="Analyzes each request and selects the required workers",
        instruction=create_router_instruction,
    )

    remote_customer_data = RemoteA2aAgent(
        name="customer_data",
        description="Access customer and ticket data from MCP server",
        agent_card=(
            f"{CUSTOMER_DATA_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}"
        ),
        before_agent_callback=should_run_customer_data_agent,
    )

    remote_support = RemoteA2aAgent(
        name="support_specialist",
        description="Provide customer support and troubleshooting solutions",
        agent_card=f"{SUPPORT_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
        before_agent_callback=should_run_support_agent,
    )

    sequential_execution_agent = SequentialAgent(
        name="conditional_support_workers",
        description="Runs only the workers selected by the query router",
        sub_agents=[remote_customer_data, remote_support],
    )

    return SequentialAgent(
        name="advanced_customer_support_host",
        description="Routes support requests to the required remote agents",
        sub_agents=[router_agent, sequential_execution_agent],
    )
