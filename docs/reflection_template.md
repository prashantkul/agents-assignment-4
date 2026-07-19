# Assignment 4: Reflection

## Student Name: Grady Olsen

---

## Part 1: MCP Tools + Customer Data Agent

### Tool Design Decisions
- The MCP server exposes 15 tools total (customer CRUD, ticket CRUD, stats/search). I split them into two role-based `tool_filter` lists rather than writing new tools:
  - **Customer Data toolset** (14 tools): everything except `delete_ticket` — this agent needs broad read/write access for account and ticket management, including admin actions like `disable_customer`/`activate_customer`.
  - **Support toolset** (10 tools): lookups (`get_customer`, `list_customers`, `get_ticket`, `list_tickets`, `search_tickets`), ticket creation/updates (`create_ticket`, `update_ticket_status`, `update_ticket_priority`), and stats — explicitly excluding `disable_customer`, `activate_customer`, `delete_ticket`, `add_customer`, `update_customer` so a support rep can never destroy data or change account standing.
- No manual tool signatures were needed — `McpToolset` (an alias I added for the installed package's actual `MCPToolset` class; see Part 3) connects over SSE and auto-discovers each tool's JSON schema directly from the FastMCP server at runtime. The only "design" work on the ADK side is picking which tool *names* go in the filter list; the parameter types, defaults, and docstrings all come from the `@mcp.tool()` decorators already written in `mcp_server/app.py`.

### Data Agent Instruction
- The instruction states the agent's role (customer/ticket data specialist), enumerates its capabilities (lookup, list, create/update customers and tickets, enable/disable accounts, stats, keyword search), and gives explicit process guidance: parse the request → call the right tool(s) → only ask for missing IDs if they can't be inferred → format results in plain language instead of raw JSON.
- It also tells the agent how to fail gracefully: if a lookup returns nothing or errors, say so plainly and suggest a concrete next step (double-check the ID, list instead) rather than guessing at data it doesn't have.
- This mattered in practice — in the live test run, when a user claimed to be "Sarah Johnson, customer ID 2" but the record on file was "Jane Smith," the agent surfaced the mismatch instead of silently proceeding, which is exactly the "verify before acting" behavior the instruction was written to encourage.

---

## Part 2: Multi-Agent A2A System

### Support Agent Design
- The instruction embeds a knowledge base directly in the prompt: login issues, password resets, billing/payment failures, performance problems, feature requests, and data export issues, each with concrete troubleshooting steps (not just categories).
- For pure knowledge-base questions ("how do I reset my password?") the agent can answer from the instruction alone with zero tool calls. It only reaches for the (filtered, non-destructive) MCP toolset when it needs to ground advice in a real account/ticket — e.g., confirming a customer's ticket history before giving guidance, or filing a new ticket when an issue needs follow-up.

### Host Agent Orchestration
- `SequentialAgent` runs its `sub_agents` list in strict order and shares the same session/conversation state across them — each sub-agent's turn is appended to the conversation, so the next sub-agent in the list sees everything that happened before it.
- Concretely: the Customer Data Agent runs first and its response (customer details, ticket history) becomes part of the conversation the Support Agent reads next. In the "check my ticket status and get support" test scenario, the Support Agent's response referenced the exact ticket IDs and statuses the Data Agent had just looked up — it didn't need a separate tool call to re-fetch that context.

### A2A Protocol Insights
- Every agent server exposes an `AgentCard` (name, URL, description, skills, examples) at a well-known path (`AGENT_CARD_WELL_KNOWN_PATH`, i.e. `.well-known/agent-card.json`). This is the A2A equivalent of an OpenAPI spec — it's how a caller discovers what an agent can do and how to reach it *before* sending it any real traffic.
- `RemoteA2aAgent(agent_card=f"{url}{AGENT_CARD_WELL_KNOWN_PATH}")` fetches that card, resolves the JSON-RPC endpoint, and wraps the remote service so it can be dropped into a `SequentialAgent`'s `sub_agents` list exactly like a local `Agent`. Compared to a direct function call, this means the Host Agent never imports the Customer Data or Support agent's code at all — it only needs a URL. Each agent can be deployed, scaled, versioned, or replaced independently as long as it keeps serving a compatible AgentCard, at the cost of network latency and JSON-RPC serialization overhead on every hop.

---

## Part 3: Challenges and Solutions

### Technical Challenges
The most difficult part wasn't the agent logic — it was that the assignment's own scaffold and test files didn't match the actual installed `google-adk` package, in two places:
1. All the given code and test files import `McpToolset` (mixed case). The real class, in every `google-adk` version I checked (1.9.0 and 2.5.0), is `MCPToolset` (all caps). Every import of it would raise `ImportError` regardless of how correct a student's `tool_filter` logic was.
2. The parallel-router bonus spec calls for `RemoteA2aAgent(..., output_key='...')`. `output_key` is only a field on `LlmAgent`; `RemoteA2aAgent`'s pydantic model has `extra='forbid'`, so passing it raises a `ValidationError` immediately.

I debugged both by reading the installed package source directly (`grep`-ing for the class/field name inside `site-packages/google/adk`) rather than trusting the docstrings, and confirmed the mismatch was consistent across dependency versions rather than something specific to my environment.

**Solutions:**
1. Added a one-line alias — `from google.adk.tools.mcp_tool import MCPToolset as McpToolset` — in `shared/mcp_toolset.py` and in the two test files that import it directly, so the rest of the given code (which universally spells it `McpToolset`) keeps working unmodified.
2. Reproduced `output_key`'s actual behavior (writing the agent's final response text into session state) using an `after_agent_callback` on each `RemoteA2aAgent`, which reads the last event authored by that agent from the session and writes it into `callback_context.state` — a publicly supported extension point on every `BaseAgent` subclass.

