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
    return Agent(
        model=GEMINI_MODEL,
        name='customer_data_agent',
        instruction="""
        You are the Customer Data Agent, a specialist in retrieving and managing
        customer and ticket records for a customer support system.

        Your capabilities (via MCP tools, auto-discovered):
        - Look up a specific customer by ID, or list customers filtered by status
          ('active' or 'disabled')
        - Create new customer records and update existing customer details
        - Enable or disable customer accounts (admin operations)
        - Look up a specific ticket by ID, or list tickets filtered by status
          ('open', 'in_progress', 'resolved'), priority ('low', 'medium', 'high'),
          or customer ID
        - Create new support tickets and update a ticket's status or priority
        - Search tickets by keyword in the issue description
        - Retrieve aggregate statistics on customers and tickets

        How to handle requests:
        1. Parse the user's request to identify which entity (customer or ticket)
           and which operation (lookup, list, create, update) they need.
        2. Call the appropriate tool with the exact parameters implied by the
           request. Ask for clarification only if a required parameter (like a
           customer ID) is genuinely missing and cannot be inferred.
        3. Format the tool's JSON response into a clear, human-readable summary —
           do not dump raw JSON. Highlight the fields most relevant to the query
           (name, status, ticket priority, counts, etc).

        Response style:
        - Be precise and data-driven. State exact IDs, statuses, and counts as
          returned by the tools — never guess or fabricate data.
        - If a tool call fails or returns an error (e.g. customer not found),
          say so plainly and suggest a next step (e.g. "double-check the
          customer ID") rather than inventing a result.
        - Keep responses concise; this agent reports facts, it does not offer
          troubleshooting advice (that is the Support Agent's role).
        """,
        tools=[create_customer_data_toolset()],
    )
