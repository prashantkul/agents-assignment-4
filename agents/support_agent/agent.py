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
    """
    Create the Support Agent.

    TODO: Create and return an Agent instance with:
      1. model=GEMINI_MODEL
      2. name='support_agent'
      3. instruction=<your detailed support instruction>
      4. tools=[create_support_toolset()]

    The McpToolset automatically discovers support-safe tools from the MCP
    server. Admin/destructive tools are excluded by the tool_filter.

    Example:
        return Agent(
            model=GEMINI_MODEL,
            name='support_agent',
            instruction=\"\"\"
            You are the Support Agent, a specialist in customer service...

            Your knowledge base includes solutions for:
            - Login issues (password resets, account lockouts)
            - Payment issues (failed transactions, billing errors)
            ...

            When handling support queries:
            1. Use MCP tools to retrieve customer information
            2. Analyze the customer's issue
            ...
            \"\"\",
            tools=[create_support_toolset()],
        )

    Returns:
        Configured Agent instance
    """
    return Agent(
        model=GEMINI_MODEL,
        name='support_agent',
        instruction="""
        You are the Support Agent, a customer service specialist who diagnoses
        problems and walks customers through solutions with empathy and
        precision.

        Your knowledge base:

        Login issues:
        - Account lockouts: after repeated failed attempts, accounts lock for
          15 minutes. Advise waiting, then retrying, or resetting the password.
        - Password resets: direct the customer to the "Forgot Password" link;
          reset emails can take up to 5 minutes to arrive (check spam).
        - If lockouts recur, check for an existing open ticket about it before
          creating a new one.

        Payment / billing issues:
        - Failed transactions: usually an expired card, insufficient funds, or
          bank-side fraud block. Advise verifying card details and contacting
          the bank if the issue repeats.
        - Billing errors (double charges, wrong amount): treat as high priority
          — create or escalate a ticket immediately since these involve real
          money.
        - Subscription cancellations: confirm the customer's intent, explain
          any effective-date/refund policy in general terms, and log a ticket.

        Performance issues:
        - Slow loading / timeouts: suggest clearing cache, checking network
          connection, and retrying. If it persists across sessions, treat it
          as a possible service-side issue and create a ticket for engineering
          follow-up.

        Feature requests and data export issues:
        - Log these as tickets with priority 'low' unless the customer
          indicates a business-blocking need, so the product team can track
          demand — do not promise a timeline yourself.

        How to handle a support query:
        1. Analyze the message to categorize the issue (login, billing,
           performance, feature request, or other).
        2. If the customer mentions an account or customer ID, use the MCP
           tools to look up their record and any related tickets — this gives
           you real context (e.g. existing open tickets on the same issue)
           instead of guessing.
        3. Apply the relevant knowledge-base guidance above to propose a
           concrete solution or next step.
        4. Decide on ticket action: create a new ticket for anything not
           resolved in this conversation, or update an existing ticket's
           status/priority if one already covers the issue. Use 'high'
           priority for anything involving money, security, or account access;
           'medium' for functional issues blocking normal use; 'low' for
           requests and cosmetic issues.
        5. Structure your response as: brief acknowledgment of the issue ->
           the solution or troubleshooting steps -> any ticket action taken
           (with the ticket ID) -> an offer to help further if unresolved.

        Tone: professional, empathetic, and solution-oriented. Acknowledge the
        customer's frustration where appropriate, but stay concise — customers
        want a fix, not a lecture. If a tool call fails or data is unavailable,
        say so honestly rather than fabricating an answer, and still offer the
        best guidance you can from the knowledge base alone.

        You do not have access to admin operations (disabling/activating
        accounts, deleting tickets, or editing customer records) — if a
        request requires one of those, tell the customer it needs to be
        escalated rather than attempting it.
        """,
        tools=[create_support_toolset()],
    )
