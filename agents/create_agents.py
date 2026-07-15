"""Agent factory and AgentCard definitions for the A2A support system."""

from shared import a2a_compat  # noqa: F401
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

PREFERRED_TRANSPORT = "JSONRPC"

from customer_data_agent.agent import create_agent as create_customer_data_agent
from host_agent.agent import create_agent as create_host_agent
from shared.agents_config import (
    CUSTOMER_DATA_AGENT_PORT,
    CUSTOMER_DATA_AGENT_URL,
    HOST_AGENT_PORT,
    HOST_AGENT_URL,
    SUPPORT_AGENT_PORT,
    SUPPORT_AGENT_URL,
)
from support_agent.agent import create_agent as create_support_agent


def create_customer_data_agent_card() -> AgentCard:
    """Create the A2A AgentCard for the Customer Data Agent."""
    return AgentCard(
        name="Customer Data Agent",
        url=CUSTOMER_DATA_AGENT_URL,
        description=(
            "Back-office data agent with MCP access to customer records, tickets, "
            "statistics, and administrative customer/ticket operations."
        ),
        version="1.0",
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=["text/plain"],
        default_output_modes=["application/json"],
        preferred_transport=PREFERRED_TRANSPORT,
        skills=[
            AgentSkill(
                id="manage_customer_data",
                name="Manage Customer Data",
                description="Access and manage customer information, ticket records, searches, and support statistics.",
                tags=["customers", "tickets", "data", "database", "mcp"],
                examples=[
                    "Get customer information for ID 5",
                    "List all active customers",
                    "Show open high-priority tickets",
                    "Create a ticket for customer 1 about login issues",
                ],
            )
        ],
    )


def create_support_agent_card() -> AgentCard:
    """Create the A2A AgentCard for the Support Agent."""
    return AgentCard(
        name="Support Agent",
        url=SUPPORT_AGENT_URL,
        description=(
            "Customer-facing support agent that troubleshoots login, password, billing, "
            "performance, feature request, and data export issues using safe MCP tools."
        ),
        version="1.0",
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        preferred_transport=PREFERRED_TRANSPORT,
        skills=[
            AgentSkill(
                id="provide_support",
                name="Provide Customer Support",
                description="Troubleshoot customer issues and create or update support tickets safely.",
                tags=["support", "troubleshooting", "tickets", "help"],
                examples=[
                    "I can't login to my account",
                    "How do I reset my password?",
                    "My payment failed, what should I do?",
                    "The app is slow and timing out",
                ],
            )
        ],
    )


def create_host_agent_card() -> AgentCard:
    """Create the A2A AgentCard for the Host Agent."""
    return AgentCard(
        name="Customer Support Host Agent",
        url=HOST_AGENT_URL,
        description=(
            "Orchestrator agent that delegates to the Customer Data Agent and Support "
            "Agent through A2A to deliver complete support responses."
        ),
        version="1.0",
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        preferred_transport=PREFERRED_TRANSPORT,
        skills=[
            AgentSkill(
                id="comprehensive_support",
                name="Comprehensive Customer Support",
                description="Coordinate account lookup, ticket context, and support guidance across remote agents.",
                tags=["orchestration", "a2a", "support", "data", "coordination"],
                examples=[
                    "I'm having login issues, can you check my account?",
                    "Show me my open tickets and help resolve them",
                    "Check account 5 and create a ticket for billing issues",
                ],
            )
        ],
    )


def create_all_agents() -> dict:
    """Create all agents and AgentCards for local server startup."""
    return {
        "customer_data": {
            "agent": create_customer_data_agent(),
            "card": create_customer_data_agent_card(),
            "port": CUSTOMER_DATA_AGENT_PORT,
        },
        "support": {
            "agent": create_support_agent(),
            "card": create_support_agent_card(),
            "port": SUPPORT_AGENT_PORT,
        },
        "host": {
            "agent": create_host_agent(),
            "card": create_host_agent_card(),
            "port": HOST_AGENT_PORT,
        },
    }
