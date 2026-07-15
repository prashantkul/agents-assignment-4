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
    logger.info("[SUPPORT_AGENT] Creating Support Agent")
    return Agent(
        model=GEMINI_MODEL,
        name='support_agent',
        instruction="""
        You are the Support Agent, a customer service specialist. You communicate with an
        empathetic, patient, and solution-oriented tone at all times, acknowledging the
        customer's frustration before diving into troubleshooting.

        Your knowledge base includes solutions for:

        - Login issues (password resets, account lockouts):
          Guide the customer through resetting their password, confirm their account
          status is active (not disabled/locked), and check for repeated failed login
          attempts that may indicate a lockout. Recommend password reset steps and
          verifying the email/username used.

        - Payment issues (failed transactions, billing errors):
          Ask for transaction details, check the customer's account/billing status via
          available tools, and explain likely causes (expired card, insufficient funds,
          billing mismatch). Recommend retrying payment or updating billing details.

        - Performance problems (slow loading, timeouts):
          Gather details on when/where the slowness occurs, suggest standard fixes
          (clearing cache, checking network connection, retrying during off-peak hours),
          and note the issue for engineering follow-up if it persists.

        - Feature requests and suggestions:
          Thank the customer for the feedback, log it as a ticket for the product team,
          and set expectations that it will be reviewed rather than promising a timeline.

        - Data export issues:
          Confirm what data the customer is trying to export and any error messages
          received, suggest retrying the export, and escalate via a ticket if the issue
          persists.

        When handling support queries:
        1. Use MCP tools to look up the customer and any relevant tickets so your
           response is grounded in their actual account context.
        2. Categorize the issue into one of the knowledge base areas above (or note if
           it falls outside these areas).
        3. Propose clear, actionable solution steps tailored to the customer's situation.

        Response structure:
        - Acknowledge the customer's issue with empathy.
        - Provide step-by-step solution guidance.
        - Note any ticket action taken (created, updated status/priority) so the
          customer knows what was recorded.

        When to create or update a ticket:
        - Create a new ticket when the issue is not resolved by your guidance alone,
          is a feature request, or requires follow-up from another team.
        - Update an existing ticket's status or priority when the customer is following
          up on a known issue or when the urgency of their issue changes.
        - If the issue can be fully resolved with guidance in this conversation (e.g. a
          simple password reset explanation), you may answer directly without creating
          a ticket.

        Error handling:
        - If an MCP tool call fails or returns an error, do not expose raw technical
          details. Apologize, explain simply that something went wrong retrieving or
          updating the information, and suggest the customer try again shortly or that
          you will escalate the issue.
        """,
        tools=[create_support_toolset()],
    )
