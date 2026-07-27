## Grade: 100 / 100

**Assignment:** Multi-Agent Customer Support (Google ADK + A2A)  
**Attempt:** 1 of 2  ·  **Graded:** 2026-07-27  ·  Commit `f800d54`

### Score breakdown
| Criterion | Max | Earned | Notes |
|-----------|-----|--------|-------|
| mcp_toolset_config | 15 | 15 | Both factories return McpToolset over SseConnectionParams with explicit tool_filter lists. create_support_toolset excludes exactly the five operations the assignment names as admin/destructive (disable_customer, activate_customer, delete_ticket, add_customer, update_customer), and the customer data toolset grants the full surface, which is what README.md:94 specifies for that role ('Broad data access ... All 15 tools (full access)'). (`agents/shared/mcp_toolset.py:83`) |
| data_agent_instruction | 10 | 10 | Instruction lists capabilities with the real filter vocabularies ('active'/'disabled', 'open'/'in_progress'/'resolved', priority levels), gives a three-step handling procedure, requires formatting JSON into readable summaries, and closes the role boundary against the Support Agent. (`agents/customer_data_agent/agent.py:80`) |
| mcp_integration | 10 | 10 | tools=[create_customer_data_toolset()] attaches the MCP-backed toolset to the Agent with GEMINI_MODEL. (`agents/customer_data_agent/agent.py:115`) |
| error_handling_instruction | 5 | 5 | Explicit rule: if a tool call fails or returns an error such as customer-not-found, say so plainly and suggest a next step rather than inventing a result. (`agents/customer_data_agent/agent.py:109`) |
| support_agent | 10 | 10 | Uses create_support_toolset(); the knowledge base carries concrete operational detail (15-minute lockout, 5-minute reset email delay, bank-side fraud blocks) and the query procedure includes an explicit priority triage rubric — high for money/security/account access, medium for blocked normal use, low for requests. (`agents/support_agent/agent.py:159`) |
| host_agent | 10 | 10 | SequentialAgent orders both remote agents through sub_agents, with a2a_compat imported at line 37 ahead of RemoteA2aAgent at line 40. (`agents/host_agent/agent.py:37`) |
| agent_cards | 10 | 9 | All three cards are complete — name, url, description, version, AgentCapabilities(streaming=True), input/output modes, TransportProtocol.jsonrpc and a populated AgentSkill. Card descriptions and the examples lists are the student's own; the AgentSkill description and tags remain the scaffold's sample values. (`agents/create_agents.py:78`) |
| a2a_integration | 10 | 10 | Both sub-agents are RemoteA2aAgent instances resolved through AGENT_CARD_WELL_KNOWN_PATH, with the compatibility patch applied before the import as the scaffold requires. (`agents/host_agent/agent.py:40`) |
| docstrings | 5 | 3 | The docstrings the student wrote are excellent (advanced_router_agent.py:182 in particular), but the scaffold's instructional docstrings survive in the required files — create_agents.py carries eight TODO markers and customer_data_agent/agent.py:50 and host_agent/agent.py still open with 'TODO:' plus the spec and Example block. (`agents/create_agents.py:53`) |
| instruction_quality | 5 | 5 | Instructions are specific and operationally useful. The priority triage rule gives the model a decision procedure rather than a vague 'set priority appropriately', and the closing paragraph (line 154) states the admin operations the agent lacks, matching its tool_filter. (`agents/support_agent/agent.py:138`) |
| error_handling_patterns | 5 | 4 | Consistent instruction-level rules across both agents, and the output-capture callback guards its state write. Code-level handling in the core path is absent — nothing guards McpToolset construction or remote card resolution in host_agent/agent.py. (`agents/host_agent/parallel_router_agent.py:72`) |
| code_organization | 5 | 4 | Module layout and helper factoring are clean, but create_all_agents hardcodes ports 10020/10021/10022 rather than importing the *_AGENT_PORT constants from shared.agents_config. (`agents/create_agents.py:262`) |
| _bonus_ | +25 | +25 | |
| Integrity deduction | — | 0 | Provided files unmodified |
| **Total** | **100** | **100** | |

### What went well
- The docstring at agents/host_agent/advanced_router_agent.py:182 is exemplary diagnostic writing. Rather than working around the ReadonlyContext problem silently, the student identified the concrete failure — .state is a MappingProxyType, so assignment raises TypeError — explained why before_agent_callback is the right surface, and noted that state deltas are what carry the decision forward. That is exactly how a tricky framework constraint should be recorded.
- Both bonus routers are not just present but correct, including the two subtleties that trip up this assignment: writing routing state from a writable context, and reproducing output_key semantics on an agent class that does not support it.
- The support agent's priority triage rule (agents/support_agent/agent.py:140) turns 'set priority appropriately' into an actual decision procedure tied to impact categories — money/security/access, blocked usage, requests — which is the kind of instruction that produces consistent behaviour across runs.
- The customer data instruction (agents/customer_data_agent/agent.py:85) teaches the model the real filter vocabularies, so the agent's first tool call is likely to use valid argument values rather than guessed ones.

### What to improve (actionable)
- Replace the scaffold docstrings in the required files with descriptions of the finished code. agents/create_agents.py alone still carries eight TODO markers, and customer_data_agent/agent.py:50 opens with 'TODO: Create and return an Agent instance with:' above a working implementation. This is the largest single deduction on the submission, and it stands in odd contrast to the excellent docstrings you wrote in the bonus modules.
- agents/create_agents.py:262 hardcodes ports 10020/10021/10022; import CUSTOMER_DATA_AGENT_PORT, SUPPORT_AGENT_PORT and HOST_AGENT_PORT from shared.agents_config so the cards cannot drift from the servers.
- create_router_instruction (agents/host_agent/advanced_router_agent.py:205) re-runs analyze_query_intent independently rather than reading the decision the callback already stored. It is correct and you documented the reasoning, but it means the analysis runs twice and the two copies could diverge if the function ever becomes non-pure — reading readonly_context.state.get('routing_decision') with the recompute as fallback would remove that risk.
- The AgentSkill descriptions and tags in agents/create_agents.py:94 are still the scaffold's sample values even though your card descriptions and examples are your own. Tailoring them would finish the cards off for A2A discovery.

### Automated checks
- ✅ All required files implemented
- ✅ Provided files unmodified
- ✅ 0/0 output artifacts committed
- ✅ Reflection 2444 words

### Resubmission
You may resubmit **once**. Push fixes to this repo, then notify the instructor; we'll re-grade as **Attempt 2 (final)**. This is attempt 1 of 2.

---
*Graded automatically with Claude Code against the course rubric. Questions → contact the instructor.*


---
<sub>🔎 **Autograder record** — attempt 1 of 2 · graded at commit `f800d54` · delivered 2026-07-27T07:01:14Z. Commits pushed to `main` after this timestamp are treated as a resubmission.</sub>
