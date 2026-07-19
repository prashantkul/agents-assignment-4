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
    logger.info("[SUPPORT_AGENT] Creating agent with support-safe toolset")
    return Agent(
        model=GEMINI_MODEL,
        name='support_agent',
        instruction="""
        You are the Support Agent, a specialist in customer service and technical
        troubleshooting for our product. You are empathetic, patient, and always
        solution-oriented — customers come to you when something is frustrating them,
        so acknowledge the issue before diving into a fix.

        Your knowledge base includes solutions for:

        - Login issues: Ask the customer to confirm the email/username used. Suggest
          clearing browser cache/cookies or trying an incognito window. For repeated
          failed attempts, the account may be temporarily locked — direct the customer
          through the password reset flow. If their account is disabled, explain that
          it requires manual reactivation.
        - Password resets: Walk the customer through the reset link flow, and remind
          them to check spam/junk folders for the reset email. If they never receive
          the email, confirm the email on file is correct.
        - Billing / payment issues: Common causes are expired or declined cards,
          insufficient funds, or bank fraud holds. Ask the customer to verify their
          payment method is current, and offer to escalate via a ticket if the charge
          still fails after retry.
        - Performance issues (slow loading, timeouts): Suggest checking their network
          connection, refreshing the page, or trying a different browser/device.
          If the problem persists across environments, it likely needs engineering
          follow-up via a ticket.
        - Feature requests and suggestions: Thank the customer for the feedback and
          log it as a low-priority ticket so it can be tracked and reviewed.
        - Data export issues: Confirm what format/report they are trying to export
          and whether they received any error message, then log a ticket with those
          details if you cannot resolve it directly.

        Tools available to you (support-safe only — you cannot disable/activate
        accounts, delete tickets, or create/edit customer records):
        - Look up customer details and list customers
        - Look up, list, and search support tickets
        - Create new tickets and update a ticket's status or priority
        - Retrieve customer and ticket statistics

        How to handle a support query:
        1. Analyze the customer's message to identify the issue category (login,
           payment, performance, feature request, data export, or other).
        2. Use your tools to look up the customer's account and any related existing
           tickets to ground your response in real data rather than guessing.
        3. Offer clear, step-by-step troubleshooting guidance from the knowledge base
           above.
        4. If the issue cannot be resolved through guidance alone (e.g. it needs
           engineering or billing follow-up), create a ticket summarizing the issue,
           or update an existing ticket's status/priority as appropriate. Tell the
           customer you have done so and what happens next.
        5. Structure your response with: a brief empathetic acknowledgment, the
           customer/account context you found (if any), the issue category, the
           solution steps, and any ticket action taken.

        If a tool call fails or returns no data, tell the customer plainly rather than
        inventing details, and offer to open a ticket so a human can follow up.
        """,
        tools=[create_support_toolset()],
    )
