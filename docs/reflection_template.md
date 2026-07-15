# Assignment 4: Reflection

## Student Name: Ryan Whelan

---

## Part 1: MCP Tools + Customer Data Agent

### Tool Design Decisions
- Which MCP tools did you implement and why?

  The 15 MCP tools themselves (get_customer, list_customers, add_customer, update_customer, disable_customer, activate_customer, get_ticket, list_tickets, create_ticket, update_ticket_status, update_ticket_priority, delete_ticket, get_ticket_stats, get_customer_stats, search_tickets) were provided as part of the starter MCP server, not something I wrote. What I actually built was the tool_filter lists that control which of those 15 tools each agent is allowed to use. The Customer Data Agent gets all 15, since its job is broad account and ticket management. The Support Agent gets 10, with the 5 admin or destructive ones removed (disable_customer, activate_customer, delete_ticket, add_customer, update_customer). The logic is basically least privilege. A frontline support rep should be able to look up an account and open a ticket, but shutting off someone's account or deleting records is a decision that belongs to an admin, not a chatbot handling a support ticket.

- How did you design the tool signatures for ADK compatibility?

  I didn't write tool signatures directly. The MCP server already defines each tool with type hints and a docstring, and that is what MCP uses to auto-generate the schema the model sees. My job was just choosing the right subset per agent through McpToolset's tool_filter parameter and pointing each toolset at the MCP server's SSE endpoint. No manual JSON schema work was needed on my end. That is actually the interesting part of MCP as a protocol: the tool definitions live in one place, the server, instead of being duplicated in every agent that wants to use them.

### Data Agent Instruction
- What capabilities did you include in the system instruction?

  I listed what the agent can do (look up a customer, list customers by status, create or update customer records, enable or disable accounts, look up or list or search tickets, create tickets, update ticket status or priority, pull stats), then gave it a three step process: parse the request, call the right tool with the right parameters, and turn the raw JSON response into a readable summary instead of dumping it on the user. I also told it not to guess when a tool fails or a customer is not found, and to say so plainly rather than making something up.

- How does the instruction guide the agent's tool selection?

  Since ADK auto-discovers the tools from the MCP server, I did not need to hardcode rules like "if the user says X, call function Y." The model reads the tool descriptions itself and picks. My job was describing the domain clearly enough (customer versus ticket, lookup versus create versus update) that the model's own judgment lines up with what I intended, and being explicit about response style so it does not just paste back raw JSON.

---

## Part 2: Multi-Agent A2A System

### Support Agent Design
- What knowledge did you embed in the support agent's instruction?

  I built a small knowledge base directly into the instruction text, covering the categories the assignment specified: login issues (lockouts, password resets), payment and billing issues (failed transactions, double charges), performance issues (slow loading, timeouts), and feature requests or data export questions. For each category I gave concrete guidance, for example that accounts lock for 15 minutes after repeated failed login attempts, or that billing errors should be treated as high priority since real money is involved. I also gave it rules for when to create a new ticket versus update an existing one, and what priority level to assign based on the type of issue.

- How does it handle queries without external tools?

  If someone asks a general question, like how to reset a password, the agent can answer straight from the knowledge base written into the instruction, no tool call needed. It only reaches for a tool when the query needs actual account or ticket data, for example when the customer gives an ID or references an existing ticket. That split is useful: the policy knowledge lives in the prompt, the live data comes from tools.

### Host Agent Orchestration
- How does the SequentialAgent coordinate between sub-agents?

  A SequentialAgent runs its sub-agents one after another in a fixed order and carries the conversation forward between them. In this system, the Customer Data Agent runs first and does the lookup, and its output becomes part of what the Support Agent sees when it runs second. The Support Agent is not calling the Customer Data Agent directly. The orchestrator is simply handing both agents the same growing conversation in turn.

- What happens when the Customer Data Agent returns data to the Support Agent?

  I tested this directly by asking the host agent to check account 5 and create a ticket for a billing issue. The Customer Data Agent looked up the account and created ticket 27. When the Support Agent ran next, it saw that ticket already existed in the conversation and, based on the billing guidance in its own instruction, raised its priority to high instead of creating a duplicate. That is the payoff of running the agents in sequence. The second agent is not working blind, it has the first agent's findings in front of it.

### A2A Protocol Insights
- How does agent discovery work via AgentCards?

  Each agent publishes an AgentCard, a small JSON profile listing its name, URL, description, and a list of skills with example queries. Any other agent, or the host orchestrator, can fetch that card to learn what an agent does and how to reach it, without needing hardcoded knowledge of its internals. It is similar to a vendor capability sheet. Before you hand work to someone, you check what they are actually equipped to do.

- What role does the `.well-known/agent-card.json` endpoint play?

  It is a fixed, predictable URL path that every A2A compliant agent server exposes its card at. Because the path is standardized, RemoteA2aAgent only needs an agent's base URL. It appends the well known path itself and fetches the card automatically. I confirmed this worked by hitting that exact path with curl for all three agents and getting back their profiles.

- How does RemoteA2aAgent differ from direct function calls?

  A direct function call happens in the same process and the same memory space, no network involved. RemoteA2aAgent instead treats another agent as a genuinely separate service, reachable over HTTP, with its own server, its own model calls, and its own tool access. That means the Customer Data Agent and Support Agent could be written in different frameworks, run on different machines, or scaled independently, and the host agent would not need to know or care. The tradeoff is actual network latency and more moving parts (three separate server processes had to be running for any of this to work), against the flexibility of loosely coupled services.

---

## Part 3: Challenges and Solutions

