"""
Part 3: Host Agent / Orchestrator (20 points)

Create a SequentialAgent that coordinates between Customer Data Agent and Support Agent
using the A2A (Agent-to-Agent) protocol.

This is the core of the assignment: connecting remote agents via A2A.

Architecture:
  Host Agent (SequentialAgent)
    -> RemoteA2aAgent("customer_data") -- calls Customer Data Agent via A2A
    -> RemoteA2aAgent("support_specialist") -- calls Support Agent via A2A

Requirements:
  - Import and apply the A2A compatibility patch (CRITICAL) (2 pts)
  - Create RemoteA2aAgent for Customer Data Agent (6 pts)
  - Create RemoteA2aAgent for Support Agent (6 pts)
  - Create SequentialAgent combining both remote agents (6 pts)

Key concepts:
  - RemoteA2aAgent wraps a remote agent as a local sub-agent
  - agent_card URL = agent_url + AGENT_CARD_WELL_KNOWN_PATH
  - SequentialAgent runs sub-agents in order, passing context between them
"""

import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Requirement (2 pts): Apply A2A compatibility patch BEFORE importing RemoteA2aAgent.
# This fixes an import issue between google-adk and a2a-sdk versions.
from shared import a2a_compat  # noqa: F401

from google.adk.agents import SequentialAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH
from shared.agents_config import (
    CUSTOMER_DATA_AGENT_URL,
    SUPPORT_AGENT_URL,
)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [HOST_AGENT] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Sub-agent names must match the architecture diagram above.
CUSTOMER_DATA_SUB_AGENT_NAME = 'customer_data'
SUPPORT_SUB_AGENT_NAME = 'support_specialist'
HOST_AGENT_NAME = 'customer_support_host'


def _agent_card_url(base_url: str) -> str:
    """Build the well-known AgentCard discovery URL for a remote agent."""
    return f'{base_url}{AGENT_CARD_WELL_KNOWN_PATH}'


def create_agent() -> SequentialAgent:
    """Create the Host Agent orchestrator.

    Workflow (sequential — context passes from step 1 to step 2):
      1. Customer Data Agent: look up customer/ticket data via A2A + MCP
      2. Support Agent: provide troubleshooting using prior context + MCP tools

    Returns:
        Configured SequentialAgent with two RemoteA2aAgent sub-agents.
    """
    logger.info("Creating Host Agent (SequentialAgent orchestrator)")

    # Requirement (6 pts): RemoteA2aAgent for Customer Data Agent (port 10020).
    remote_customer_data = RemoteA2aAgent(
        name=CUSTOMER_DATA_SUB_AGENT_NAME,
        description='Access customer and ticket data from MCP server',
        agent_card=_agent_card_url(CUSTOMER_DATA_AGENT_URL),
    )

    # Requirement (6 pts): RemoteA2aAgent for Support Agent (port 10021).
    remote_support = RemoteA2aAgent(
        name=SUPPORT_SUB_AGENT_NAME,
        description='Provide customer support and troubleshooting solutions',
        agent_card=_agent_card_url(SUPPORT_AGENT_URL),
    )

    # Requirement (6 pts): SequentialAgent runs data lookup first, then support.
    return SequentialAgent(
        name=HOST_AGENT_NAME,
        sub_agents=[remote_customer_data, remote_support],
    )
