"""
Customer Data Agent
Root agent declaration for ADK Web testing

The root agent is created at import time for ADK Web.
"""

from .agent import create_agent

# Root agent required for ADK Web.
root_agent = create_agent()