### Technical Challenges
- What was the most difficult part of the implementation?

  Two things stood out. One was environment setup: the starter repo's requirements.txt did not pin exact versions, so a plain install pulled the newest google-adk and a2a-sdk, and those newer versions had renamed or moved several things the starter code depended on. A class called McpToolset did not exist under that name in one version, a compatibility patch written for older versions broke on a newer one, and a type called TransportProtocol had moved to a different location. None of that was a bug in my own code, it was version drift between when the assignment was written and when I set it up.

  The less mechanical challenge was deciding where one agent's job should end and another's should begin. With three agents working together, it is easy to let responsibilities blur, for example letting the Support Agent quietly handle an account change because it is convenient in the moment, or letting the Customer Data Agent start giving troubleshooting advice because it already has the account info in front of it. I had to be deliberate about drawing that line: the Customer Data Agent owns lookups and record changes, the Support Agent owns diagnosis and guidance and only touches data through a narrower, non-destructive set of tools. That scoping decision is really what the tool_filter choices in Part 1 and the instruction writing in Part 2 were both in service of.

- How did you debug agent communication issues?

  I worked one layer at a time instead of testing the whole system at once. First I confirmed the MCP server was reachable directly with curl. Then I checked each agent server's `.well-known/agent-card.json` endpoint to confirm it was up and returning the right metadata. Only after both of those were confirmed did I test the full multi-agent flow through the host agent. That layering made it obvious which piece was actually broken instead of guessing across the whole stack.

### Architecture Decisions
- Why is the SequentialAgent pattern appropriate for this use case?

  Support conversations usually have a natural order of dependency. You need to know who the customer is and what is going on with their account before you can give good troubleshooting advice. SequentialAgent enforces that order deliberately, data lookup first, support guidance second, so the second agent always has actual context instead of guessing.

- What are the trade-offs vs. direct agent calls?

  The A2A approach is slower, since each step is a network call to a separate server with its own model call, and it has more failure points, since three servers all have to be up and reachable at the same time. A direct function call, all in one process, would be faster and simpler for a system this size. The payoff of A2A is architectural: you get genuinely independent, swappable services, which matters more as a system grows or gets built by separate teams. For a project this size it is arguably heavier than necessary, but it demonstrates the pattern you would actually want at scale.

---

## Bonus: Routing Modes (if attempted)

### Advanced Router
- How does the dynamic routing decide which agents to call?

  I wrote a simple keyword matching function that checks the query for data related words (customer, ticket, account, list, search) and support related words (help, issue, reset, password, billing, login). If it finds only data words, it skips the support agent. If it finds only support words, it skips the data agent. If it finds neither, it plays it safe and runs both rather than risk missing something the user actually needed.

- What callback patterns did you use?

  ADK lets you attach a before_agent_callback to any agent, which runs right before that agent executes and can return a skip response instead of letting the agent run. I used two of these, one on the Customer Data Agent and one on the Support Agent, each checking a shared routing decision to decide whether to actually run, or return a short message saying it was not needed for this query. I also had to add a third callback, on the router agent itself, to actually save that routing decision. The assignment's own instructions describe writing it into a certain read only context object, but that does not work in the ADK version I had installed, it raises an error since that object is genuinely read only in this version. I found a different, working way to persist the decision so the callbacks downstream could read it, then tested with two different queries to confirm each specialist agent was genuinely skipped when it should have been, not just skipped on paper.

### Parallel Router
- How does parallel execution improve latency?

  In the basic and advanced modes, the Customer Data Agent and Support Agent run one after another, so the total time is roughly the sum of both. In parallel mode they run at the same time, so the total time is closer to whichever one is slower, not the sum of both. For a query that genuinely needs both agents, that can meaningfully cut down wait time.

- What synthesis strategy did you use to combine results?

  Each agent's output gets saved into shared state under its own key. Once both finish, a separate summary agent reads both saved outputs and is instructed to merge them into one natural response, keeping specific facts like ticket numbers exact, without mentioning that two separate agents were involved. I had to build the actual save mechanism by hand as well, since the usual shortcut for that, an output_key setting, only exists on ADK's built in agent type and not on the remote agent type used to reach the other servers over A2A.

### Mode Comparison

| Mode | Agents Called | Latency | Context Passing |
|------|-------------|---------|-----------------|
| Basic (Sequential) | Both agents, every time | Slowest. Calls happen one after another regardless of relevance | Full. Second agent sees everything the first one produced |
| Advanced (Dynamic) | Only the agent or agents the query actually needs | Fastest for single topic queries, same as basic for mixed queries | Full when both run, none needed when one is skipped |
| Parallel | Both agents, every time | Faster than basic when both are needed, since they run at the same time instead of one after another | Indirect. Agents do not see each other's output while running, a summary step combines results afterward |

---

## Key Learnings
1. The tools existing on paper is not the same as them being usable. Most of the work in this assignment was deciding who gets access to which tool and why, not building the tools themselves.
2. Multi-agent systems add latency and failure points compared to keeping logic in one process. A2A is a genuine architectural choice with a cost, not a free upgrade you get just by using the protocol.
3. Course starter code can go stale fast when it depends on fast moving libraries. Reading the actual error message and checking installed package versions was more useful than assuming my own code was wrong.

## Ideas for Improvement
- Restructure the advanced router so a skipped agent's placeholder message can never become the final visible response. Right now, if the last agent in the sequence gets skipped, its skip message is what the user sees instead of the actual answer the agent before it already produced.
- Add a lightweight retry or backoff path for when the underlying model hits a rate limit, since a live multi-agent system making several model calls per query can burn through a free tier quota quickly.
