# Assignment 4: Reflection

## Student Name: Arjun Kallapur

---

## Part 1: MCP Tools + Customer Data Agent

### Tool Design Decisions

The MCP server and its 15 tools were provided, so my implementation focused on
configuring role-based access rather than rewriting the tools. The Customer Data
Agent receives all 15 customer, ticket, search, and statistics tools because it
is responsible for broad data management. The Support Agent receives 10
support-safe tools. It can look up customers, view and search tickets, create or
update tickets, and retrieve statistics, but it cannot add or update customers,
activate or disable accounts, or delete tickets.

The provided FastMCP tools use explicit, serializable parameters and return data
that can be represented through the MCP protocol. Google ADK's `McpToolset`
discovers those signatures automatically over SSE. Each agent therefore only
needs an `SseConnectionParams` connection and a `tool_filter` containing exact
MCP tool names; no ADK-specific wrapper functions are necessary.

### Data Agent Instruction

The Customer Data Agent instruction covers customer lookup and management,
ticket retrieval and management, search, and aggregate statistics. It tells the
agent to treat MCP results as authoritative, preserve important identifiers and
statuses, request missing identifiers, and avoid inventing data.

The instruction guides tool selection by asking the agent to identify the
entity, operation, filters, and identifiers before choosing the narrowest
appropriate tool. It also requires explicit intent before destructive or
administrative actions and explains how to respond when records are missing or
the MCP service fails.

---

## Part 2: Multi-Agent A2A System

### Support Agent Design

The Support Agent instruction includes guidance for login and password-reset
issues, account lockouts, billing and payment problems, performance issues,
feature requests, and data-export failures. It also describes urgency
classification, escalation conditions, duplicate-ticket avoidance, ticket
creation and updates, privacy safeguards, and an empathetic response style.

For general troubleshooting questions, the agent can answer from its embedded
knowledge without calling a tool. When the answer depends on a particular
customer, account, or ticket, it uses its support-safe MCP tools. If a tool is
unavailable, the instruction tells it to acknowledge the limitation, avoid
guessing, provide safe general guidance, and offer a retry or escalation path.

### Host Agent Orchestration

The basic host is a `SequentialAgent` containing two `RemoteA2aAgent`
sub-agents. It calls the Customer Data Agent first and the Support Agent second.
This order allows the first stage to retrieve relevant customer and ticket
context before the second stage generates troubleshooting guidance.

The Customer Data Agent's response becomes part of the shared sequential
conversation context. The Support Agent can use that context along with the
original request to personalize its response, avoid repeating data collection,
and recommend or perform an appropriate ticket action.

### A2A Protocol Insights

Each service publishes an `AgentCard` describing its name, URL, protocol
capabilities, input and output modes, transport, skills, tags, and example
requests. A client or host agent can inspect this metadata to discover what the
remote agent can do without relying on an application-specific Python API.

The `.well-known/agent-card.json` endpoint is the standard discovery location
for this metadata. The host constructs each remote card URL from the configured
agent base URL and `AGENT_CARD_WELL_KNOWN_PATH`. This lets
`RemoteA2aAgent` discover the remote service and communicate using the A2A
JSON-RPC transport.

A `RemoteA2aAgent` makes a protocol request to an independently hosted agent.
Unlike a direct function call, it crosses a service boundary, uses a published
capability contract, and does not require the remote implementation to be in
the same process or even use the same internal framework. The trade-off is
additional network latency and more failure modes, such as unavailable servers
or invalid discovery metadata.

---

## Part 3: Challenges and Solutions

### Technical Challenges

**Most difficult part:** Since I used the Codex AI model for coding assistance, coding was not the main challenge, rather the biggest issues were initial environment setup and getting everything up and running, as well as the plumbing work needed to get everything to work well together.

**Debugging agent communication:** The main way I debugged agent communication was by running each agent on its own, to ensure I could test the agents individually before getting into the whole system.

### Architecture Decisions

The sequential pattern is appropriate because customer support often has a
natural dependency: retrieve authoritative account and ticket context first,
then use that context to diagnose the issue and recommend next steps. The
ordering is easy to understand, produces predictable behavior, and reduces the
chance that the support response is based on assumptions.

Compared with direct calls, the A2A-based sequential design is more modular and
allows each specialist to be deployed, discovered, tested, and scaled
independently. It also provides a standard boundary between agents. Its costs
are extra latency, network and serialization overhead, and operational
complexity. The basic mode also invokes both agents even when a request only
needs one, which motivated the advanced routing mode.

---

## Bonus: Routing Modes

### Advanced Router

The advanced router performs deterministic keyword-based intent analysis. It
classifies whether a query needs data, support, or both; assigns low, medium, or
high urgency; and selects `data_only`, `support_only`, or `sequential`
execution. Unrecognized requests default to support so the workflow does not
accidentally skip every worker.

A dynamic router instruction stores the decision in shared agent state.
`before_agent_callback` functions read that decision before each remote worker
runs. A callback returns `None` when the worker should execute and returns a
`Content` response when the worker should be skipped.

### Parallel Router

Parallel execution can reduce latency for requests where customer-data lookup
and support analysis do not depend on each other's immediate output. A
`ParallelAgent` sends the request to both remote specialists concurrently
instead of waiting for one network and model call to finish before starting the
other.

Each remote agent stores its result under a separate `output_key` in shared
state. A final synthesis agent reads both values and combines them into one
concise response. Its instruction preserves identifiers and confirmed actions,
removes duplication, organizes next steps, and prevents it from inventing a
result when one worker fails.

### Mode Comparison

| Mode | Agents Called | Latency | Context Passing |
|------|---------------|---------|-----------------|
| Basic (Sequential) | Customer Data, then Support | Highest for simple requests; two stages run in order | Support receives the preceding data-agent context |
| Advanced (Dynamic) | Data, Support, or both based on intent | Lower when an unnecessary worker is skipped | Routing decision is stored in state; sequential context is used when both run |
| Parallel | Customer Data and Support concurrently, then Synthesizer | Lower worker-stage latency when both calls are needed, plus synthesis time | Worker outputs are stored under separate state keys and merged by the synthesizer |

---

## Key Learnings

1. MCP separates tool implementation from agent integration: ADK can discover
   typed tools remotely while `tool_filter` enforces least-privilege access.
2. A2A AgentCards and standard discovery endpoints allow independently hosted
   agents to collaborate without direct implementation-level coupling.
3. Orchestration strategy is a trade-off: sequential execution provides clear
   dependencies, dynamic routing avoids unnecessary work, and parallel
   execution can reduce latency but requires explicit result synthesis.

## Ideas for Improvement

- Replace keyword routing with structured model classification and a validated
  routing schema while retaining deterministic fallbacks.
- Add retries, timeouts, health checks, authentication, tracing, and tests for
  partial failures across the MCP and A2A service boundaries.
- Add a confirmation or authorization layer for destructive Customer Data Agent
  operations and improve duplicate-ticket detection.
