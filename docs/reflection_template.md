# Assignment 4: Reflection

## Student Name: **\*\***\_\_\_**\*\***

---

## Part 1: MCP Tools + Customer Data Agent

### Tool Design Decisions

- Which MCP tools did you implement and why?
- How did you design the tool signatures for ADK compatibility?

### Data Agent Instruction

- What capabilities did you include in the system instruction?
- How does the instruction guide the agent's tool selection?

---

## Part 2: Multi-Agent A2A System

### Support Agent Design

- What knowledge did you embed in the support agent's instruction?
- How does it handle queries without external tools?

### Host Agent Orchestration

- How does the SequentialAgent coordinate between sub-agents?
- What happens when the Customer Data Agent returns data to the Support Agent?

### A2A Protocol Insights

- How does agent discovery work via AgentCards?
- What role does the `.well-known/agent-card.json` endpoint play?
- How does RemoteA2aAgent differ from direct function calls?

---

## Part 3: Challenges and Solutions

### Technical Challenges

- What was the most difficult part of the implementation?
- How did you debug agent communication issues?

### Architecture Decisions

- Why is the SequentialAgent pattern appropriate for this use case?
- What are the trade-offs vs. direct agent calls?

---

## Bonus: Routing Modes (if attempted)

### Advanced Router

- How does the dynamic routing decide which agents to call?
- What callback patterns did you use?

### Parallel Router

- How does parallel execution improve latency?
- What synthesis strategy did you use to combine results?

### Mode Comparison

| Mode               | Agents Called | Latency | Context Passing |
| ------------------ | ------------- | ------- | --------------- |
| Basic (Sequential) |               |         |                 |
| Advanced (Dynamic) |               |         |                 |
| Parallel           |               |         |                 |

---

## Key Learnings

1.
2.
3.

## Ideas for Improvement

-
-

# Assignment 4: Reflection

## Student Name: Diego Carpenter

---

## Part 1: MCP Tools + Customer Data Agent

### Tool Design Decisions

- The Customer Data Agent's toolset (`create_customer_data_toolset()`) includes all 15 MCP tools with no filtering, since this agent is the system of record with full read/write access — customer lookup/management (get_customer, list_customers, add_customer, update_customer, disable_customer, activate_customer), ticket operations (get_ticket, list_tickets, create_ticket, update_ticket_status, update_ticket_priority,
  delete_ticket), and statistics/search (get_ticket_stats, get_customer_stats,
  search_tickets). The Support Agent's toolset (`create_support_toolset()`) filters this down to 10 support-safe tools, excluding the five admin/destructive operations (disable_customer, activate_customer, delete_ticket, add_customer, update_customer) so a customer-facing agent can't accidentally disable an account or destroy data.
- Tool signatures didn't need manual design — ADK's `McpToolset` auto-discovers tool schemas directly from the MCP server via the `list_tools` MCP method and converts them into ADK-compatible `BaseTool` instances. My job was purely to configure `tool_filter` correctly per agent role via `SseConnectionParams(url=MCP_SSE_URL)`.

### Data Agent Instruction

- The instruction covers: the agent's role as the full-access data specialist, its four capability areas (customer lookup, customer record management, ticket operations, statistics/search), how to parse and handle requests, response style, and explicit graceful error handling guidance for failed tool calls.
- The instruction guides tool selection by mapping each capability area to the relevant tool category up front, so the model can match a user's intent (e.g. "look up a customer" vs. "check ticket stats") to the right tool family before reasoning about which specific tool and arguments to use.

---

## Part 2: Multi-Agent A2A System

### Support Agent Design

- The Support Agent's instruction embeds a knowledge base covering five areas: login issues (password resets, account lockouts), payment issues (failed transactions, billing errors), performance problems (slow loading, timeouts), feature requests/suggestions, and data export issues — each with specific guidance on likely causes and recommended steps.
- It handles queries by grounding responses in real account context first (using its filtered MCP tools to look up the customer/tickets), then categorizing the issue against the knowledge base, then proposing solution steps — so even "knowledge base" answers aren't purely static; they're informed by live customer data where relevant.

### Host Agent Orchestration

- The `SequentialAgent` (`customer_support_host`) runs its two `RemoteA2aAgent`
  sub-agents — `customer_data` and `support_specialist` — in order, passing the
  accumulated conversation context forward at each step.
- When the Customer Data Agent returns data (e.g. a customer record or ticket list),that output becomes part of the context the Support Agent sees on its turn, letting the Support Agent give personalized, data-grounded guidance instead of generic troubleshooting.

