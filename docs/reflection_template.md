# Assignment 4: Reflection

## Student Name: Gabe Jacobson

---

## Part 1: MCP Tools + Customer Data Agent

### Tool Design Decisions

The assignment provides an MCP server with customer, ticket, search, and statistics tools. I configured two ADK `McpToolset` factories instead of writing manual wrapper functions because the ADK McpToolset can auto-discover tools from the MCP server over SSE.

The Customer Data Agent receives broad access to all MCP tools because it is the internal data-management agent. It can retrieve and manage customer records, inspect tickets, update tickets, and view statistics.

The Support Agent receives a filtered support-safe toolset. It can look up customers and tickets, search tickets, create tickets, and update ticket status/priority, but it cannot perform destructive or administrative operations such as disabling customers, activating customers, deleting tickets, adding customers, or updating customer master records.

### Data Agent Instruction

The Customer Data Agent instruction defines it as the authoritative source for customer and ticket facts. The instruction tells the agent to parse identifiers, use MCP tools instead of guessing, ask clarifying questions when required fields are missing, and communicate errors gracefully.

---

## Part 2: Multi-Agent A2A System

### Support Agent Design

The Support Agent includes a support knowledge base covering login issues, password resets, billing/payment issues, performance issues, feature requests, and data export issues. Its instruction emphasizes empathy, safe tool use, and structured responses: acknowledge the issue, summarize retrieved context, categorize the issue, provide troubleshooting steps, and state any ticket action.

The Support Agent can handle general troubleshooting without external tools, but it uses the MCP toolset when it needs customer context or ticket actions.

### Host Agent Orchestration

The Host Agent uses a `SequentialAgent` with two `RemoteA2aAgent` sub-agents. The first remote agent calls the Customer Data Agent to retrieve account and ticket context. The second remote agent calls the Support Agent to produce customer-facing guidance. This sequence is appropriate because support recommendations are stronger when account and ticket context are gathered first.

### A2A Protocol Insights

Agent discovery works through `AgentCard` metadata exposed at the well-known agent card URL. The Host Agent does not directly import and call the other agents' functions; instead, it uses `RemoteA2aAgent` wrappers that communicate with the remote agents through the A2A protocol. This preserves agent boundaries and simulates a distributed multi-agent system.

---

## Part 3: Challenges and Solutions

### Technical Challenges

The main challenge was coordinating three layers at once: ADK agent construction, MCP tool filtering, and A2A remote-agent orchestration. I addressed this by implementing and validating each layer separately: first MCP toolsets, then individual agents, then AgentCards and the Host Agent.

### Architecture Decisions

The `SequentialAgent` pattern is appropriate because the workflow has a natural dependency order: data lookup should occur before support guidance. A direct function-call design would be simpler, but it would not demonstrate A2A agent boundaries or discovery through AgentCards. The tradeoff is that A2A orchestration adds more setup complexity and more places where configuration errors can happen.

---

## Bonus: Routing Modes

I focused on the required basic sequential architecture for reliability. A future version could add dynamic routing to skip the Customer Data Agent for purely general troubleshooting questions, or use a parallel router to reduce latency when data lookup and support reasoning can safely happen simultaneously.

### Mode Comparison

| Mode | Agents Called | Latency | Context Passing |
|------|-------------|---------|-----------------|
| Basic (Sequential) | Customer Data Agent, then Support Agent | Medium | Strong ordered context |
| Advanced (Dynamic) | Depends on query intent | Lower for simple queries | Conditional context |
| Parallel | Customer Data Agent and Support Agent together | Lower | Requires synthesis step |

---

## Key Learnings

1. MCP tool filtering is useful for enforcing role-appropriate permissions.
2. A2A AgentCards make remote agent discovery explicit and inspectable.
3. Sequential orchestration is a good fit when one agent's output should inform the next agent's response.

## Ideas for Improvement

- Add dynamic routing for data-only or support-only questions.
- Add a parallel execution mode with a synthesis agent.
- Add more robust schema validation for agent outputs.
- Add automated integration tests with the MCP server running.
