## Grade: 97 / 100

**Assignment:** Multi-Agent Customer Support (Google ADK + A2A)  
**Attempt:** 1 of 2  ·  **Graded:** 2026-07-27  ·  Commit `28351a5`

### Score breakdown
| Criterion | Max | Earned | Notes |
|-----------|-----|--------|-------|
| mcp_toolset_config | 15 | 15 | Both factories return McpToolset over SseConnectionParams with tool_filter. create_support_toolset excludes exactly the five operations the assignment names as admin/destructive (disable_customer, activate_customer, delete_ticket, add_customer, update_customer). The customer data filter grants 14 tools, which matches the capability list in the TODO 1 comment block in this very file exactly — the scaffold is internally inconsistent here, since README.md:94 instead specifies full access for that role. Both readings are accepted: the canonical rubric constrains only the support toolset. (`agents/shared/mcp_toolset.py:60`) |
| data_agent_instruction | 10 | 10 | Instruction names each tool by its real MCP name with its filter parameters, gives a four-step handling procedure including 'do not guess IDs — use a lookup tool first', and specifies a precise, data-driven response style. (`agents/customer_data_agent/agent.py:42`) |
| mcp_integration | 10 | 10 | tools=[create_customer_data_toolset()] attaches the MCP-backed toolset to the Agent with GEMINI_MODEL. (`agents/customer_data_agent/agent.py:72`) |
| error_handling_instruction | 5 | 5 | Explicit rule: never invent customer or ticket data; if a tool call returns an error or empty result, report that plainly instead of making something up. Paired with the missing-ID guidance at line 56. (`agents/customer_data_agent/agent.py:62`) |
| support_agent | 10 | 10 | Uses create_support_toolset(); the instruction carries a genuinely detailed five-category knowledge base with concrete resolutions (15-minute lockout, card decline vs billing mismatch, narrow the export range), plus ticket-action decision rules. (`agents/support_agent/agent.py:113`) |
| host_agent | 10 | 10 | SequentialAgent('customer_support_host') orders both remote agents through sub_agents. (`agents/host_agent/agent.py:65`) |
| agent_cards | 10 | 9 | All three cards are complete and valid — name, url, description, version, AgentCapabilities(streaming=True), input/output modes, TransportProtocol.jsonrpc and a populated AgentSkill. Card descriptions are the student's own; the AgentSkill descriptions, tags and examples are the scaffold's sample values rather than tailored. (`agents/create_agents.py:41`) |
| a2a_integration | 10 | 10 | Both sub-agents are RemoteA2aAgent instances resolved through AGENT_CARD_WELL_KNOWN_PATH, and the a2a_compat patch is imported at line 27, before RemoteA2aAgent at line 30 — the ordering the scaffold requires. (`agents/host_agent/agent.py:53`) |
| docstrings | 5 | 5 | Documentation is thorough and consistent: across all five implemented modules every scaffold docstring has been replaced with a real description of the finished code, each with a Returns section naming the actual return shape (e.g. create_all_agents documents the dict keys and value structure). No TODO text remains in any implemented module; the 20 that remain sit in the two untouched bonus files. (`agents/create_agents.py:151`) |
| instruction_quality | 5 | 5 | Instructions are specific and internally consistent — the support agent is explicitly told it has no admin operations and should hand those to the data/admin team rather than attempting a workaround, which matches its tool_filter exactly. (`agents/support_agent/agent.py:97`) |
| error_handling_patterns | 5 | 4 | Instruction-level handling is consistent across both agents, including escalation paths for cases the agent cannot fix. Code-level handling is absent: nothing guards McpToolset construction or remote card resolution. (`agents/support_agent/agent.py:50`) |
| code_organization | 5 | 4 | Module layout, section banners and type hints are tidy, but create_all_agents hardcodes ports 10020/10021/10022 instead of importing the *_AGENT_PORT constants from shared.agents_config. (`agents/create_agents.py:162`) |
| Integrity deduction | — | 0 | Provided files unmodified |
| **Total** | **100** | **97** | |

### What went well
- The access policy is stated where a reader will look for it: agents/shared/mcp_toolset.py:72 names every operation the support role is denied, and the filter at line 91 matches that list exactly — so the comment and the code cannot quietly drift apart.
- Documentation hygiene is exemplary: every scaffold docstring was replaced with a description of the real code, and create_all_agents (agents/create_agents.py:152) even documents its return dict's key and value shape. This is the difference between a repo that reads as finished work and one that still reads as an exercise.
- The support knowledge base (agents/support_agent/agent.py:43) contains real domain content — a concrete lockout duration, the distinction between a card decline and a billing-address mismatch, and the observation that most export failures come from oversized ranges — rather than restating the category names.
- Natural-language scope and tool scope agree: agents/support_agent/agent.py:97 tells the agent it has no admin operations and to route those to the data/admin team, which is exactly what its tool_filter enforces.

### What to improve (actionable)
- agents/create_agents.py:162 hardcodes ports 10020/10021/10022. You already import the URLs from shared.agents_config — import CUSTOMER_DATA_AGENT_PORT, SUPPORT_AGENT_PORT and HOST_AGENT_PORT the same way so the cards cannot drift from the servers when config changes.
- The AgentSkill blocks in agents/create_agents.py:54 still carry the scaffold's sample description, tags and examples even though your card descriptions are your own. Tailoring them — especially the examples, which are what an A2A client uses to route — would finish the cards off.
- Add code-level error handling to match the quality of your instruction-level handling. A guard around McpToolset construction, or a check that the remote agent card is reachable before the SequentialAgent runs, would turn an opaque connection failure into a clear message.
- Both bonus routers were left untouched (+25 available). The advanced router in particular is mostly intent classification plus before_agent_callback wiring layered onto the host agent you have already built correctly — given the quality of the rest of this submission, it would have been well within reach.

### Automated checks
- ✅ All required files implemented
- ✅ Provided files unmodified
- ✅ 0/0 output artifacts committed
- ✅ Reflection 1712 words

### Resubmission
You may resubmit **once**. Push fixes to this repo, then notify the instructor; we'll re-grade as **Attempt 2 (final)**. This is attempt 1 of 2.

---
*Graded automatically with Claude Code against the course rubric. Questions → contact the instructor.*
