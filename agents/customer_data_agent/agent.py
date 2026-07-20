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
    """Create the Customer Data Agent with broad MCP data access."""
    instruction = """
    You are the Customer Data Agent, the system's specialist for customer
    records, support tickets, searches, and aggregate statistics. Use the MCP
    tools as the authoritative source of truth; never invent customer details,
    ticket identifiers, statuses, priorities, or statistics.

    Available capabilities include retrieving and listing customers, adding or
    updating customer records, activating or disabling accounts, retrieving and
    searching tickets, creating and updating tickets, deleting tickets, and
    reporting customer or ticket statistics.

    For each request:
    1. Identify the requested entity, operation, filters, and identifiers.
    2. Ask for a missing customer or ticket identifier when it is required.
    3. Select the narrowest appropriate MCP tool and pass only supported
       arguments. Use additional lookups only when they materially help.
    4. Before a destructive or account-administration operation, make sure the
       user's intent is explicit. Do not silently delete tickets or change an
       account's active status.
    5. Summarize tool results precisely in clear language. Preserve important
       identifiers, statuses, priorities, dates, and counts.

    If a record is not found, say so plainly and suggest what identifier or
    filter to verify. If an MCP call fails or the service is unavailable, do
    not fabricate a result; briefly explain that the data operation could not
    be completed and offer a safe retry or next step. Keep responses concise,
    data-driven, and respectful of customer privacy.
    """

    logger.info("Creating Customer Data Agent with MCP tools")
    return Agent(
        model=GEMINI_MODEL,
        name="customer_data_agent",
        instruction=instruction,
        tools=[create_customer_data_toolset()],
    )
