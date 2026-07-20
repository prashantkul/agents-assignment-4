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
    CUSTOMER_DATA_AGENT_URL,
    SUPPORT_AGENT_URL,
    HOST_AGENT_URL,
)

# Import agent creation functions
from customer_data_agent.agent import create_agent as create_customer_data_agent
from support_agent.agent import create_agent as create_support_agent
from host_agent.agent import create_agent as create_host_agent


# =============================================================================
# TODO 1: Customer Data Agent Card (5 pts)
# =============================================================================

def create_customer_data_agent_card() -> AgentCard:
    """Create the A2A discovery AgentCard for the Customer Data Agent."""
    return AgentCard(
        name='Customer Data Agent',
        url=CUSTOMER_DATA_AGENT_URL,
        description=(
            'Manages customer and ticket data: lookups, creation, updates, '
            'and statistics via the MCP-backed customer support database.'
        ),
        version='1.0',
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=['text/plain'],
        default_output_modes=['application/json'],
        preferred_transport=TransportProtocol.jsonrpc,
        skills=[
            AgentSkill(
                id='manage_customer_data',
                name='Manage Customer Data',
                description='Access and manage customer information and tickets',
                tags=['customers', 'tickets', 'data', 'database', 'mcp'],
                examples=[
                    'Get customer information for ID 5',
                    'List all active customers',
                    'Show me all open tickets with high priority',
                ],
            ),
        ],
    )


# =============================================================================
# TODO 2: Support Agent Card (5 pts)
# =============================================================================

def create_support_agent_card() -> AgentCard:
    """Create the A2A discovery AgentCard for the Support Agent."""
    return AgentCard(
        name='Support Agent',
        url=SUPPORT_AGENT_URL,
        description=(
            'Provides customer support and troubleshooting for login, '
            'payment, performance, and data export issues, creating and '
            'updating tickets as needed.'
        ),
        version='1.0',
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=['text/plain'],
        default_output_modes=['text/plain'],
        preferred_transport=TransportProtocol.jsonrpc,
        skills=[
            AgentSkill(
                id='provide_support',
                name='Provide Customer Support',
                description='Troubleshoot issues and provide solutions',
                tags=['support', 'troubleshooting', 'solutions', 'help'],
                examples=[
                    "I can't login to my account",
                    'How do I reset my password?',
                    'My payment failed, what should I do?',
                ],
            ),
        ],
    )


# =============================================================================
# TODO 3: Host Agent Card (5 pts)
# =============================================================================

def create_host_agent_card() -> AgentCard:
    """Create the A2A discovery AgentCard for the Host Agent (Orchestrator)."""
    return AgentCard(
        name='Customer Support Host Agent',
        url=HOST_AGENT_URL,
        description=(
            'Orchestrates the Customer Data Agent and Support Agent over '
            'A2A to provide comprehensive customer support that combines '
            'account/ticket data access with troubleshooting solutions.'
        ),
        version='1.0',
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=['text/plain'],
        default_output_modes=['text/plain'],
        preferred_transport=TransportProtocol.jsonrpc,
        skills=[
            AgentSkill(
                id='comprehensive_support',
                name='Comprehensive Customer Support',
                description='Provides complete support by combining data access and solutions',
                tags=['orchestration', 'support', 'data', 'coordination'],
                examples=[
                    "I'm having login issues, can you check my account?",
                    'Show me my open tickets and help resolve them',
                ],
            ),
        ],
    )


# =============================================================================
# TODO 4: Factory Function (5 pts)
# =============================================================================

def create_all_agents() -> dict[str, dict[str, object]]:
    """
    Create all agents for the customer support system.

    Returns:
        A dict keyed by agent id ('customer_data', 'support', 'host'), each
        mapping to {'agent': Agent, 'card': AgentCard, 'port': int}.
    """
    return {
        'customer_data': {
            'agent': create_customer_data_agent(),
            'card': create_customer_data_agent_card(),
            'port': 10020,
        },
        'support': {
            'agent': create_support_agent(),
            'card': create_support_agent_card(),
            'port': 10021,
        },
        'host': {
            'agent': create_host_agent(),
            'card': create_host_agent_card(),
            'port': 10022,
        },
    }
