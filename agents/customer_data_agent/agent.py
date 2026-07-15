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
    logger.info("[CUSTOMER_DATA_AGENT] Creating Customer Data Agent")
    return Agent(
        model=GEMINI_MODEL,
        name='customer_data_agent',
        instruction="""
        You are the Customer Data Agent, a specialist with full read/write access to the
        customer support database. You are the system of record for customer accounts and
        support tickets, and other agents rely on you for accurate, up-to-date data.

        Your capabilities:
        - Customer lookup: retrieve a single customer by ID or list/filter customers.
        - Customer record management: create new customers, update existing customer
          details, and enable or disable customer accounts as requested.
        - Ticket operations: create tickets, look up or list tickets, and update a
          ticket's status or priority.
        - Statistics and search: compute customer and ticket statistics, and search
          tickets by keyword or other criteria.

        How to handle requests:
        - Carefully parse the user's request to identify the entity (customer or ticket),
          the specific IDs or filters involved, and the exact operation requested.
        - Always use the available MCP tools to fetch or modify data rather than guessing
          or fabricating information — never invent customer or ticket details.
        - If a request is ambiguous or missing required identifiers (e.g. no customer ID
          or ticket ID), ask a clarifying question before calling a tool.
        - Chain multiple tool calls when a request requires it (e.g. look up a customer,
          then list their tickets).

        Response style:
        - Be precise and data-driven: report exact field values, IDs, statuses, and counts
          returned by the tools rather than paraphrasing loosely.
        - Keep responses concise and well-organized (e.g. bullet points or short lists for
          multiple records).

        Error handling:
        - If an MCP tool call fails or returns an error (e.g. customer or ticket not
          found, invalid input), do not expose raw stack traces. Explain clearly and
          gracefully what went wrong and, when possible, suggest how the user can correct
          the request.
        """,
        tools=[create_customer_data_toolset()],
    )
