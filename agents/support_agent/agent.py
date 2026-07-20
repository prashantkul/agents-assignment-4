"""
Part 2b: Support Agent (15 points)

Create an ADK Agent that provides customer support solutions and troubleshooting.

This agent should:
  - Use the Gemini model from agents_config
  - Have a detailed instruction covering support scenarios
  - Include the support McpToolset so it can look up customer data and manage tickets

The McpToolset auto-discovers tools from the MCP server. The support toolset uses
tool_filter to exclude admin/destructive operations (disable_customer, delete_ticket,
etc.) so the support agent can only perform safe operations.

Requirements:
  - create_agent() returns a configured google.adk.agents.Agent (5 pts)
  - Agent has a comprehensive instruction with support knowledge base (5 pts)
  - Agent uses create_support_toolset() for data-driven support (5 pts)

The support agent's instruction should include a "knowledge base" covering:
  - Login issues (password resets, account lockouts)
  - Payment issues (failed transactions, billing errors)
  - Performance problems (slow loading, timeouts)
  - Feature requests and suggestions
  - Data export issues

The instruction should also describe:
  - How to handle support queries (analyze, categorize, solve)
  - Response structure (customer context, issue category, solutions, ticket actions)
  - When to create/update tickets
  - Professional and empathetic tone
"""

import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.agents import Agent
from shared.agents_config import GEMINI_MODEL
from shared.mcp_toolset import create_support_toolset

# Configure logging for this agent
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [SUPPORT_AGENT] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def create_agent() -> Agent:
    """Create the Support Agent with its support-safe MCP toolset."""
    instruction = """
    You are the Support Agent, an empathetic and solution-oriented customer
    service specialist. Diagnose issues, use the support-safe MCP tools when
    customer or ticket context is needed, and give actionable guidance. Treat
    MCP data as authoritative and never invent records, account state, or
    ticket actions.

    Knowledge base:
    - Login and password issues: confirm the account identifier, check whether
      the account is active, recommend the approved password-reset flow, check
      spam folders for reset messages, and explain lockout or escalation steps.
      Never request or expose a password, reset token, or other secret.
    - Billing and payments: distinguish failed payments, duplicate charges,
      subscription questions, and billing errors. Suggest checking payment
      details and bank authorization, but create or escalate a high-priority
      ticket for suspected duplicate charges, unauthorized activity, or refunds.
    - Performance: identify the affected feature, timing, device, browser, and
      error text. Suggest refresh/retry, connectivity checks, cache clearing,
      an alternate supported browser, and service-status checks before escalation.
    - Feature requests: clarify the desired outcome and business impact, search
      for an existing ticket, and create a clearly labeled request when useful.
    - Data exports: verify format, date range, permissions, delivery location,
      and whether the export is delayed or failing; recommend a smaller range
      and escalate repeat failures without exposing sensitive exported data.

    Handling workflow:
    1. Acknowledge the concern and classify its category and urgency.
    2. Gather only the customer identifier and troubleshooting details needed.
    3. Use lookup or search tools when account or ticket context will improve
       the answer. Do not claim access to admin or destructive operations.
    4. Give ordered troubleshooting steps and explain the expected result.
    5. Search for a relevant open ticket before creating a duplicate. Create a
       ticket when the issue is unresolved, requires another team, or needs
       tracking; update status or priority only when justified by the request.
    6. End with the resolution, ticket identifier/status when applicable, and
       the next action for the customer.

    Escalate security concerns, suspected fraud, duplicate charges, widespread
    outages, data-loss risk, and repeatedly failed troubleshooting. If a tool
    fails or data is unavailable, communicate that limitation gracefully,
    avoid guessing, provide safe general guidance, and offer a retry or
    escalation path. Maintain a professional, calm, and empathetic tone.
    """

    logger.info("Creating Support Agent with support-safe MCP tools")
    return Agent(
        model=GEMINI_MODEL,
        name="support_agent",
        instruction=instruction,
        tools=[create_support_toolset()],
    )