### A2A Protocol Insights

- Agent discovery works through `AgentCard` objects served by each agent at a
  well-known URL — I verified this directly with `curl http://localhost:10020/.well-known/agent-card.json`
  and got back a JSON document with the agent's name, description, skills (with
  examples), transport, and protocol version.
- The `.well-known/agent-card.json` endpoint is what lets a `RemoteA2aAgent` discover a remote agent's capabilities without hardcoded knowledge of its internals — it's the A2A equivalent of a service manifest, fetched before any actual task delegation.
- `RemoteA2aAgent` differs from a direct function call in that it goes over the network
  via the A2A/JSON-RPC protocol (I could see this live as `POST http://localhost:10022`
  calls in the logs) rather than an in-process Python call — meaning each sub-agent is its own independently running server, can be scaled, versioned, or deployed separately, and communicates only through the standardized A2A message format rather than sharing memory or objects directly.

---

## Part 3: Challenges and Solutions

### Technical Challenges

- The most difficult part wasn't the agent logic itself — Parts 1 and 2 passed their local structure tests on the first implementation — it was environment/dependency compatibility. I ran into three separate bugs:
  1. `a2a-sdk` was pinned as `a2a-sdk>=0.3.0` in requirements.txt with no upper bound, so pip installed `1.1.0` — a major version far newer than the provided `a2a_compat.py` patch (written for `0.3.0`) anticipated. This caused a `cannot import name 'ClientEvent' from 'a2a.client'` failure at Host Agent creation. Fix: pinned to `a2a-sdk==0.3.26`, the latest release in the compatible
  2. Even after that fix, `test_scenarios.py` failed all availability checks with "unknown async library, or not in async context" — a `sniffio` error. I traced this to `sniffio==1.3.1` (last released 2024) not supporting Python 3.14, which my environment was running (Python 3.14 shipped very recently). No newer `sniffio` release existed to fix it. Solution: rebuilt the entire venv on Python 3.12 (via Homebrew), which resolved it completely.
  3. Once the system ran end-to-end, I hit a `404` from Gemini stating
     `gemini-2.5-flash` was "no longer available to new users" — a real Google API policy change affecting newly created API projects — plus `429` rate-limit errors from the free tier's low requests-per-minute cap (each query fires several LLM calls across the SequentialAgent chain). Fix: switched `GEMINI_MODEL` to `gemini-2.5-flash-lite`, which is still free-tier and has higher rate limits.
- I debugged agent communication issues by isolating each layer: first confirming the MCP server responded to tools directly.

### Architecture Decisions

- `SequentialAgent` is appropriate here because the two-step task genuinely has an
  ordering dependency: the Support Agent's guidance is more useful when it's grounded in
  the customer/ticket data the Customer Data Agent retrieves first. Running them in a
  fixed order guarantees that context is available when needed, without requiring
  custom coordination logic.
- The trade-off vs. direct (in-process) agent calls is added latency and operational
  complexity — three separate servers, JSON-RPC serialization, and network calls
  instead of function calls — in exchange for genuine process isolation (the Support
  Agent literally cannot call an admin tool because it's a separate server with its own
  filtered toolset, not just a filtered set of functions in the same process),
  independent scalability, and the ability to swap or upgrade individual agents without
  touching the others.

---

## Bonus: Routing Modes

I did not attempt for this submission — focused on fully verifying Parts 1 and 2 end-to-end.

---

## Key Learnings

1. Passing local unit/structure tests doesn't guarantee a distributed system works —
   the real proof came from starting all three servers and running live A2A calls
   end-to-end, which surfaced issues (dependency versions, Python version
   compatibility) that no amount of static test-passing would have caught.
2. Loose dependency pins (`>=` with no ceiling) are a real production risk, not just an
   assignment quirk — a `>=0.3.0` constraint silently installed a `1.1.0` package with a
   materially different API surface, breaking a compatibility patch that was written for
   an earlier version.
3. Free-tier LLM API constraints (rate limits, model deprecation for new accounts) are
   operational realities that show up immediately once you're actually running a
   multi-agent system that fires several LLM calls per user query, not just a single
   agent.

## Ideas for Improvement

- Pin `a2a-sdk` and other fast-moving dependencies to exact versions (or at least an
  upper bound) in `requirements.txt` from the start, rather than `>=`, to avoid
  environment drift between when the assignment was authored and when a student
  installs it.
- Add a note in the README about tested Python version ranges, given how quickly async libraries like `sniffio` can break on newer Python releases.
