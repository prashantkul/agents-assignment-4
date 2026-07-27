## Grade: 100 / 100

**Assignment:** Multi-Agent Customer Support (Google ADK + A2A)  
**Attempt:** 1 of 2  ·  **Graded:** 2026-07-27  ·  Commit `196b540`

### Score breakdown
| Criterion | Max | Earned | Notes |
|-----------|-----|--------|-------|
| mcp_toolset_config | 15 | 15 | Both factories return McpToolset over SseConnectionParams with explicit tool_filter lists. create_support_toolset excludes exactly the five operations the assignment names as admin/destructive (disable_customer, activate_customer, delete_ticket, add_customer, update_customer), and the customer data toolset grants the full surface, which is what README.md:94 specifies for that role ('Broad data access ... All 15 tools (full access)'). (`agents/shared/mcp_toolset.py:92`) |
| data_agent_instruction | 10 | 10 | Instruction names the role, enumerates capabilities, gives a 5-step request workflow, forbids fabricating records, and requires explicit intent before destructive/admin operations. (`agents/customer_data_agent/agent.py:48`) |
| mcp_integration | 10 | 10 | tools=[create_customer_data_toolset()] attaches the MCP-backed toolset to the Agent alongside GEMINI_MODEL. (`agents/customer_data_agent/agent.py:82`) |
| error_handling_instruction | 5 | 5 | Explicit not-found and MCP-failure guidance: state the failure plainly, do not fabricate a result, offer a safe retry or next step. (`agents/customer_data_agent/agent.py:70`) |
| support_agent | 10 | 10 | Uses create_support_toolset(); instruction carries a five-domain knowledge base (login, billing, performance, feature requests, exports), a 6-step handling workflow, and escalation criteria. (`agents/support_agent/agent.py:105`) |
| host_agent | 10 | 10 | SequentialAgent('customer_support_host') composes the two remote agents in order via sub_agents. (`agents/host_agent/agent.py:74`) |
| agent_cards | 10 | 10 | All three AgentCards set name, url, description, version, AgentCapabilities(streaming=True), input/output modes, TransportProtocol.jsonrpc, and a populated AgentSkill with tags and examples. (`agents/create_agents.py:54`) |
| a2a_integration | 10 | 10 | Both sub-agents are RemoteA2aAgent instances resolved via agent_card = URL + AGENT_CARD_WELL_KNOWN_PATH; the a2a_compat patch is imported before RemoteA2aAgent (line 37). No direct function calls. (`agents/host_agent/agent.py:59`) |
| docstrings | 5 | 5 | Every public function across all five modules carries a docstring; the toolset factories document Returns. (`agents/shared/mcp_toolset.py:83`) |
| instruction_quality | 5 | 5 | Instructions are scoped, ordered, and role-appropriate; the support agent is explicitly told not to claim access to admin or destructive operations, matching its tool_filter. (`agents/support_agent/agent.py:56`) |
| error_handling_patterns | 5 | 4 | Graceful-degradation guidance is consistent across both agents and the parallel synthesizer. Code-level handling is thinner: the toolset factories log but do not guard MCP connection construction. (`agents/support_agent/agent.py:94`) |
| code_organization | 5 | 5 | Clean separation: toolsets in shared/, one module per agent, cards and the factory centralised in create_all_agents() keyed by role with agent/card/port. (`agents/create_agents.py:172`) |
| _bonus_ | +25 | +24 | |
| Integrity deduction | — | 0 | Provided files unmodified |
| **Total** | **100** | **100** | |

### What went well
- Tool scoping is genuinely role-aware: the support toolset in agents/shared/mcp_toolset.py:154 omits every admin and destructive operation, and the support instruction (agents/support_agent/agent.py:84) reinforces that boundary in natural language so the model does not promise capabilities it lacks.
- The A2A wiring is textbook — agents/host_agent/agent.py:37 applies the compatibility patch before importing RemoteA2aAgent, and both sub-agents are resolved through AGENT_CARD_WELL_KNOWN_PATH rather than hardcoded card paths.
- Both bonus routers are real implementations, not sketches: the advanced router does keyword intent analysis feeding before_agent_callback skips, and the parallel router uses output_key plus a state-reading synthesizer instruction.
- Instructions are unusually disciplined — each one gives the model an ordered workflow, an explicit anti-fabrication rule, and a defined failure behaviour rather than a single paragraph of role text.

### What to improve (actionable)
- create_router_instruction (agents/host_agent/advanced_router_agent.py:205) has two coupled fragilities worth fixing together. It reads the query via getattr(readonly_context, 'latest_user_message', None), but that is not a standard ReadonlyContext attribute — the getattr default means a rename or absence yields no query, analyze_query_intent sees an empty string, and routing silently falls through to the support-only default rather than failing loudly. Then at line 214 it writes the result back into readonly_context.state, which is a read-only view. Doing both in a before_agent_callback on the router — which receives the user content and a writable CallbackContext — fixes the read and the write in one move.
- analyze_query_intent (agents/host_agent/advanced_router_agent.py:63) matches on substrings, so 'id ' and 'status' will fire on unrelated words. Anchoring on word boundaries, or having the router LLM emit a structured decision, would make routing less brittle.
- The toolset factories log but never guard construction. Wrapping McpToolset creation so an unreachable MCP server surfaces one clear error would make the code-level error handling match the quality of the instruction-level handling.

### Automated checks
- ✅ All required files implemented
- ✅ Provided files unmodified
- ✅ 0/0 output artifacts committed
- ✅ Reflection 1236 words

### Resubmission
You may resubmit **once**. Push fixes to this repo, then notify the instructor; we'll re-grade as **Attempt 2 (final)**. This is attempt 1 of 2.

---
*Graded automatically with Claude Code against the course rubric. Questions → contact the instructor.*


---
<sub>🔎 **Autograder record** — attempt 1 of 2 · graded at commit `196b540` · delivered 2026-07-27T07:00:49Z. Commits pushed to `main` after this timestamp are treated as a resubmission.</sub>
