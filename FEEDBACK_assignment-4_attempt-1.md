## Grade: 95 / 100

**Assignment:** Multi-Agent Customer Support (Google ADK + A2A)  
**Attempt:** 1 of 2  ·  **Graded:** 2026-07-27  ·  Commit `0e5853f`

### Score breakdown
| Criterion | Max | Earned | Notes |
|-----------|-----|--------|-------|
| mcp_toolset_config | 15 | 15 | Both factories return McpToolset over SseConnectionParams with explicit tool_filter lists. create_support_toolset excludes exactly the five operations the assignment names as admin/destructive (disable_customer, activate_customer, delete_ticket, add_customer, update_customer), and the customer data toolset grants the full surface, which is what README.md:94 specifies for that role ('Broad data access ... All 15 tools (full access)'). (`agents/shared/mcp_toolset.py:93`) |
| data_agent_instruction | 10 | 10 | Instruction is well structured — role as system of record, four capability groups, request-handling rules including clarifying questions for missing IDs, response style, and a dedicated error-handling section. (`agents/customer_data_agent/agent.py:81`) |
| mcp_integration | 10 | 10 | tools=[create_customer_data_toolset()] wires the MCP-backed toolset into the Agent with GEMINI_MODEL. (`agents/customer_data_agent/agent.py:117`) |
| error_handling_instruction | 5 | 5 | Explicit error-handling block: no raw stack traces, explain what went wrong gracefully, suggest how the user can correct the request. (`agents/customer_data_agent/agent.py:111`) |
| support_agent | 10 | 10 | Uses create_support_toolset(); the instruction expands all five knowledge-base domains with concrete troubleshooting steps and sets clear create-vs-update ticket criteria (line 139). (`agents/support_agent/agent.py:154`) |
| host_agent | 10 | 10 | SequentialAgent('customer_support_host') orders the two remote agents through sub_agents. (`agents/host_agent/agent.py:110`) |
| agent_cards | 10 | 9 | All three cards are complete and valid — name, url, version, AgentCapabilities(streaming=True), input/output modes, TransportProtocol.jsonrpc, and a populated AgentSkill. Descriptions are the student's own; the skill ids, tags and examples are carried over verbatim from the scaffold's example blocks rather than tailored. (`agents/create_agents.py:77`) |
| a2a_integration | 10 | 10 | Both sub-agents are RemoteA2aAgent instances addressed via AGENT_CARD_WELL_KNOWN_PATH, with the a2a_compat patch imported first at line 37. No direct function calls between agents. (`agents/host_agent/agent.py:98`) |
| docstrings | 5 | 3 | The scaffold's instructional docstrings are left in place. create_agent still opens with 'TODO: Implement this function to:' and walks through steps 1-3 plus an Example block, so the docstring describes the exercise rather than the finished code. Same pattern in create_agents.py:53 and support_agent/agent.py:60. (`agents/host_agent/agent.py:57`) |
| instruction_quality | 5 | 5 | Instructions are specific and role-appropriate — the support agent gets tone guidance, per-domain playbooks, a response structure, and ticketing rules that match its restricted toolset. (`agents/support_agent/agent.py:94`) |
| error_handling_patterns | 5 | 4 | Both agents carry a consistent, well-worded error-handling clause. Code-level handling is absent: no guard around McpToolset construction or remote card resolution. (`agents/support_agent/agent.py:148`) |
| code_organization | 5 | 4 | Module layout is clean and imports are tidy, but create_all_agents hardcodes ports 10020/10021/10022 as literals instead of importing the *_AGENT_PORT constants from shared.agents_config alongside the URLs it already imports (line 33). (`agents/create_agents.py:251`) |
| Integrity deduction | — | 0 | Provided files unmodified |
| **Total** | **100** | **95** | |

### What went well
- The support toolset in agents/shared/mcp_toolset.py:155 gets the security boundary exactly right, and the support instruction is written to match — it never promises account-administration actions the agent cannot perform.
- The support agent's knowledge base (agents/support_agent/agent.py:99) is a highlight of the submission: each of the five domains has real diagnostic steps rather than a restatement of the category name, and the create-vs-update ticket rules give the model a clear decision procedure.
- A2A orchestration is wired correctly and in the right order — agents/host_agent/agent.py:37 applies the compatibility patch before RemoteA2aAgent is imported, and both remotes resolve through AGENT_CARD_WELL_KNOWN_PATH.
- Both agents end with a consistent, customer-facing error-handling clause that forbids leaking raw technical detail, which is a nice touch of product sense.

### What to improve (actionable)
- Replace the scaffold docstrings with descriptions of the finished code. agents/host_agent/agent.py:57 and agents/create_agents.py:53 still read 'TODO: Implement this function to:' followed by the instructions and an Example block — a reader of the final repo cannot tell what is spec and what is implementation. This is the single largest point loss in Part 3.
- agents/create_agents.py:251 hardcodes ports 10020/10021/10022. You already import URLs from shared.agents_config at line 33; import CUSTOMER_DATA_AGENT_PORT, SUPPORT_AGENT_PORT and HOST_AGENT_PORT the same way so a config change cannot desynchronise the cards from the servers.
- The AgentSkill ids, tags and examples in agents/create_agents.py:88 are the scaffold's sample values. Tailoring them to the capabilities you actually implemented would make the cards more useful for A2A discovery.
- Both bonus routers were left untouched. The advanced router (+15) is mostly intent classification plus before_agent_callback wiring on top of the host agent you already have, so it is a substantial score for a contained amount of work.

### Automated checks
- ✅ All required files implemented
- ✅ Provided files unmodified
- ✅ 0/0 output artifacts committed
- ✅ Reflection 1490 words

### Resubmission
You may resubmit **once**. Push fixes to this repo, then notify the instructor; we'll re-grade as **Attempt 2 (final)**. This is attempt 1 of 2.

---
*Graded automatically with Claude Code against the course rubric. Questions → contact the instructor.*


---
<sub>🔎 **Autograder record** — attempt 1 of 2 · graded at commit `0e5853f` · delivered 2026-07-27T07:00:53Z. Commits pushed to `main` after this timestamp are treated as a resubmission.</sub>
