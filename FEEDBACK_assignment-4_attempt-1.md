## Grade: 100 / 100

**Assignment:** Multi-Agent Customer Support (Google ADK + A2A)  
**Attempt:** 1 of 2  ·  **Graded:** 2026-07-27  ·  Commit `4fee3d7`

> **Note: provided files were modified.** These instructor-provided files (not meant to be changed) differ from the originals: `tests/test_mcp_toolset.py`, `tests/test_agents.py`. No automatic deduction was applied. If this was a necessary setup fix, no action is needed.

### Score breakdown
| Criterion | Max | Earned | Notes |
|-----------|-----|--------|-------|
| mcp_toolset_config | 15 | 15 | Both factories return McpToolset over SseConnectionParams with tool_filter. create_support_toolset excludes exactly the five operations the assignment names as admin/destructive (disable_customer, activate_customer, delete_ticket, add_customer, update_customer). The customer data filter grants 14 tools, which matches the capability list in the TODO 1 comment block in this very file exactly — the scaffold is internally inconsistent here, since README.md:94 instead specifies full access for that role. Both readings are accepted: the canonical rubric constrains only the support toolset. (`agents/shared/mcp_toolset.py:96`) |
| data_agent_instruction | 10 | 10 | Instruction enumerates capabilities down to the actual filter values ('active'/'disabled', 'open'/'in_progress'/'resolved', priority levels), gives a three-step handling procedure, and requires formatting results into readable summaries rather than dumping raw JSON. (`agents/customer_data_agent/agent.py:81`) |
| mcp_integration | 10 | 10 | tools=[create_customer_data_toolset()] attaches the MCP-backed toolset to the Agent with GEMINI_MODEL. (`agents/customer_data_agent/agent.py:114`) |
| error_handling_instruction | 5 | 5 | Explicit rule: if a lookup returns no results or an error, tell the user plainly what was not found and suggest a next step (re-check the ID, try listing instead) rather than failing silently or guessing at data. (`agents/customer_data_agent/agent.py:109`) |
| support_agent | 10 | 10 | Uses create_support_toolset(); the instruction carries a six-category knowledge base with concrete causes and remedies, and lines 124-129 spell out the support-safe tool inventory alongside what the agent explicitly cannot do. (`agents/support_agent/agent.py:149`) |
| host_agent | 10 | 10 | SequentialAgent('customer_support_host') orders both remote agents through sub_agents, with a2a_compat imported at line 37 ahead of RemoteA2aAgent at line 40. (`agents/host_agent/agent.py:37`) |
| agent_cards | 10 | 9 | All three cards are complete — name, url, description, version, AgentCapabilities(streaming=True), input/output modes, TransportProtocol.jsonrpc and a populated AgentSkill. Card descriptions and the examples lists are the student's own; the AgentSkill description and tags remain the scaffold's sample values. (`agents/create_agents.py:77`) |
| a2a_integration | 10 | 10 | Both sub-agents are RemoteA2aAgent instances resolved through AGENT_CARD_WELL_KNOWN_PATH, with the compatibility patch applied before the import as the scaffold requires. No direct function calls between agents. (`agents/host_agent/agent.py:40`) |
| docstrings | 5 | 3 | The student's own helpers are well documented (parallel_router_agent.py:59) and the explanatory comment blocks are excellent, but every scaffold function keeps its instructional docstring — create_agent still opens 'TODO: Create and return an Agent instance with:' followed by the spec and an Example block, and the same holds across create_agents.py and both bonus modules. (`agents/customer_data_agent/agent.py:47`) |
| instruction_quality | 5 | 5 | Instructions are specific and internally consistent — the support agent is given an explicit inventory of what it can and cannot do that matches its tool_filter exactly, and each knowledge-base entry names likely root causes rather than restating the category. (`agents/support_agent/agent.py:124`) |
| error_handling_patterns | 5 | 4 | Instruction-level handling is consistent across both agents, ending with a fail-plainly-and-offer-a-ticket rule. Code-level handling is thinner: nothing guards McpToolset construction or remote card resolution, and _capture (parallel_router_agent.py:62) reaches into state without a try/except. (`agents/support_agent/agent.py:146`) |
| code_organization | 5 | 4 | Module layout and helper factoring are clean, but create_all_agents hardcodes ports 10020/10021/10022 rather than importing the *_AGENT_PORT constants from shared.agents_config. (`agents/create_agents.py:263`) |
| _bonus_ | +25 | +24 | |
| Integrity deduction | — | 0 | Provided files MODIFIED — flagged, no deduction (tests/test_mcp_toolset.py, tests/test_agents.py) |
| **Total** | **100** | **100** | |

