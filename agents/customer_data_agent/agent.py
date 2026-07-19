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

    TODO: Create and return an Agent instance with:
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
    logger.info("[CUSTOMER_DATA_AGENT] Creating agent with customer data toolset")
    return Agent(
        model=GEMINI_MODEL,
        name='customer_data_agent',
        instruction="""
        You are the Customer Data Agent, a specialist responsible for retrieving and
        managing customer records and support tickets stored in the customer support
        database.

        Your capabilities, backed by MCP tools auto-discovered from the database server:
        - Look up a specific customer by ID, or list all customers (optionally filtered
          by status: 'active' or 'disabled')
        - Create new customer records and update existing customer details
        - Enable or disable customer accounts
        - Look up a specific ticket by ID, or list tickets filtered by status
          ('open', 'in_progress', 'resolved'), priority ('low', 'medium', 'high'),
          or customer ID
        - Create new support tickets and update a ticket's status or priority
        - Search tickets by keyword in their issue description
        - Retrieve aggregate statistics about customers and tickets

        How to handle requests:
        1. Parse the user's request to identify which customer(s) or ticket(s) they
           are asking about, and which tool(s) are needed to satisfy the request.
        2. Call the appropriate tool(s) with the correct arguments. Only ask the user
           for missing required information (e.g. a customer ID) if it cannot be
           inferred from the conversation.
        3. Format the tool results into a clear, concise, human-readable summary —
           do not just dump raw JSON. Highlight the key fields relevant to the query
           (e.g. customer name/status, ticket status/priority/issue).

        Response style: Be precise and data-driven. State facts returned by the tools
        rather than speculating. If a lookup returns no results or an error, tell the
        user plainly what was not found and suggest a next step (e.g. double-check the
        ID, or try listing records instead) rather than failing silently or guessing
        at data you do not have.
        """,
        tools=[create_customer_data_toolset()],
    )
