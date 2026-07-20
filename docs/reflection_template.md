# Assignment 4: Reflection

## Student Name: Nick Cherepanov

---

## Part 1: MCP Tools + Customer Data Agent

### Tool Design Decisions
- The MCP server and its 15 tools were provided. My design work was the
  capability boundary: which of those 15 each agent may call, expressed as a
  `tool_filter` on the `McpToolset`. I wrote two allow-lists. The customer data
  toolset lists all 15 explicitly (an explicit allow-list is self-documenting
  and fails closed if the server later grows a tool this role should not
  auto-inherit). The support toolset lists only 10, withholding the five
  account-mutating or destructive ops: `add_customer`, `update_customer`,
  `disable_customer`, `activate_customer`, `delete_ticket`.
- The key property is that `tool_filter` enforces least privilege at the
  protocol layer, not in the prompt. A filtered tool is never discovered by the
  agent, so no amount of clever prompting can make the support agent disable an
  account or delete a ticket. Prompt-level "please do not" guards are advisory;
  a filter is structural.

### Data Agent Instruction
- The instruction frames the agent as a back-office system of record: precise,
  literal, data-driven, and explicitly NOT a troubleshooter (that separation
  keeps its behavior predictable and hands emotional/solution work to the
  support agent). It groups the tools into three categories (customer records,
  ticket lifecycle, analytics/search) so the model has a map of what it can do.
- It guides tool selection with a small procedure: identify the exact entity and
  operation, ask one clarifying question if an identifier is missing rather than
  guessing, then call the single most specific tool (get_ vs list_/search_). It
  also tells the agent to report tool results faithfully and never fabricate
  data the tools did not return, which is the main failure mode for a data
  agent.

---

## Part 2: Multi-Agent A2A System

### Support Agent Design
- The instruction embeds a small knowledge base for the four required issue
  classes plus feature requests and data export: login/lockout, password reset,
  payment/billing, and performance, each with concrete first-line steps. It also
  sets a response structure (acknowledge, customer context, category, solution
  steps, ticket action) and an empathetic tone.
- It is NOT tool-free. The support agent uses the filtered toolset to ground its
  help in the customer's real account and ticket history, and to open or update
  tickets. What it cannot do is mutate accounts or delete data, and the
  instruction tells it to escalate those to an administrator rather than fail
  silently.

### Host Agent Orchestration
- The `SequentialAgent` runs its two `RemoteA2aAgent` sub-agents in order and
  threads the conversation context through them. The Customer Data Agent runs
  first and looks up the account; because ADK carries the running conversation
  forward, the Support Agent then answers with that account context already in
  hand and does not have to re-fetch it.
- When the data agent returns, its output becomes part of the conversation the
  support agent sees. That is the "data lookup then guidance" workflow the
  assignment asks for, achieved by ordering plus shared context rather than by
  manually copying fields between agents.

### A2A Protocol Insights
- Discovery works through Agent Cards. Each agent publishes a card (name, url,
  description, capabilities, transport, skills-with-examples) that advertises
  what it can do. The host does not import the sub-agents; it is given their
  card URLs.
- The `.well-known/agent-card.json` endpoint is the fixed, conventional location
  where a running agent serves its card. `RemoteA2aAgent` fetches
  `{agent_url}{AGENT_CARD_WELL_KNOWN_PATH}`, reads the card, and learns how to
  talk to that agent. I saw this live in the logs: the host fetched
  `http://localhost:10020/.well-known/agent-card.json` and then "Successfully
  resolved remote A2A agent: customer_data".
- `RemoteA2aAgent` differs from a direct function call in that the host and the
  sub-agent are separate processes (here, separate ports) that communicate over
  A2A/JSON-RPC. The host has no Python reference to the sub-agent's code; it only
  has a card URL and speaks the protocol. That is what makes the agents
  independently deployable and swappable, at the cost of a network hop.

---

## Part 3: Challenges and Solutions

