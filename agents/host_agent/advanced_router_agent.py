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

def _message_text(content) -> str:
    """Flatten a genai Content (or None) into a plain lowercase query string."""
    if content is None:
        return ""
    parts = getattr(content, "parts", None) or []
    text = " ".join((getattr(p, "text", None) or "") for p in parts)
    return text.strip()


# Keyword lexicons for deterministic intent detection. Kept classical on
# purpose: routing is a cheap, reproducible decision that does not need an LLM
# call. The LLM sits downstream, inside the agents that actually do the work.
_DATA_KEYWORDS = (
    "customer", "ticket", "tickets", "account", "id", "list", "search",
    "record", "records", "status", "open", "priority", "stats", "statistics",
    "history", "lookup", "database",
)
_SUPPORT_KEYWORDS = (
    "help", "issue", "problem", "reset", "fix", "login", "log in", "password",
    "billing", "payment", "charge", "refund", "slow", "error", "broken",
    "can't", "cannot", "trouble", "support", "how do i", "not working",
    "failed", "crash",
)
_URGENCY_KEYWORDS = ("urgent", "immediately", "asap", "critical", "emergency", "right now")


def analyze_query_intent(query: str) -> dict:
    """Analyze a user query to decide how to route it.

    Deterministic keyword analysis (no LLM call) returning a routing decision:
      - needs_data: does the query require a customer/ticket lookup?
      - needs_support: does the query require troubleshooting/help?
      - urgency: 'low' | 'medium' | 'high'
      - execution_mode: 'sequential' (both) | 'data_only' | 'support_only'

    Args:
        query: The raw user query text.

    Returns:
        dict: routing decision as described above.
    """
    q = (query or "").lower()

    needs_data = any(kw in q for kw in _DATA_KEYWORDS)
    needs_support = any(kw in q for kw in _SUPPORT_KEYWORDS)

    # Fail safe: if we cannot tell, run the full pipeline rather than silently
    # skipping a step. An empty plan is the worst outcome for the user.
    if not needs_data and not needs_support:
        needs_data = needs_support = True

    if needs_data and needs_support:
        execution_mode = "sequential"
    elif needs_data:
        execution_mode = "data_only"
    else:
        execution_mode = "support_only"

    urgency = "high" if any(kw in q for kw in _URGENCY_KEYWORDS) else "low"
    # A blocked-access support issue is at least medium even without an urgency word.
    if urgency == "low" and needs_support and any(
        kw in q for kw in ("login", "log in", "password", "payment", "billing", "failed")
    ):
        urgency = "medium"

    decision = {
        "needs_data": needs_data,
        "needs_support": needs_support,
        "urgency": urgency,
        "execution_mode": execution_mode,
    }
    logger.info("[ROUTER] intent(%r) -> %s", query[:60], decision)
    return decision


def store_routing_decision(callback_context: CallbackContext) -> Optional[types.Content]:
    """Router before_agent_callback: compute the routing decision and store it.

    ReadonlyContext (what an instruction provider receives) exposes state as a
    read-only mapping, so the decision is written here, from a CallbackContext
    whose .state is writable. It runs before the router agent's instruction is
    built and before any sub-agent, so the plan is in session state by the time
    the sub-agent gating callbacks read it.
    """
    query = _message_text(callback_context.user_content)
    callback_context.state["routing_decision"] = analyze_query_intent(query)
    return None  # None -> let the router agent run normally


# =============================================================================
# TODO BONUS: Callback Functions for Dynamic Routing
# =============================================================================

