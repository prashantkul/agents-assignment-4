"""
Part 4: Agent Factory and AgentCard Definitions (20 points)

Create AgentCards for A2A discovery and a factory function to create all agents.

AgentCards are the A2A protocol's way of advertising agent capabilities.
They include metadata like name, URL, description, skills, and examples.

Requirements:
  - create_customer_data_agent_card() returns valid AgentCard (5 pts)
  - create_support_agent_card() returns valid AgentCard (5 pts)
  - create_host_agent_card() returns valid AgentCard (5 pts)
  - create_all_agents() returns dict with all agents and cards (5 pts)

Each AgentCard needs:
  - name: Human-readable agent name
  - url: The agent's server URL
  - description: What the agent does
  - version: Version string (e.g., '1.0')
  - capabilities: AgentCapabilities(streaming=True)
  - default_input_modes: ['text/plain']
  - default_output_modes: ['text/plain'] or ['application/json']
  - preferred_transport: TransportProtocol.jsonrpc
  - skills: List of AgentSkill with id, name, description, tags, examples
"""

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    TransportProtocol,
)
from shared.agents_config import (
    CUSTOMER_DATA_AGENT_PORT,
    CUSTOMER_DATA_AGENT_URL,
    HOST_AGENT_PORT,
    HOST_AGENT_URL,
    SUPPORT_AGENT_PORT,
    SUPPORT_AGENT_URL,
)

# Import agent creation functions
from customer_data_agent.agent import create_agent as create_customer_data_agent
from support_agent.agent import create_agent as create_support_agent
from host_agent.agent import create_agent as create_host_agent


# =============================================================================
# Customer Data Agent Card
# =============================================================================

def create_customer_data_agent_card() -> AgentCard:
    """Create the A2A discovery card for the Customer Data Agent."""
    return AgentCard(
        name="Customer Data Agent",
        url=CUSTOMER_DATA_AGENT_URL,
        description=(
            "Retrieves and manages customer records and support tickets through "
            "the MCP data service, including searches and aggregate statistics."
        ),
        version="1.0",
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=["text/plain"],
        default_output_modes=["application/json"],
        preferred_transport=TransportProtocol.jsonrpc,
        skills=[
            AgentSkill(
                id="manage_customer_data",
                name="Manage Customer Data",
                description=(
                    "Access and manage customer information, account state, "
                    "tickets, searches, and support statistics."
                ),
                tags=["customers", "tickets", "data", "database", "mcp"],
                examples=[
                    "Get customer information for ID 5",
                    "List all active customers",
                    "Show all open high-priority tickets",
                    "Create a login issue ticket for customer 1",
                ],
            )
        ],
    )


# =============================================================================
# Support Agent Card
# =============================================================================

def create_support_agent_card() -> AgentCard:
    """Create the A2A discovery card for the Support Agent."""
    return AgentCard(
        name="Support Agent",
        url=SUPPORT_AGENT_URL,
        description=(
            "Provides empathetic troubleshooting for account, billing, "
            "performance, feature-request, and data-export issues using "
            "support-safe customer and ticket tools."
        ),
        version="1.0",
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        preferred_transport=TransportProtocol.jsonrpc,
        skills=[
            AgentSkill(
                id="provide_support",
                name="Provide Customer Support",
                description=(
                    "Diagnose customer issues, recommend solutions, and create "
                    "or update support tickets when tracking is needed."
                ),
                tags=[
                    "support",
                    "troubleshooting",
                    "solutions",
                    "tickets",
                    "help",
                ],
                examples=[
                    "I can't log in to my account",
                    "How do I reset my password?",
                    "My payment failed. What should I do?",
                    "The application is loading very slowly",
                ],
            )
        ],
    )


# =============================================================================
# Host Agent Card
# =============================================================================

def create_host_agent_card() -> AgentCard:
    """Create the A2A discovery card for the host orchestrator."""
    return AgentCard(
        name="Customer Support Host Agent",
        url=HOST_AGENT_URL,
        description=(
            "Coordinates the Customer Data and Support agents over A2A to "
            "provide data-informed, end-to-end customer assistance."
        ),
        version="1.0",
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        preferred_transport=TransportProtocol.jsonrpc,
        skills=[
            AgentSkill(
                id="comprehensive_support",
                name="Comprehensive Customer Support",
                description=(
                    "Combines customer and ticket context with troubleshooting "
                    "guidance in a coordinated support workflow."
                ),
                tags=["orchestration", "support", "data", "a2a", "coordination"],
                examples=[
                    "I'm having login issues; can you check my account?",
                    "Show my open tickets and help me resolve them",
                    "Check customer 5 and create a billing issue ticket",
                ],
            )
        ],
    )


# =============================================================================
# Agent Factory
# =============================================================================

def create_all_agents() -> dict[str, dict[str, object]]:
    """Create every agent together with its discovery card and port."""
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
