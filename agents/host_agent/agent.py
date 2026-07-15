"""Host Agent / A2A Orchestrator for Assignment 4."""

import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import a2a_compat  # noqa: F401
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents import SequentialAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

from shared.agents_config import CUSTOMER_DATA_AGENT_URL, SUPPORT_AGENT_URL

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [HOST_AGENT] %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def create_agent() -> SequentialAgent:
    """Create the A2A Host Agent with remote customer-data and support agents."""
    logger.info("Creating Host Agent with RemoteA2aAgent sub-agents")
    remote_customer_data = RemoteA2aAgent(
        name="customer_data",
        description="Access customer and ticket data from the MCP-backed Customer Data Agent.",
        agent_card=f"{CUSTOMER_DATA_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
    )

    remote_support = RemoteA2aAgent(
        name="support_specialist",
        description="Provide customer-facing troubleshooting and support guidance.",
        agent_card=f"{SUPPORT_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
    )

    return SequentialAgent(
        name="customer_support_host",
        description=(
            "Sequential host orchestrator that first gathers account/ticket data "
            "and then asks the support specialist to provide safe customer guidance."
        ),
        sub_agents=[remote_customer_data, remote_support],
    )