### What went well
- The output_key workaround in agents/host_agent/parallel_router_agent.py:52 is the standout piece of work in this submission. The student hit a real ValidationError, correctly identified that output_key is implemented on LlmAgent rather than every BaseAgent, wrote down the diagnosis, and then built a functionally equivalent after_agent_callback that actually captures the worker's response text — so the synthesizer receives real parallel output, not a stand-in.
- Tool scoping is deliberate rather than incidental: agents/shared/mcp_toolset.py:98 withholds delete_ticket from the data role, a tighter grant than the assignment requires, and the support filter at line 155 excludes every admin and destructive operation.
- The customer data instruction (agents/customer_data_agent/agent.py:87) teaches the model the real filter vocabularies — 'active'/'disabled', 'open'/'in_progress'/'resolved', the priority levels — which is exactly the detail that makes tool calls succeed on the first attempt.
- Version drift is handled honestly and visibly: the MCPToolset alias at agents/shared/mcp_toolset.py:34 carries a comment explaining why the name differs, so a reader on a different ADK version understands the situation immediately.

### What to improve (actionable)
- Replace the scaffold docstrings with descriptions of the finished code. agents/customer_data_agent/agent.py:47 and the card factories in create_agents.py still read 'TODO: ...' with the full spec and Example block — this is the single largest Part 3 deduction, and it is squarely at odds with the quality of the explanatory comments you wrote elsewhere.
- _capture in agents/host_agent/parallel_router_agent.py:62 reaches through callback_context._invocation_context, a private attribute. The approach is right, but a private path can break silently on an ADK upgrade — worth a comment marking it as version-sensitive, or a getattr guard so a rename degrades to 'no captured output' instead of an AttributeError mid-run.
- agents/create_agents.py:263 hardcodes ports 10020/10021/10022; import CUSTOMER_DATA_AGENT_PORT, SUPPORT_AGENT_PORT and HOST_AGENT_PORT from shared.agents_config so the cards cannot drift from the servers.
- analyze_query_intent (agents/host_agent/advanced_router_agent.py:95) matches substrings, so 'id' hits inside 'video', 'consider' and similar. Tokenising and matching whole words would make the routing decision far less noisy.
- Note on the integrity check: tests/test_mcp_toolset.py and tests/test_agents.py differ from the provided versions. The diff is only the McpToolset -> MCPToolset import alias needed for your ADK version, which is a reasonable adaptation and carries no penalty under this rubric — but for future assignments, prefer aliasing in your own module (as you already do in mcp_toolset.py:37) and leaving provided test files untouched.

### Automated checks
- ✅ All required files implemented
- ⚠️ Provided files MODIFIED — flagged, no deduction (tests/test_mcp_toolset.py, tests/test_agents.py)
- ✅ 0/0 output artifacts committed
- ✅ Reflection 1755 words

### Resubmission
You may resubmit **once**. Push fixes to this repo, then notify the instructor; we'll re-grade as **Attempt 2 (final)**. This is attempt 1 of 2.

---
*Graded automatically with Claude Code against the course rubric. Questions → contact the instructor.*
