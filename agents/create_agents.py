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
    """
    Create AgentCard for Customer Data Agent.

    Returns an AgentCard with:
      - name='Customer Data Agent'
      - url=CUSTOMER_DATA_AGENT_URL
      - description describing data management capabilities
      - version='1.0'
      - capabilities=AgentCapabilities(streaming=True)
      - default_input_modes=['text/plain']
      - default_output_modes=['application/json']
      - preferred_transport=TransportProtocol.jsonrpc
      - skills: at least one AgentSkill with relevant examples

    Example AgentSkill:
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
        )
    """
    return AgentCard(
        name='Customer Data Agent',
        url=CUSTOMER_DATA_AGENT_URL,
        description=(
            'Back-office data specialist with full access to the customer '
            'database via MCP. Retrieves and manages customer records, runs the '
            'full ticket lifecycle, and reports account and ticket statistics.'
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
                description=(
                    'Look up and manage customer records and support tickets, '
                    'and report statistics, using the MCP data tools.'
                ),
                tags=['customers', 'tickets', 'data', 'database', 'mcp'],
                examples=[
                    'Get customer information for ID 5',
                    'List all active customers',
                    'Show me all open tickets with high priority',
                    'Create a ticket for customer 1 about a login issue',
                ],
            ),
        ],
    )


# =============================================================================
# TODO 2: Support Agent Card (5 pts)
# =============================================================================

def create_support_agent_card() -> AgentCard:
    """
    Create AgentCard for Support Agent.

    Returns an AgentCard with:
      - name='Support Agent'
      - url=SUPPORT_AGENT_URL
      - description describing support capabilities
      - version='1.0'
      - capabilities=AgentCapabilities(streaming=True)
      - default_input_modes=['text/plain']
      - default_output_modes=['text/plain']
      - preferred_transport=TransportProtocol.jsonrpc
      - skills: at least one AgentSkill with support-related examples

    Example AgentSkill:
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
        )
    """
    return AgentCard(
        name='Support Agent',
        url=SUPPORT_AGENT_URL,
        description=(
            'Customer-facing support specialist. Troubleshoots login, password, '
            'billing, and performance issues, provides step-by-step solutions, '
            'and opens or updates tickets using a support-safe MCP toolset.'
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
                description=(
                    'Diagnose customer issues, give actionable solutions, and '
                    'record them as tickets.'
                ),
                tags=['support', 'troubleshooting', 'solutions', 'help'],
                examples=[
                    "I can't login to my account",
                    'How do I reset my password?',
                    'My payment failed, what should I do?',
                    'The app is really slow today',
                ],
            ),
        ],
    )


# =============================================================================
# TODO 3: Host Agent Card (5 pts)
# =============================================================================

def create_host_agent_card() -> AgentCard:
    """
    Create AgentCard for Host Agent (Orchestrator).

    Returns an AgentCard with:
      - name='Customer Support Host Agent'
      - url=HOST_AGENT_URL
      - description describing orchestration capabilities
      - version='1.0'
      - capabilities=AgentCapabilities(streaming=True)
      - default_input_modes=['text/plain']
      - default_output_modes=['text/plain']
      - preferred_transport=TransportProtocol.jsonrpc
      - skills: at least one AgentSkill describing comprehensive support

    Example AgentSkill:
        AgentSkill(
            id='comprehensive_support',
            name='Comprehensive Customer Support',
            description='Provides complete support by combining data access and solutions',
            tags=['orchestration', 'support', 'data', 'coordination'],
            examples=[
                "I'm having login issues, can you check my account?",
                'Show me my open tickets and help resolve them',
            ],
        )
    """
    return AgentCard(
        name='Customer Support Host Agent',
        url=HOST_AGENT_URL,
        description=(
            'Orchestrator that delivers complete customer support by '
            'coordinating the Customer Data Agent and the Support Agent over '
            'A2A: it looks up the customer account, then resolves the issue.'
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
                description=(
                    'Provides complete support by combining account data access '
                    'with troubleshooting and resolution in a single workflow.'
                ),
                tags=['orchestration', 'support', 'data', 'coordination', 'a2a'],
                examples=[
                    "I'm having login issues, can you check my account and help?",
                    'Show me my open tickets and help resolve them',
                    'Check account 5 and create a ticket for a billing issue',
                ],
            ),
        ],
    )


# =============================================================================
# TODO 4: Factory Function (5 pts)
# =============================================================================

def create_all_agents():
    """
    Create all agents for the customer support system.

    Creates all agents and their cards, returns a dictionary with:
      {
          'customer_data': {
              'agent': <Agent from create_customer_data_agent()>,
              'card': <AgentCard from create_customer_data_agent_card()>,
              'port': 10020,
          },
          'support': {
              'agent': <Agent from create_support_agent()>,
              'card': <AgentCard from create_support_agent_card()>,
              'port': 10021,
          },
          'host': {
              'agent': <Agent from create_host_agent()>,
              'card': <AgentCard from create_host_agent_card()>,
              'port': 10022,
          },
      }

    Returns:
        Dictionary with all agents and their cards
    """
    from shared.agents_config import (
        CUSTOMER_DATA_AGENT_PORT,
        SUPPORT_AGENT_PORT,
        HOST_AGENT_PORT,
    )

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
