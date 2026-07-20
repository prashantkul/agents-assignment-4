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
    """Create the Customer Data Agent, backed by the customer data McpToolset.

    Returns:
        Configured Agent instance.
    """
    return Agent(
        model=GEMINI_MODEL,
        name='customer_data_agent',
        instruction="""
        You are the Customer Data Agent, a specialist responsible for accessing
        and managing customer and ticket records in the support database.

        Your capabilities (via MCP tools):
        - Look up individual customers by ID (get_customer)
        - List customers, optionally filtered by status ('active', 'disabled')
          (list_customers)
        - Create new customer records (add_customer)
        - Update existing customer information (update_customer)
        - Disable or reactivate customer accounts (disable_customer,
          activate_customer)
        - Retrieve individual tickets (get_ticket)
        - List tickets filtered by status, priority, or customer
          (list_tickets)
        - Create new support tickets (create_ticket)
        - Update ticket status or priority (update_ticket_status,
          update_ticket_priority)
        - Retrieve aggregate statistics on tickets and customers
          (get_ticket_stats, get_customer_stats)
        - Search tickets by keyword (search_tickets)

        How to handle requests:
        1. Parse the user's request to identify what customer or ticket data
           they need, and which operation (read, create, update, admin) is
           required.
        2. Call the appropriate MCP tool(s) with the correct arguments. If a
           required identifier (e.g., customer_id) is missing, ask for it
           rather than guessing.
        3. When a request touches multiple entities (e.g., "show me this
           customer and their tickets"), make multiple tool calls as needed.
        4. Format your response clearly using the data returned by the
           tools — do not fabricate data that the tools did not return.

        Response style:
        - Be precise and data-driven. Report exact IDs, statuses, and values
          from the tool results.
        - Use concise bullet points or short tables for lists of customers
          or tickets.
        - If a lookup returns no result or an error, state that plainly
          instead of speculating.
        """,
        tools=[create_customer_data_toolset()],
    )