I also pinned `google-adk==1.9.0` and `a2a-sdk==0.3.0` explicitly (rather than the `>=` floors in `requirements.txt`) to match the exact versions `shared/a2a_compat.py`'s docstring says its patch targets, since `pip install -r requirements.txt` as written would otherwise silently pull the newest available release each time.

### Architecture Decisions
- `SequentialAgent` is the right choice here because the Support Agent's advice is *better* when it has the Customer Data Agent's output in context first (e.g., "you already have an open high-priority ticket for this" instead of generic troubleshooting). A pipeline where step 2 depends on step 1's output is exactly what `SequentialAgent` models.
- The trade-off vs. calling `customer_data_agent` and `support_agent` as local Python functions: direct calls would be faster (no HTTP/JSON-RPC round trip, no agent-card discovery) and simpler to debug, but they'd tie all three agents to the same process/deployment and remove the A2A discovery contract entirely. The assignment's whole premise is testing A2A as a *protocol* boundary between independently addressable agents, so the added latency is the cost of that decoupling, not a bug.

---

## Bonus: Routing Modes (attempted)

### Advanced Router
- `analyze_query_intent()` does keyword matching against the query text: data-related keywords (`customer`, `ticket`, `account`, `id`, `list`, `search`, `stats`, ...) set `needs_data`; support-related keywords (`help`, `issue`, `problem`, `reset`, `login`, `payment`, `slow`, ...) set `needs_support`; urgency keywords (`urgent`, `asap`, `critical`, ...) bump `urgency` to `high`. If neither category matches, it defaults both to `True` rather than silently doing nothing.
- The result is stored in session state as `routing_decision` from inside the router agent's dynamic instruction function (`create_router_instruction`, called with a `ReadonlyContext` that exposes the live query via `.user_content`).
- `should_run_customer_data_agent` / `should_run_support_agent` are `before_agent_callback`s attached to each `RemoteA2aAgent`. Each reads `routing_decision` back out of `callback_context.state`; if its flag is `False` it returns a `types.Content` explaining the skip (which short-circuits that agent's turn), and returns `None` (meaning "proceed normally") otherwise.

### Parallel Router
- `ParallelAgent` fires both `RemoteA2aAgent`s concurrently via `asyncio`, so total wall-clock time is close to `max(data_agent_latency, support_agent_latency)` instead of their sum in the sequential mode.
- Since neither remote agent can see the other's output while both are in flight, synthesis happens afterward: each agent's `after_agent_callback` captures its final response text into a distinct state key (`customer_data_output`, `support_specialist_output`), and a final `summary_agent` (a plain `Agent` with `include_contents='none'` and a dynamic instruction built from those two state values) merges them into one natural-sounding reply without exposing that two separate agents ever ran.

### Mode Comparison

| Mode | Agents Called | Latency | Context Passing |
|------|-------------|---------|-----------------|
| Basic (Sequential) | Both, always, in fixed order | Sum of both agent calls (slowest, but simplest) | Support Agent sees Data Agent's turn already in the shared conversation before it runs |
| Advanced (Dynamic) | 0–2, chosen per query by keyword analysis (plus one extra router LLM call) | Variable — faster when only one specialist is actually needed, but every query pays the router's own LLM latency first | Router writes `routing_decision` into session state; each remote agent's `before_agent_callback` reads it to decide whether to run at all |
| Parallel | Both, always, concurrently | ~max(Data, Support) instead of their sum — fastest when both are genuinely needed | No mid-flight context passing between the two agents (each only sees the original query); a summary agent stitches their independent outputs together afterward from state |

---

## Key Learnings
1. `McpToolset`'s real value is that it turns "which tools can this agent use" into a one-line `tool_filter` list — no wrapper functions, no manual JSON schemas — which made enforcing role-based access (support agent can't delete/disable anything) trivial to implement and easy to audit.
2. A2A's AgentCard + well-known-path discovery genuinely decouples orchestration from implementation: the Host Agent never imports the other two agents' code, only their URLs, which is what makes `RemoteA2aAgent` swappable for a locally-run agent with zero change to the orchestrator's logic.
3. Course/library scaffolding can drift out of sync with the actual installed SDK faster than expected — I hit two real API-name mismatches (`McpToolset` vs. the installed `MCPToolset`, and `output_key` existing only on `LlmAgent` rather than `RemoteA2aAgent`) that had nothing to do with my own logic. Verifying against the installed package's actual source (not just the assignment's docstrings) was what unblocked both.

## Ideas for Improvement
- Pin exact dependency versions (`==`) instead of floors (`>=`) in `requirements.txt`, so every student's `pip install` resolves to the same tested environment instead of silently drifting to whatever's newest on PyPI.
- Add a lightweight local test for the bonus router files (`advanced_router_agent.py`, `parallel_router_agent.py`) similar to `tests/test_agents.py` — right now they have no automated coverage, so mistakes there are only caught by manually exercising `HOST_AGENT_MODE=advanced|parallel`.
- Have the toolset factories validate their `tool_filter` names against the MCP server's live tool list at startup (via a discovery call) instead of trusting hardcoded strings, so a typo'd tool name fails fast instead of silently omitting a tool.
