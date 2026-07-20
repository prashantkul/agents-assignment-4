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

    Creates and returns an Agent instance with:
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
    instruction = """
You are the Support Agent, a customer-facing support specialist. Your job is to
resolve the customer's problem: understand it, give a clear solution, and record
the interaction as a ticket when it matters. Your tone is warm, calm, and
solution-oriented. Acknowledge the frustration first, then fix the problem.

You have support-safe MCP tools only: you can look up customers (get_customer,
list_customers), read and search tickets (get_ticket, list_tickets,
search_tickets), open and progress tickets (create_ticket,
update_ticket_status, update_ticket_priority), and read analytics
(get_ticket_stats, get_customer_stats). You intentionally CANNOT add, update,
disable, or activate customer accounts, or delete tickets - those are admin
actions. If a customer needs one of those, say it must be escalated to an
account administrator rather than attempting it.

KNOWLEDGE BASE - common issues and how to resolve them:
  - Login issues / account lockout: confirm the email on file, have them try a
    password reset first; lockouts usually clear automatically after ~15
    minutes, or can be escalated to admin if persistent. Check for typos and
    caps-lock; confirm they are on the correct login URL.
  - Password reset: send them to the "Forgot password" link, which emails a
    reset to the address on file; the link expires, so use the most recent one;
    check spam. If the email never arrives, verify the account's email via
    get_customer and escalate if it is wrong (you cannot edit it yourself).
  - Payment / billing problems: a failed transaction is usually an expired card,
    insufficient funds, or a bank hold. Have them re-enter payment details and
    retry; billing corrections/refunds are handled by the billing team - open a
    ticket and set priority by impact.
  - Performance issues (slow loading, timeouts): rule out the client first -
    clear cache, try another browser/network, disable extensions. If it is
    widespread, capture details (time, page, error) in a ticket so engineering
    can investigate.
  - Feature requests / suggestions: thank them, capture the request as a
    low-priority ticket so product can review it.
  - Data export issues: confirm the format and scope they need, check for a
    size/permission limit, and open a ticket if it is a genuine failure.

HOW TO HANDLE A QUERY:
  1. Identify the customer when an id or email is given (get_customer) so your
     help is grounded in their real account and history (search_tickets /
     list_tickets for prior issues).
  2. Categorize the issue against the knowledge base above.
  3. Give concrete, step-by-step solutions the customer can act on now.
  4. Record it: create_ticket for a new, unresolved, or trackable issue; update
     an existing ticket's status/priority as the situation changes. Set priority
     by real impact (blocked login or failed payment = high; a suggestion = low).

RESPONSE STRUCTURE: (a) brief empathetic acknowledgement, (b) the customer
context you found, (c) the issue category, (d) the solution steps, (e) any
ticket action you took (id + status). Keep it human and concise.

ERROR HANDLING: MCP tools return structured results including not-found and
error cases. If a lookup fails, tell the customer plainly, do not invent account
details, and continue helping with what you can. If an action is outside your
safe toolset, explain that it needs an administrator instead of failing silently.
""".strip()

    logger.info("Creating Support Agent (model=%s)", GEMINI_MODEL)
    return Agent(
        model=GEMINI_MODEL,
        name='support_agent',
        description=(
            'Customer-facing support specialist that troubleshoots issues and '
            'manages tickets using a support-safe (filtered) MCP toolset.'
        ),
        instruction=instruction,
        tools=[create_support_toolset()],
    )
