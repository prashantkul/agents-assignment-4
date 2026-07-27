## Grade: 100 / 100

**Assignment:** Multi-Agent Customer Support (Google ADK + A2A)  
**Attempt:** 1 of 2  ·  **Graded:** 2026-07-27  ·  Commit `ab06666`

### Score breakdown
| Criterion | Max | Earned | Notes |
|-----------|-----|--------|-------|
| mcp_toolset_config | 15 | 15 | Both factories return McpToolset over SseConnectionParams with tool_filter from named constants. The comment block at line 147 states the least-privilege reasoning explicitly, names each of the five withheld tools with a justification, and observes that filtered tools are never discovered so prompting cannot reach them. The full-access grant for the data role is likewise argued at line 83 — an explicit allow-list is preferred over no filter because it fails closed when the server grows a new tool. (`agents/shared/mcp_toolset.py:147`) |
| data_agent_instruction | 10 | 10 | Instruction sets a clear role boundary against the Support Agent, groups all 15 tools by purpose, gives a three-step procedure with 'call the single most specific tool', and adds a dedicated write-operations clause requiring the agent to echo back ids and new values after a mutation. (`agents/customer_data_agent/agent.py:77`) |
| mcp_integration | 10 | 10 | tools=[create_customer_data_toolset()] attaches the MCP-backed toolset, and the Agent also carries a description field that summarises the role for A2A consumers. (`agents/customer_data_agent/agent.py:122`) |
| error_handling_instruction | 5 | 5 | Error handling names the structured not-found case and models the desired phrasing ('No customer exists with id 999'), requires stating what was tried, suggests the closest valid next step, and forbids hiding a failure behind invented data. (`agents/customer_data_agent/agent.py:106`) |
| support_agent | 10 | 10 | Uses create_support_toolset(); the instruction names its available tools, states in capitals what it CANNOT do and that those need an account administrator, then supplies a six-domain knowledge base and priority-by-impact ticketing rules. (`agents/support_agent/agent.py:156`) |
| host_agent | 10 | 10 | SequentialAgent orders both remote agents through sub_agents, with a2a_compat imported at line 37 ahead of RemoteA2aAgent at line 40. (`agents/host_agent/agent.py:37`) |
| agent_cards | 10 | 10 | All three cards are complete — name, url, description, version, AgentCapabilities(streaming=True), input/output modes, TransportProtocol.jsonrpc and a populated AgentSkill. Skill descriptions, tags and examples are tailored rather than carried over from the scaffold samples. (`agents/create_agents.py:220`) |
| a2a_integration | 10 | 10 | Both sub-agents are RemoteA2aAgent instances resolved through AGENT_CARD_WELL_KNOWN_PATH, with the compatibility patch applied first as the scaffold requires. (`agents/host_agent/agent.py:40`) |
| docstrings | 5 | 4 | The student went through and rewrote the scaffold's 'TODO:' openings into descriptive prose ('Creates and returns an Agent instance with:'), and every helper they added is documented with real rationale. The scaffold's Example blocks were left behind inside those docstrings, so create_agent still carries a sample implementation that duplicates the real one below it. (`agents/customer_data_agent/agent.py:47`) |
| instruction_quality | 5 | 5 | Instructions are precise and mutually consistent — each agent is told what the other one handles, and the support agent's stated prohibitions match its tool_filter exactly, down to naming the escalation path for each. (`agents/support_agent/agent.py:100`) |
| error_handling_patterns | 5 | 5 | Consistent instruction-level rules across both agents, plus real defensive code: the output-capture callback falls back to writing an empty string when no matching event is found, so the downstream synthesizer always sees a defined state key rather than a KeyError. (`agents/host_agent/parallel_router_agent.py:104`) |
| code_organization | 5 | 5 | Clean throughout: tool lists hoisted to documented module constants, agent instructions separated from factory calls, and create_all_agents imports CUSTOMER_DATA_AGENT_PORT / SUPPORT_AGENT_PORT / HOST_AGENT_PORT from shared.agents_config rather than hardcoding port literals. (`agents/create_agents.py:268`) |
| _bonus_ | +25 | +25 | |
| Integrity deduction | — | 0 | Provided files unmodified |
| **Total** | **100** | **100** | |

### What went well
- The comment block at agents/shared/mcp_toolset.py:147 is an unusually clear articulation of the assignment's core idea — it names each withheld tool with a reason and points out that tool_filter enforces least privilege at the protocol layer, so excluded tools are never discovered and no amount of clever prompting can reach them. That is exactly the security property the exercise is teaching.
- The advanced router gets the state-writing question right where it is easy to get wrong: agents/host_agent/advanced_router_agent.py:133 computes the routing decision in a before_agent_callback with a writable CallbackContext, and line 198 documents why an instruction provider — which only sees a ReadonlyContext — is the wrong place for it.
- Role separation is enforced in both directions. The data agent is told it does not give troubleshooting advice (agents/customer_data_agent/agent.py:80) and the support agent is told which actions require an administrator (agents/support_agent/agent.py:100), so the two instructions describe one coherent system rather than two independently written prompts.
- Configuration discipline is strong: named tool constants, ports imported from shared.agents_config at agents/create_agents.py:268, and agent descriptions supplied on the Agent objects themselves as well as on the cards.

### What to improve (actionable)
- Finish the docstring cleanup you started. You rewrote the 'TODO:' openings into descriptive prose, but the scaffold's Example blocks survive inside them — agents/customer_data_agent/agent.py:60 still shows a sample Agent(...) construction directly above your real one, which is confusing for a reader and adds nothing now that the implementation exists.
- analyze_query_intent (agents/host_agent/advanced_router_agent.py:84) matches keywords by substring, so 'id' fires inside 'video', 'consider' and similar words. Tokenising the query and matching whole words would keep the routing decision from being triggered by coincidence.
- The import of the port constants at agents/create_agents.py:268 sits inside create_all_agents. Everything else in the module imports at the top — moving it up would keep the import surface visible in one place, unless it is deliberately deferred to dodge a circular import (worth a comment if so).

### Automated checks
- ✅ All required files implemented
- ✅ Provided files unmodified
- ✅ 0/0 output artifacts committed
- ✅ Reflection 1401 words

### Resubmission
You may resubmit **once**. Push fixes to this repo, then notify the instructor; we'll re-grade as **Attempt 2 (final)**. This is attempt 1 of 2.

---
*Graded automatically with Claude Code against the course rubric. Questions → contact the instructor.*


---
<sub>🔎 **Autograder record** — attempt 1 of 2 · graded at commit `ab06666` · delivered 2026-07-27T07:01:10Z. Commits pushed to `main` after this timestamp are treated as a resubmission.</sub>
