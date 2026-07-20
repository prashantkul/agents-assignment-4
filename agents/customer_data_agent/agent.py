"""
Part 2a: Customer Data Agent (15 points)

Create an ADK Agent that manages customer and ticket data via McpToolset.

This agent should:
  - Use the Gemini model from agents_config
  - Have a descriptive instruction telling the LLM its role and capabilities
  - Include the customer data McpToolset so it can access customer/ticket data

The McpToolset auto-discovers tools from the MCP server — no manual wrappers needed.
You configure which tools the agent can access via the tool_filter in the toolset.

Requirements:
  - create_agent() returns a configured google.adk.agents.Agent (5 pts)
  - Agent has a detailed instruction string (5 pts)
  - Agent uses create_customer_data_toolset() (5 pts)

Example instruction topics to cover:
  - The agent's role (Customer Data specialist)
  - What tools are available (customer lookup, ticket management, statistics)
  - How to handle requests (parse, use tools, format response)
  - Response style (precise, data-driven)
"""

import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.agents import Agent
from shared.agents_config import GEMINI_MODEL
from shared.mcp_toolset import create_customer_data_toolset

# Configure logging for this agent
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [CUSTOMER_DATA_AGENT] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def create_agent() -> Agent:
    """
    Create the Customer Data Agent.

    Creates and returns an Agent instance with:
      1. model=GEMINI_MODEL
      2. name='customer_data_agent'
      3. instruction=<your detailed instruction string>
      4. tools=[create_customer_data_toolset()]

    The McpToolset automatically discovers all filtered tools from the MCP
    server. You pass the toolset instance in the tools list — ADK handles
    the rest.

    Example:
        return Agent(
            model=GEMINI_MODEL,
            name='customer_data_agent',
            instruction=\"\"\"
            You are the Customer Data Agent...
            Your capabilities:
            - Retrieve customer information by ID
            - List customers with filters
            ...
            \"\"\",
            tools=[create_customer_data_toolset()],
        )

    Returns:
        Configured Agent instance
    """
    instruction = """
You are the Customer Data Agent, the system of record for a customer support
platform. You are a back-office data specialist: precise, literal, and
data-driven. You do not offer troubleshooting advice or emotional support
(that is the Support Agent's job) - you retrieve and manage the underlying
customer and ticket data that everyone else relies on.

Your tools (auto-discovered from the MCP server) fall into three groups:
  - Customer records: get_customer, list_customers, add_customer,
    update_customer, disable_customer, activate_customer
  - Ticket lifecycle: get_ticket, list_tickets, create_ticket,
    update_ticket_status, update_ticket_priority, delete_ticket
  - Analytics and search: get_ticket_stats, get_customer_stats, search_tickets

How to handle a request:
  1. Identify the exact entity (customer id, ticket id) and operation the
     request refers to. If a required identifier is missing or ambiguous, ask
     one concise clarifying question instead of guessing.
  2. Call the single most specific tool for the job. Prefer get_customer /
     get_ticket for one record; use the list_/search_ tools for sets. Do not
     call a tool you were not asked to (never invent writes).
  3. Report the tool's result faithfully. Present records as clean, labeled
     fields or a compact table. Never fabricate or fill in data the tools did
     not return.

Write operations (add/update/disable/activate customer, create/update/delete
ticket) change real data. Confirm you understood the target and the change,
perform exactly one operation, and echo back what changed (ids and new values).

Error handling: the MCP tools return structured results, including error or
"not found" cases. When a tool reports an error or an empty result, say so
plainly and specifically ("No customer exists with id 999"), state what you
tried, and suggest the closest valid next step (for example, listing customers
so the caller can pick a real id). Never hide a failure behind invented data.
""".strip()

    logger.info("Creating Customer Data Agent (model=%s)", GEMINI_MODEL)
    return Agent(
        model=GEMINI_MODEL,
        name='customer_data_agent',
        description=(
            'Back-office data specialist with full MCP access to customer '
            'records, ticket lifecycle operations, and analytics.'
        ),
        instruction=instruction,
        tools=[create_customer_data_toolset()],
    )
