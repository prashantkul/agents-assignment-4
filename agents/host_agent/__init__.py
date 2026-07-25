"""
Host Agent (Orchestrator)
Root agent declaration for ADK Web testing

Available implementations:
1. agent.py - Basic SequentialAgent (default)
2. advanced_router_agent.py - Dynamic routing with callbacks (BONUS)
3. parallel_router_agent.py - Parallel execution with synthesis (BONUS)

Switch implementations via HOST_AGENT_MODE in .env:
- basic (default)
- advanced
- parallel
"""

import os

AGENT_MODE = os.getenv("HOST_AGENT_MODE", "basic")

if AGENT_MODE == "advanced":
    from .advanced_router_agent import create_agent
    print("[HOST_AGENT] Using ADVANCED router with dynamic routing")
elif AGENT_MODE == "parallel":
    from .parallel_router_agent import create_agent
    print("[HOST_AGENT] Using PARALLEL router with concurrent execution")
else:
    from .agent import create_agent
    print("[HOST_AGENT] Using BASIC sequential router")

root_agent = create_agent()