### Technical Challenges
- The hardest part was not the agent code, it was a narrow dependency window.
  The starter and tests import `McpToolset` (that exact casing) and
  `TransportProtocol` from `a2a.types`. But `google-adk` 1.9.0 only ships
  `MCPToolset` (all caps), while `a2a-sdk` 1.x removed `TransportProtocol`. So
  the code only imports on `google-adk` 2.x paired with `a2a-sdk` 0.3.x. A naive
  `pip install -r requirements.txt` with the shipped `>=` bounds installs the
  latest of both and breaks. I resolved it to `google-adk==2.4.0` +
  `a2a-sdk>=0.3.0,<1.0` and pinned those in requirements.txt so the grader
  reproduces a working environment.
- A second gotcha: the `McpToolset` import silently no-ops if the `mcp` package
  is not installed, because ADK guards the whole export block in a
  try/except ImportError. That turns a missing dependency into an empty module
  rather than a loud error.
- I debugged agent communication mostly from the server logs. The card-fetch and
  "resolved remote A2A agent" lines confirm discovery; the per-agent event
  authors in a run confirm which sub-agents actually executed.

### Architecture Decisions
- `SequentialAgent` fits the base case because the support step genuinely
  depends on the data step: you want the account context before you troubleshoot.
  Sequential ordering plus shared context expresses that dependency directly.
- The trade-off versus direct calls is latency and complexity for independence.
  A direct in-process call would be faster and simpler, but it couples the host
  to the sub-agents' code and deployment. A2A decouples them (separate services,
  discovered by card) at the cost of network round-trips and a protocol layer.

---

## Bonus: Routing Modes (attempted, both working)

### Advanced Router
- `analyze_query_intent` is a deterministic keyword classifier returning
  `needs_data`, `needs_support`, `urgency`, and `execution_mode`. Routing is a
  cheap, reproducible decision, so it does not spend an LLM call; the LLM stays
  downstream where the real work is. It fails safe: if it cannot classify, it
  runs the full pipeline rather than skipping a step.
- The decision is written to session state in the router's
  `before_agent_callback` (`store_routing_decision`). I did it there rather than
  in the instruction provider because ADK gives an instruction provider a
  read-only `ReadonlyContext.state`; only a `CallbackContext` can write. Each
  sub-agent then has its own `before_agent_callback` (`should_run_*`) that reads
  the decision and returns a skip `Content` when its flag is False, or `None` to
  run. I verified live that a data-only query skips the support agent entirely
  (it makes zero LLM calls).

### Parallel Router
- Parallel execution improves latency by running both sub-agents concurrently in
  a `ParallelAgent`, so wall-clock is the slower of the two rather than their
  sum.
- Synthesis strategy: `RemoteA2aAgent` has no `output_key` field (it subclasses
  `BaseAgent`, not `LlmAgent`), so I capture each remote's final text in an
  `after_agent_callback` and write it to state under `customer_data_output` /
  `support_specialist_output`. A final summary `LlmAgent` with
  `include_contents='none'` reads both from state via its dynamic instruction and
  merges them into one cohesive reply. I verified live that both outputs land in
  state and the summary combines them.

### Mode Comparison

| Mode | Agents Called | Latency | Context Passing |
|------|-------------|---------|-----------------|
| Basic (Sequential) | Both, always, in order | Sum of both | Shared conversation, data then support |
| Advanced (Dynamic) | Only the ones the query needs | Sum of the ones run | `routing_decision` in state + shared conversation |
| Parallel | Both, concurrently | Max of the two | Each output captured to state, merged by a summary agent |

---

## Key Learnings
1. A `tool_filter` is a real security boundary, not a hint: least privilege
   enforced at the protocol layer beats any instruction, because withheld tools
   are never even discovered.
2. A2A discovery via Agent Cards at a well-known URL is what decouples agents
   into independently deployable services; the host holds a card URL, never a
   code reference.
3. Framework version skew can be the whole problem. Reading which class and
   symbol names actually exist in the installed packages, and pinning to the
   window where the given code compiles, mattered more here than any single
   agent's logic.

## Ideas for Improvement
- Replace the keyword `analyze_query_intent` with a tiny classifier LLM call
  when queries get ambiguous, while keeping the deterministic path as the
  default and the fallback.
- Add ret/backoff around the Gemini calls for the free tier: the end-to-end run
  hit both the 5-requests-per-minute and the daily free-tier caps, and a small
  bounded retry (which ADK already does for some cases) makes the suite robust.
