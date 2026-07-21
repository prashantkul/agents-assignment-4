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
    CUSTOMER_DATA_AGENT_PORT,
    SUPPORT_AGENT_PORT,
    HOST_AGENT_PORT,
)

from customer_data_agent.agent import create_agent as create_customer_data_agent
from support_agent.agent import create_agent as create_support_agent
from host_agent.agent import create_agent as create_host_agent


def create_customer_data_agent_card() -> AgentCard:
    """Create AgentCard for Customer Data Agent.

    Returns:
        AgentCard advertising data management capabilities.
    """
    return AgentCard(
        name='Customer Data Agent',
        url=CUSTOMER_DATA_AGENT_URL,
        description=(
            'Specialized agent for customer and ticket data management. '
            'Retrieves, creates, and updates customer records and support tickets '
            'via MCP database tools. Provides statistics and search across the '
            'customer support database.'
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


def create_support_agent_card() -> AgentCard:
    """Create AgentCard for Support Agent.

    Returns:
        AgentCard advertising troubleshooting and support capabilities.
    """
    return AgentCard(
        name='Support Agent',
        url=SUPPORT_AGENT_URL,
        description=(
            'Customer-facing support specialist that troubleshoots login issues, '
            'password resets, billing problems, and performance issues. Uses MCP '
            'tools to look up account data and manage support tickets with an '
            'empathetic, solution-oriented approach.'
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


def create_host_agent_card() -> AgentCard:
    """Create AgentCard for Host Agent (Orchestrator).

    Returns:
        AgentCard advertising orchestration capabilities.
    """
    return AgentCard(
        name='Customer Support Host Agent',
        url=HOST_AGENT_URL,
        description=(
            'Orchestrator agent that coordinates the customer support workflow. '
            'Sequentially delegates to the Customer Data Agent for database lookups '
            'and the Support Agent for troubleshooting guidance, combining data '
            'access with empathetic customer support via A2A protocol.'
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


def create_all_agents():
    """Create all agents for the customer support system.

    Returns:
        Dictionary with all agents, their AgentCards, and server ports.
    """
    return {
        'customer_data': {
            'agent': create_customer_data_agent(),
            'card': create_customer_data_agent_card(),
            'port': CUSTOMER_DATA_AGENT_PORT,
        },
        'support': {
            'agent': create_support_agent(),
            'card': create_support_agent_card(),
            'port': SUPPORT_AGENT_PORT,
        },
        'host': {
            'agent': create_host_agent(),
            'card': create_host_agent_card(),
            'port': HOST_AGENT_PORT,
        },
    }
