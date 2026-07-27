## Grade: 100 / 100

**Assignment:** Multi-Agent Customer Support (Google ADK + A2A)  
**Attempt:** 1 of 2  ·  **Graded:** 2026-07-27  ·  Commit `44990be`

### Score breakdown
| Criterion | Max | Earned | Notes |
|-----------|-----|--------|-------|
| mcp_toolset_config | 15 | 15 | Both factories return McpToolset over SseConnectionParams with tool_filter. create_support_toolset excludes exactly the five operations the assignment names as admin/destructive (disable_customer, activate_customer, delete_ticket, add_customer, update_customer). The customer data filter grants 14 tools, which matches the capability list in the TODO 1 comment block in this very file exactly — the scaffold is internally inconsistent here, since README.md:94 instead specifies full access for that role. Both readings are accepted: the canonical rubric constrains only the support toolset. (`agents/shared/mcp_toolset.py:67`) |
| data_agent_instruction | 10 | 10 | Instruction pairs every capability with the actual MCP tool name in parentheses and includes the real status filter values, gives a four-step handling procedure covering multi-entity requests, and sets a precise data-driven response style. (`agents/customer_data_agent/agent.py:59`) |
| mcp_integration | 10 | 10 | tools=[create_customer_data_toolset()] attaches the MCP-backed toolset to the Agent with GEMINI_MODEL. (`agents/customer_data_agent/agent.py:97`) |
| error_handling_instruction | 5 | 4 | The essentials are covered — ask for a missing identifier rather than guessing (line 81), do not fabricate data the tools did not return (line 86), and state a no-result or error plainly instead of speculating. Thin in places: there is no dedicated error-handling section, no distinction between a tool failure and a not-found result, and no guidance on suggesting a recovery step to the caller. (`agents/customer_data_agent/agent.py:94`) |
| support_agent | 10 | 10 | Uses create_support_toolset(); the instruction supplies a five-domain knowledge base, lists the tools actually available, and states plainly at line 98 which admin and destructive operations it lacks and that such requests must be escalated. (`agents/support_agent/agent.py:121`) |
| host_agent | 10 | 10 | SequentialAgent orders both remote agents through sub_agents, with a2a_compat imported at line 37 ahead of RemoteA2aAgent at line 40. (`agents/host_agent/agent.py:37`) |
| agent_cards | 10 | 9 | All three cards are complete — name, url, description, version, AgentCapabilities(streaming=True), input/output modes, TransportProtocol.jsonrpc and a populated AgentSkill. Card descriptions are the student's own; the AgentSkill description, tags and examples remain the scaffold's sample values. (`agents/create_agents.py:58`) |
| a2a_integration | 10 | 10 | Both sub-agents are RemoteA2aAgent instances resolved through AGENT_CARD_WELL_KNOWN_PATH, with the compatibility patch applied before the import as the scaffold requires. (`agents/host_agent/agent.py:40`) |
| docstrings | 5 | 4 | The function docstrings were properly rewritten — create_all_agents documents its exact return shape, and both agent modules carry clean Returns sections with no TODO text. What remains is the scaffold's section-banner comments ('TODO 2: Support Agent Card (5 pts)') still heading four blocks in create_agents.py, which leaves the finished module reading partly as an exercise sheet. (`agents/create_agents.py:152`) |
| instruction_quality | 5 | 5 | Instructions are clear and internally consistent — the support agent's stated prohibitions match its tool_filter exactly, and the login playbook correctly routes disabled-account cases to an administrator rather than promising a fix it cannot deliver. (`agents/support_agent/agent.py:98`) |
| error_handling_patterns | 5 | 4 | The output-capture callback guards its state write, and the instruction-level rules are consistent across both agents. Code-level handling in the core path is absent — nothing guards McpToolset construction or remote card resolution in host_agent/agent.py. (`agents/host_agent/parallel_router_agent.py:73`) |
| code_organization | 5 | 4 | Module layout, type hints and helper factoring are tidy, but create_all_agents hardcodes ports 10020/10021/10022 rather than importing the *_AGENT_PORT constants from shared.agents_config. (`agents/create_agents.py:165`) |
| _bonus_ | +25 | +25 | |
| Integrity deduction | — | 0 | Provided files unmodified |
| **Total** | **100** | **100** | |

### What went well
- Both bonus routers are implemented correctly, including the two subtleties that separate a working implementation from a plausible-looking one: routing state written through a before_agent_callback with a writable context, and output_key semantics reproduced on an agent class that does not provide the field.
- Tool scoping is deliberate — agents/shared/mcp_toolset.py:67 gives the Customer Data Agent 14 tools with delete_ticket withheld, so the filter encodes an actual policy rather than passing everything through.
- The customer data instruction (agents/customer_data_agent/agent.py:59) names the concrete MCP tool alongside each capability, which is the detail that makes the model's first tool selection reliable rather than a guess.
- The support agent's boundary is stated in both directions: line 98 lists the operations it lacks, and the login playbook (line 70) tells it to route disabled accounts to an administrator instead of promising a fix — so it will not over-commit to a customer.

### What to improve (actionable)
- Give the Customer Data Agent a proper error-handling section. Right now the guidance is a single line inside Response style (agents/customer_data_agent/agent.py:94). Distinguish a tool failure from a legitimate not-found result, and tell the agent to suggest a recovery step — 'list customers so you can pick a valid id' — rather than only reporting the failure.
- Delete the leftover scaffold section banners in agents/create_agents.py — four blocks still read 'TODO N: ... (5 pts)' even though the functions beneath them are complete and their docstrings are properly written. It is a two-minute cleanup that removes the last exercise-sheet residue from an otherwise finished module.
- agents/create_agents.py:165 hardcodes ports 10020/10021/10022; import CUSTOMER_DATA_AGENT_PORT, SUPPORT_AGENT_PORT and HOST_AGENT_PORT from shared.agents_config so the cards cannot drift from the servers.
- The AgentSkill descriptions, tags and examples in agents/create_agents.py:64 are the scaffold's sample values. Since your bonus work shows real understanding of how the agents differ, tailoring the skill metadata — especially the examples an A2A client routes on — would make the cards reflect that.
- docs/reflection_template.md was submitted as the unfilled scaffold — the Student Name line is still blank, every prompt is an unanswered bullet, the Mode Comparison table is empty and Key Learnings 1./2./3. have no entries. The automated check counts 299 words, but those are the template's own prompt text rather than your writing. The rubric does not score the reflection, so this costs you no points here, but it is the one part of the submission that is genuinely incomplete — and it is a shame, because the two framework problems you solved (reproducing output_key on RemoteA2aAgent, and using a before_agent_callback to get a writable context) are exactly what it asks you to write about. Please fill it in.

### Automated checks
- ✅ All required files implemented
- ✅ Provided files unmodified
- ✅ 0/0 output artifacts committed
- ✅ Reflection 299 words

### Resubmission
You may resubmit **once**. Push fixes to this repo, then notify the instructor; we'll re-grade as **Attempt 2 (final)**. This is attempt 1 of 2.

---
*Graded automatically with Claude Code against the course rubric. Questions → contact the instructor.*
