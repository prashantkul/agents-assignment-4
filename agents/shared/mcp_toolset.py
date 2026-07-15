"""McpToolset configuration for Assignment 4 agents."""

import logging

from google.adk.tools.mcp_tool import McpToolset, SseConnectionParams

from shared.agents_config import MCP_SERVER_URL

logger = logging.getLogger(__name__)
MCP_SSE_URL = f"{MCP_SERVER_URL}/sse"

ALL_MCP_TOOLS = [
    "get_customer", "list_customers", "add_customer", "update_customer",
    "disable_customer", "activate_customer", "get_ticket", "list_tickets",
    "create_ticket", "update_ticket_status", "update_ticket_priority",
    "delete_ticket", "get_ticket_stats", "get_customer_stats", "search_tickets",
]

SUPPORT_SAFE_TOOLS = [
    "get_customer", "list_customers", "get_ticket", "list_tickets",
    "create_ticket", "update_ticket_status", "update_ticket_priority",
    "get_ticket_stats", "get_customer_stats", "search_tickets",
]


def create_full_toolset() -> McpToolset:
    """Create an McpToolset with all MCP tools available."""
    return McpToolset(connection_params=SseConnectionParams(url=MCP_SSE_URL))


def create_customer_data_toolset() -> McpToolset:
    """Create the broad Customer Data Agent MCP toolset with all 15 tools."""
    logger.info("Creating customer data toolset")
    return McpToolset(
        connection_params=SseConnectionParams(url=MCP_SSE_URL),
        tool_filter=ALL_MCP_TOOLS,
    )


def create_support_toolset() -> McpToolset:
    """Create the support-safe MCP toolset without admin/destructive tools."""
    logger.info("Creating support-safe toolset")
    return McpToolset(
        connection_params=SseConnectionParams(url=MCP_SSE_URL),
        tool_filter=SUPPORT_SAFE_TOOLS,
    )
