## Grade: 97 / 100

**Assignment:** Multi-Agent Customer Support (Google ADK + A2A)  
**Attempt:** 1 of 2  ·  **Graded:** 2026-07-27  ·  Commit `5b9d2e6`

### Score breakdown
| Criterion | Max | Earned | Notes |
|-----------|-----|--------|-------|
| mcp_toolset_config | 15 | 15 | Both factories return McpToolset over SseConnectionParams with explicit tool_filter lists. create_support_toolset excludes exactly the five operations the assignment names as admin/destructive (disable_customer, activate_customer, delete_ticket, add_customer, update_customer), and the customer data toolset grants the full surface, which is what README.md:94 specifies for that role ('Broad data access ... All 15 tools (full access)'). (`agents/shared/mcp_toolset.py:34`) |
| data_agent_instruction | 10 | 9 | CUSTOMER_DATA_INSTRUCTION establishes the agent as authoritative source of truth, lists four capability groups, and gives six numbered operating rules including a no-fabrication clause. Compact but complete; capability descriptions are grouped rather than tied to specific tool names. (`agents/customer_data_agent/agent.py:21`) |
| mcp_integration | 10 | 10 | tools=[create_customer_data_toolset()] attaches the MCP-backed toolset to the Agent with GEMINI_MODEL. (`agents/customer_data_agent/agent.py:57`) |
| error_handling_instruction | 5 | 5 | Operating rule 4 requires explaining the issue clearly and suggesting a safe next step when a tool fails or returns no results; rule 3 handles missing identifiers and rule 6 forbids inventing records. (`agents/customer_data_agent/agent.py:42`) |
| support_agent | 10 | 10 | Uses create_support_toolset(); the instruction opens by stating exactly which administrative and destructive operations the agent cannot perform (line 28), then covers six knowledge-base categories and a six-step response structure. (`agents/support_agent/agent.py:66`) |
| host_agent | 10 | 10 | SequentialAgent('customer_support_host') orders both remote agents and carries a description explaining the data-then-support sequencing rationale. (`agents/host_agent/agent.py:39`) |
| agent_cards | 10 | 10 | All three cards are complete — name, url, description, version, AgentCapabilities(streaming=True), input/output modes, transport and a populated AgentSkill. Descriptions, skill descriptions, tags and examples are all tailored to this system rather than copied from the scaffold samples. Note: preferred_transport uses the string constant 'JSONRPC' (line 6) rather than TransportProtocol.jsonrpc; the value is equivalent, so this is a style point, not a defect. (`agents/create_agents.py:23`) |
| a2a_integration | 10 | 10 | Both sub-agents are RemoteA2aAgent instances resolved through AGENT_CARD_WELL_KNOWN_PATH, with a2a_compat imported at line 9 before RemoteA2aAgent at line 12 — the ordering the scaffold requires. (`agents/host_agent/agent.py:27`) |
| docstrings | 5 | 4 | Every module and function carries its own docstring and no scaffold TODO text survives anywhere — good hygiene. They are one-liners throughout, so return shapes and parameters are left undocumented (create_all_agents at create_agents.py:114 returns a nested dict whose structure a reader has to infer from the body). (`agents/shared/mcp_toolset.py:32`) |
| instruction_quality | 5 | 5 | Instructions are tight and internally consistent. The support agent's stated limitations match its tool_filter exactly, and the billing playbook adds a sensible safety rule — never request full card numbers. (`agents/support_agent/agent.py:28`) |
| error_handling_patterns | 5 | 4 | Both agents carry consistent instruction-level failure guidance, and the support response structure ends with an explicit step for when a tool is unavailable. No code-level guarding around McpToolset construction or remote card resolution. (`agents/support_agent/agent.py:55`) |
| code_organization | 5 | 5 | Excellent configuration discipline: create_all_agents imports CUSTOMER_DATA_AGENT_PORT, SUPPORT_AGENT_PORT and HOST_AGENT_PORT from shared.agents_config instead of hardcoding them, tool lists are hoisted to named constants, and instructions live at module level separate from the factory functions. (`agents/create_agents.py:119`) |
| Integrity deduction | — | 0 | Provided files unmodified |
| **Total** | **100** | **97** | |

### What went well
- Configuration handling is exactly right: create_all_agents (agents/create_agents.py:119) imports CUSTOMER_DATA_AGENT_PORT, SUPPORT_AGENT_PORT and HOST_AGENT_PORT from shared.agents_config instead of hardcoding 10020/10021/10022, so the agent cards cannot drift from the servers when config changes.
- Hoisting the tool lists into ALL_MCP_TOOLS and SUPPORT_SAFE_TOOLS (agents/shared/mcp_toolset.py:12) makes the access policy readable at a glance and gives you one place to change it — a nice structural instinct.
- The agent cards are thoroughly tailored — descriptions, skill descriptions, tags and examples were all written for this system rather than carried over from the scaffold's samples, which is what makes a card useful for A2A discovery.
- The submission achieves complete coverage in noticeably less code than the scaffold's structure suggests is needed, with no scaffold TODO text left anywhere — the repo reads as finished work rather than a filled-in exercise.

### What to improve (actionable)
- Expand the one-line docstrings where the return shape is non-obvious. create_all_agents (agents/create_agents.py:114) returns a dict of dicts keyed by role with 'agent', 'card' and 'port' entries — documenting that shape costs two lines and saves the next reader from reverse-engineering the body.
- agents/create_agents.py:6 defines PREFERRED_TRANSPORT = 'JSONRPC' as a bare string. The value is correct, but importing TransportProtocol from a2a.types and using TransportProtocol.jsonrpc gets you type checking and protects against a typo silently producing an invalid card.
- Add code-level error handling to complement the instruction-level rules — a guard around McpToolset construction, or a reachability check on the remote agent cards, so an unreachable MCP server or a stopped peer agent surfaces one clear message.
- Both bonus routers were left untouched (+25 available). Given how cleanly you factored the core system, the advanced router — intent classification plus before_agent_callback wiring on the host agent you already have — would have been a natural extension.

### Automated checks
- ✅ All required files implemented
- ✅ Provided files unmodified
- ✅ 0/0 output artifacts committed
- ✅ Reflection 694 words

### Resubmission
You may resubmit **once**. Push fixes to this repo, then notify the instructor; we'll re-grade as **Attempt 2 (final)**. This is attempt 1 of 2.

---
*Graded automatically with Claude Code against the course rubric. Questions → contact the instructor.*


---
<sub>🔎 **Autograder record** — attempt 1 of 2 · graded at commit `5b9d2e6` · delivered 2026-07-27T07:01:06Z. Commits pushed to `main` after this timestamp are treated as a resubmission.</sub>