def should_run_customer_data_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Callback to determine if Customer Data Agent should run.

    If the routing decision says the query does not need data, return a Content
    to skip the agent (its cost is avoided); otherwise return None to run it.
    """
    routing_decision = callback_context.state.get("routing_decision", {})
    if routing_decision.get("needs_data") is False:
        logger.info("[ROUTER] skipping Customer Data Agent (needs_data=False)")
        return types.Content(
            role="model",
            parts=[types.Part(
                text="[Router] Skipped account lookup: this query does not "
                     "reference a customer or ticket."
            )],
        )
    return None


def should_run_support_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Callback to determine if Support Agent should run.

    Mirror of should_run_customer_data_agent, gating on needs_support.
    """
    routing_decision = callback_context.state.get("routing_decision", {})
    if routing_decision.get("needs_support") is False:
        logger.info("[ROUTER] skipping Support Agent (needs_support=False)")
        return types.Content(
            role="model",
            parts=[types.Part(
                text="[Router] Skipped support step: this query is a pure data "
                     "lookup with no troubleshooting request."
            )],
        )
    return None


# =============================================================================
# TODO BONUS: Router Agent with Dynamic Instruction
# =============================================================================

def create_router_instruction(readonly_context) -> str:
    """
    Dynamic instruction for router agent based on query analysis.

    The decision itself is computed and stored by store_routing_decision (the
    router's before_agent_callback), because an instruction provider only gets a
    read-only view of state. Here we read that decision back and return an
    instruction that announces the routing plan to the user.
    """
    decision = readonly_context.state.get("routing_decision")
    if not decision:
        # Callback has not run yet (e.g. standalone invocation) - compute live.
        decision = analyze_query_intent(_message_text(readonly_context.user_content))

    steps = []
    if decision.get("needs_data"):
        steps.append("look up the customer/ticket data")
    if decision.get("needs_support"):
        steps.append("provide troubleshooting and resolution")
    plan = " then ".join(steps) if steps else "handle the request"

    return (
        "You are the routing coordinator for a customer support system. "
        f"Based on query analysis, the plan is to {plan} "
        f"(urgency: {decision.get('urgency', 'low')}, "
        f"mode: {decision.get('execution_mode', 'sequential')}).\n"
        "State the plan in one short sentence. Do not attempt the work "
        "yourself - the specialist sub-agents that run after you will execute it."
    )


# =============================================================================
# TODO BONUS: Create Advanced Agent
# =============================================================================

def create_agent():
    """
    Create the advanced router agent with dynamic routing capabilities.

    Structure:
        orchestrator (SequentialAgent)
          - router_agent (LlmAgent): before_agent_callback computes and stores
            the routing decision; its dynamic instruction announces the plan.
          - sequential_execution_agent (SequentialAgent):
              - remote_customer_data (RemoteA2aAgent) gated by
                should_run_customer_data_agent
              - remote_support (RemoteA2aAgent) gated by should_run_support_agent

    Returns:
        Configured SequentialAgent with a router and conditional sub-agents.
    """
    router_agent = Agent(
        model=GEMINI_MODEL,
        name="router",
        description="Analyzes the query and announces the routing plan.",
        instruction=create_router_instruction,
        before_agent_callback=store_routing_decision,
    )

    remote_customer_data = RemoteA2aAgent(
        name="customer_data",
        description="Access customer and ticket data from MCP server",
        agent_card=f"{CUSTOMER_DATA_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
        before_agent_callback=should_run_customer_data_agent,
    )

    remote_support = RemoteA2aAgent(
        name="support_specialist",
        description="Provide customer support and troubleshooting solutions",
        agent_card=f"{SUPPORT_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
        before_agent_callback=should_run_support_agent,
    )

    sequential_execution_agent = SequentialAgent(
        name="conditional_executor",
        description="Runs the data and support agents subject to routing gates.",
        sub_agents=[remote_customer_data, remote_support],
    )

    logger.info("Creating ADVANCED router agent (router -> conditional executor)")
    return SequentialAgent(
        name="advanced_customer_support_host",
        description=(
            "Advanced orchestrator: analyzes the query, then conditionally "
            "delegates to the data and support agents over A2A."
        ),
        sub_agents=[router_agent, sequential_execution_agent],
    )
