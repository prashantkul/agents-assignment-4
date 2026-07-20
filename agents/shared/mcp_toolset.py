"""
Part 1: McpToolset Configuration for Google ADK Agents (20 points)

Google ADK's McpToolset auto-discovers all tools from an MCP server and makes them
available to ADK agents — no manual wrapper functions needed. Your job is to configure
toolsets with appropriate `tool_filter` lists so each agent only gets the tools it needs.

The MCP server exposes these 15 tools (see mcp_server/app.py):
  Customer: get_customer, list_customers, add_customer, update_customer,
            disable_customer, activate_customer
  Ticket:   get_ticket, list_tickets, create_ticket, update_ticket_status,
            update_ticket_priority, delete_ticket
  Stats:    get_ticket_stats, get_customer_stats, search_tickets

You must implement two toolset factory functions that return McpToolset instances
with `tool_filter` selecting only the tools appropriate for each agent's role.

Requirements for each toolset:
  - Return a McpToolset connected to the MCP server via SSE
  - Use tool_filter to select only relevant tools
  - Customer data toolset: broad data access (lookup, list, create, update, stats)
  - Support toolset: support-safe tools only (exclude admin ops like disable/delete)

Grading (20 points):
  - Both toolsets return McpToolset instances: 5 pts
  - tool_filter lists are correct and non-empty: 5 pts
  - Customer data toolset includes core tools: 5 pts
  - Support toolset excludes admin/destructive tools: 5 pts
"""

import os
import logging

from google.adk.tools.mcp_tool import McpToolset, SseConnectionParams
from shared.agents_config import MCP_SERVER_URL

# Setup logging
logger = logging.getLogger(__name__)

# SSE endpoint URL for the MCP server
MCP_SSE_URL = f"{MCP_SERVER_URL}/sse"
logger.info(f"[MCP_TOOLSET] MCP SSE URL: {MCP_SSE_URL}")


# =============================================================================
# EXAMPLE: Full toolset with no filter (all 15 tools) - for reference only
# =============================================================================
def create_full_toolset() -> McpToolset:
    """Create an McpToolset with ALL MCP server tools (no filter).

    This is provided as a reference. In practice, agents should use
    filtered toolsets so each agent only has access to the tools it needs.

    Returns:
        McpToolset: Toolset connected to MCP server with all tools
    """
    logger.info("[MCP_TOOLSET] Creating full toolset (no filter)")
    return McpToolset(
        connection_params=SseConnectionParams(url=MCP_SSE_URL),
    )


# =============================================================================
# TODO 1: Customer Data Toolset (10 pts)
# =============================================================================
# Create a toolset for the Customer Data Agent with tool_filter selecting
# data-access and management tools.
#
# The customer data agent needs tools for:
#   - Looking up customers (get_customer, list_customers)
#   - Managing customer records (add_customer, update_customer)
#   - Ticket operations (get_ticket, list_tickets, create_ticket,
#     update_ticket_status, update_ticket_priority)
#   - Statistics and search (get_ticket_stats, get_customer_stats, search_tickets)
#   - Admin operations (disable_customer, activate_customer)
#
# Hint:
#   return McpToolset(
#       connection_params=SseConnectionParams(url=MCP_SSE_URL),
#       tool_filter=[...list of tool name strings...],
#   )

# Full data-plane access: every tool the MCP server exposes, including the
# admin/destructive ones (disable/activate customer, delete ticket, add/update
# customer). The Customer Data Agent is the trusted back-office role, so it gets
# the complete surface. We list all 15 explicitly rather than passing no filter:
# an explicit allow-list is self-documenting and fails closed if the server ever
# grows a tool this role should not automatically inherit.
CUSTOMER_DATA_TOOLS = [
    # Customer records
    "get_customer", "list_customers", "add_customer", "update_customer",
    "disable_customer", "activate_customer",
    # Ticket lifecycle
    "get_ticket", "list_tickets", "create_ticket",
    "update_ticket_status", "update_ticket_priority", "delete_ticket",
    # Analytics / search
    "get_ticket_stats", "get_customer_stats", "search_tickets",
]


def create_customer_data_toolset() -> McpToolset:
    """Create an McpToolset for the Customer Data Agent.

    Includes tools for customer lookup, ticket management, statistics,
    and admin operations. This agent has broad data access (all 15 tools).

    Returns:
        McpToolset: Toolset with the full set of customer data tools.
    """
    logger.info(
        "[MCP_TOOLSET] Creating customer data toolset (%d tools)",
        len(CUSTOMER_DATA_TOOLS),
    )
    return McpToolset(
        connection_params=SseConnectionParams(url=MCP_SSE_URL),
        tool_filter=CUSTOMER_DATA_TOOLS,
    )


# =============================================================================
# TODO 2: Support Toolset (10 pts)
# =============================================================================
# Create a toolset for the Support Agent with tool_filter selecting only
# support-appropriate tools. The support agent should NOT have access to
# destructive or admin operations.
#
# The support agent needs tools for:
#   - Looking up customers (get_customer, list_customers)
#   - Viewing tickets (get_ticket, list_tickets, search_tickets)
#   - Creating/updating tickets (create_ticket, update_ticket_status,
#     update_ticket_priority)
#   - Statistics (get_ticket_stats, get_customer_stats)
#
# The support agent should NOT have:
#   - disable_customer (admin only)
#   - activate_customer (admin only)
#   - delete_ticket (destructive)
#   - add_customer (admin only)
#   - update_customer (admin only)
#
# Hint:
#   return McpToolset(
#       connection_params=SseConnectionParams(url=MCP_SSE_URL),
#       tool_filter=[...list of support-safe tool names...],
#   )

# Support-safe subset: the same MCP server, a narrower capability boundary.
# The Support Agent talks directly to customers, so it can read anything and
# manage tickets, but it MUST NOT be able to mutate the customer roster or
# destroy data. These five are withheld:
#   add_customer, update_customer  -> account admin, not a support action
#   disable_customer, activate_customer -> account state changes, admin only
#   delete_ticket                  -> destructive, irreversible
# This is the tool_filter enforcing least privilege at the protocol layer:
# the excluded tools are never even discovered by this agent, so no amount of
# clever prompting can make it call them.
SUPPORT_SAFE_TOOLS = [
    # Read-only lookups
    "get_customer", "list_customers",
    # Ticket handling (create + progress, but never delete)
    "get_ticket", "list_tickets", "create_ticket",
    "update_ticket_status", "update_ticket_priority",
    # Analytics / search
    "get_ticket_stats", "get_customer_stats", "search_tickets",
]


def create_support_toolset() -> McpToolset:
    """Create an McpToolset for the Support Agent.

    Includes only support-safe tools: lookups, ticket management, and stats.
    Excludes admin operations (disable/activate customer, delete ticket,
    add/update customer) so a customer-facing agent cannot mutate accounts
    or destroy records.

    Returns:
        McpToolset: Toolset with support-safe tools only (10 tools).
    """
    logger.info(
        "[MCP_TOOLSET] Creating support toolset (%d tools, admin ops excluded)",
        len(SUPPORT_SAFE_TOOLS),
    )
    return McpToolset(
        connection_params=SseConnectionParams(url=MCP_SSE_URL),
        tool_filter=SUPPORT_SAFE_TOOLS,
    )
