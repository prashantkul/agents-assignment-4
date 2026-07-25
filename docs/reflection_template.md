# Assignment 4: Reflection

## Student Name: Sonia Mann

## Part 1: MCP Tools + Customer Data Agent

### Tool Design Decisions
The MCP tools were already provided through the MCP server (mcp_server/app.py), so my role was not to create new tools but to configure how each agent could access them. The MCP server exposes 15 database tools through SSE, covering customer management, ticket management, and statistics/search operations.

For the Customer Data Agent, I configured the MCP toolset with full access to all 15 tools by not applying a tool_filter. The reason for this design choice was that the Customer Data Agent’s role is to act as a data lookup and management agent. It needs broad access to retrieve customer records, view tickets, create tickets, update ticket information, and access statistics.

For the Support Agent, I created a separate filtered toolset with only support-safe tools. I removed administrative or destructive actions such as disabling customers, activating accounts, deleting tickets, adding customers, and updating customer records. This follows the principle of least privilege because the Support Agent should be able to help customers but should not have access to operations that could negatively impact customer data.

For ADK compatibility, I did not create custom wrapper functions for each MCP operation. The MCP server already defines the tool schemas, and ADK’s McpToolset automatically discovers those tools through the SSE connection. My configuration only needed the SseConnectionParams(url=MCP_SSE_URL) connection and the appropriate tool filter settings.

### Data Agent Instruction
For the Customer Data Agent, I designed the system instruction to clearly define that its role is a data lookup clerk, not a customer support advisor. The goal was to keep the agent focused on retrieving and managing customer and ticket information rather than trying to solve customer problems itself.

The instruction included:

The agent’s role and responsibilities
Available categories of tools
How to select the correct tool based on user intent
Expected response formatting
Error handling behavior

I guided the agent through a structured workflow:

Understand the user’s request
Identify the type of information needed
Select the appropriate MCP tool
Execute the request
Return accurate, structured results

For example:

“Get customer 5’s information” → get_customer
“Show all open tickets” → list_tickets
“How many tickets are open?” → get_ticket_stats

The instruction also emphasized that the agent should never fabricate information. If a tool fails or required information is missing, it should clearly communicate the issue rather than guessing.

### Part 2: Multi-Agent A2A System

### Support Agent Design
The Support Agent required a different design philosophy. Unlike the Customer Data Agent, its purpose was not simply retrieving information. Its job was to combine customer context with troubleshooting knowledge and provide helpful guidance.

I created a knowledge base covering common support scenarios:

Login issues
Billing problems
Performance issues
Feature requests
Data export problems

However, I did not make the agent completely dependent on static instructions. The Support Agent still uses MCP tools through create_support_toolset() when it needs customer-specific information.

For example:

A general question like “How do I reset my password?” can be answered from the knowledge base.
A question like “Why is John’s account locked?” requires retrieving customer data first.

The response structure was designed to provide consistency:

Customer context
Issue category
Troubleshooting steps
Ticket actions taken

This helped balance conversational support with data-driven responses.

### Host Agent Orchestration
The Host Agent was where I started seeing the bigger picture of agentic architecture.

Instead of directly importing Python modules and calling functions, I implemented communication using A2A. The Host Agent uses a `SequentialAgent` with two `RemoteA2aAgent` sub-agents:

- Customer Data Agent running on port 10020
- Support Specialist Agent running on port 10021

The workflow follows:

Customer Data Lookup → Support Reasoning → Final Response

The Customer Data Agent runs first and retrieves relevant customer or ticket information using MCP tools. The Support Agent then receives that information through the shared conversation context and uses it along with its troubleshooting knowledge to generate a more personalized response.

One of the biggest insights from this design was understanding that agents can have specialized responsibilities instead of creating one large agent that handles everything. The Customer Data Agent acts as the information retrieval layer, while the Support Agent focuses on customer interaction and problem solving.

The Host Agent’s role is only orchestration. It coordinates the workflow but does not contain the business logic of either specialist agent.


### A2A Protocol Insights
Agent discovery in A2A is handled through AgentCards. I think of an AgentCard as a profile or business card for an agent. It describes what the agent does, where it is located, and how another system can communicate with it.

In this project, each agent has an AgentCard that defines important information such as:

- Agent name and description
- Agent URL
- Available capabilities
- Supported transport protocol
- Skills and example queries

The Host Agent uses this information to understand what each remote agent can do before sending requests. This allows agents to be discovered dynamically instead of requiring hard-coded imports or direct knowledge of another agent’s code.

The main learning for me was that A2A creates a more service-oriented architecture. Agents advertise their capabilities, and other agents can discover and use them without needing to know how they were built internally.

The `.well-known/agent-card.json` endpoint is the standard location where an agent publishes its AgentCard information.

For example, the Customer Data Agent exposes its AgentCard through:

`http://localhost:10020/.well-known/agent-card.json`

When the Host Agent creates a `RemoteA2aAgent`, it uses this endpoint to retrieve the remote agent’s metadata. The AgentCard provides the information needed to communicate with the agent, including its capabilities, skills, and communication details.

The benefit of using a standard endpoint is that any A2A-compatible client knows where to look for an agent’s information. This improves interoperability because agents can be added, replaced, or updated without changing the entire system architecture.

The biggest difference is that `RemoteA2aAgent` communicates with another agent as an independent service, while direct function calls require both components to exist inside the same application.

With direct function calls, the Host Agent would need to import another agent’s Python module and know exactly how to call its functions. This creates tight coupling between components.

With `RemoteA2aAgent`, the Host Agent only needs the remote agent’s URL and AgentCard information. Communication happens through the A2A protocol using network messages rather than direct Python execution.

The trade-offs are:

A2A provides:
- Independent deployment
- Process isolation
- Agent discovery through AgentCards
- Ability to scale agents separately

Direct function calls provide:
- Lower latency
- Less configuration
- Simpler implementation

For this assignment, using A2A was the better design because the goal was not just to make agents work together, but to build a true multi-agent system where each agent can operate as an independent, discoverable service.


## Part 3: Challenges and Solutions

The most difficult part of the implementation was not writing the individual agents, but making sure all of the pieces worked together correctly across MCP, ADK, and A2A. Since this assignment involved multiple layers of communication, a small configuration issue in one area could affect the entire system.

One challenge was resolving the difference between the starter code comments and the README requirements for the Customer Data Agent tool access. The starter file suggested a more limited tool list, but the assignment requirements stated that the Customer Data Agent should have access to all 15 MCP tools. After reviewing the architecture, I determined that the intended design was for the Customer Data Agent to have full access and the Support Agent to have filtered access. I resolved this by removing the `tool_filter` from the Customer Data Agent toolset and allowing ADK's `McpToolset` to automatically discover all available tools.

Another challenge was handling compatibility issues between ADK and the A2A SDK. While implementing the parallel routing bonus, I found that `RemoteA2aAgent` did not accept the `output_key` parameter in the installed ADK version. The error was caused by a Pydantic validation issue because the parameter was not supported. I solved this by creating a fallback approach that stored agent outputs using `after_agent_callback` while maintaining the expected state keys.

For debugging agent communication issues, I used an incremental testing approach rather than debugging the entire system at once. I first verified the MCP tool configuration, then tested the individual agents, and finally tested the A2A communication layer.

My testing progression was:

- Initial agent tests: 7/9 passing
- After implementing the Support Agent: 11/12 passing
- After implementing the Host Agent: 14/14 passing
- After completing AgentCards and A2A integration: 17/17 passing

This approach helped me isolate whether an issue was coming from tool configuration, agent instructions, orchestration, or A2A communication.

The biggest lesson I learned from debugging this project was that multi-agent systems require validating each layer independently. The agents, tools, and communication protocols all depend on each other, so testing each component separately made it much easier to identify and fix problems.

### Architecture Decisions
The SequentialAgent pattern was appropriate for this customer support system because the workflow naturally follows a two-step process: first gather accurate information, then provide support guidance.

The Customer Data Agent acts as the fact-gathering layer. It uses MCP tools to retrieve customer records, ticket information, and statistics. Once that information is available, the Support Agent can use the data along with its troubleshooting knowledge to provide a more personalized response.

Using a sequential workflow prevents the Support Agent from making assumptions or providing generic troubleshooting steps without understanding the customer’s actual situation. The order is intentional:

Customer Data Agent → Support Agent

Another advantage of the SequentialAgent pattern is that context passing is handled automatically. When the Customer Data Agent completes its task, the results become part of the shared conversation context that the Support Agent receives in the next step. This avoids needing to build custom handoff logic between agents.

This design also creates a clear separation of responsibilities. The Customer Data Agent focuses on retrieving accurate information, the Support Agent focuses on customer communication and problem solving, and the Host Agent is responsible only for orchestration.

Compared with direct agent calls, the SequentialAgent with A2A introduces additional complexity. Direct function calls would be faster because everything happens inside the same process, with no network communication or AgentCard discovery. They are also simpler to implement for a small application.

However, direct calls create tighter coupling because the Host Agent would need to know the internal implementation of each agent. This makes it harder to update, deploy, or scale agents independently.

The A2A approach adds overhead through separate services, network communication, and agent discovery, but it provides important benefits. Each agent can run independently, advertise its capabilities through AgentCards, and be replaced or updated without changing the entire system.

For this assignment, the SequentialAgent pattern was the right choice because customer support has a natural workflow order. The data retrieval step improves the quality of the support response, while A2A provides a foundation for building more scalable multi-agent systems.
--

## Bonus: Routing Modes (if attempted)

### Advanced Router
- How does the dynamic routing decide which agents to call?

The Advanced Router was designed to make the system more efficient by deciding whether a user request actually requires the Customer Data Agent, the Support Agent, or both.

The router analyzes the user’s query using the `analyze_query_intent()` function. It looks for indicators that the request requires customer data, support assistance, or both.

For example, requests containing words related to customer records, tickets, accounts, search, or statistics are classified as requiring the Customer Data Agent. Requests involving issues such as login problems, passwords, billing, troubleshooting, or fixes are classified as requiring the Support Agent.

The router also evaluates urgency based on keywords such as urgent, critical, or ASAP.

Based on the analysis, the router determines the execution mode:

- `data_only` → only the Customer Data Agent runs
- `support_only` → only the Support Agent runs
- `sequential` → both agents run when both types of information are needed

If the router cannot determine the intent confidently, it defaults to running both agents. This provides a safer fallback because missing information is usually more problematic than performing an additional agent call.

The goal of this pattern was to reduce unnecessary agent execution. For example, a simple question like “How do I reset my password?” does not require a customer database lookup, while a question like “Check my account and help resolve my ticket” requires both agents.

---

- What callback patterns did you use?

I used ADK `before_agent_callback` functions to control whether each agent should execute after the router makes its decision.

The Customer Data Agent uses `should_run_customer_data_agent()`, which checks the routing decision stored in session state. If customer data is not needed, the callback returns a skip response instead of running the agent. If customer data is needed, it returns `None`, allowing the agent to execute normally.

The Support Agent uses the same pattern through `should_run_support_agent()`, checking whether support assistance is required.

The callback behavior follows this pattern:

- Returning `None` → allow the agent to run
- Returning a `Content` response → skip the agent

The router first analyzes the query, stores the routing decision in session state, and then the callbacks use that shared state to determine execution.

One important learning from this pattern was understanding how agent workflows can become more intelligent. Instead of always running every agent, the system can dynamically decide which specialists are actually needed, reducing unnecessary computation and improving efficiency.

### Parallel Router
The Parallel Router improves latency by allowing the Customer Data Agent and Support Agent to execute at the same time instead of waiting for one agent to finish before starting the next.

In the basic SequentialAgent workflow, the execution time is approximately:

Customer Data Agent time + Support Agent time

because the Support Agent must wait for the Customer Data Agent to complete.

With the ParallelAgent pattern, both agents run concurrently, so the execution time is closer to:

The slower of the two agent runtimes

This reduces the overall response time for queries that require both customer data and support guidance.

The trade-off is that parallel execution changes how information is shared. Unlike the sequential workflow, the Support Agent does not automatically receive the Customer Data Agent’s output before it responds because both agents start with the same initial user request.


### What synthesis strategy did you use to combine results?

Because the agents run independently in parallel, I used a separate summary agent to combine their outputs into one final response.

The Customer Data Agent output and Support Agent output are stored in session state using the keys:

- `customer_data_output`
- `support_specialist_output`

After both agents complete, the summary agent reads these outputs and creates a unified response.

The summary agent is instructed to combine factual information from the Customer Data Agent with troubleshooting guidance from the Support Agent. It prioritizes the most relevant information, avoids repeating duplicate content, and maintains a professional and empathetic customer support tone.

This approach separates the responsibilities:

The parallel agents focus on solving their individual tasks, while the summary agent focuses on communication and presenting a complete answer.

The main benefit is improved performance, while the additional synthesis step ensures the final response still provides a complete customer experience.
		
## Key Learnings

1. One of my biggest takeaways from this assignment was understanding that building effective AI systems is not just about creating a powerful model. The architecture around the model matters just as much. MCP, A2A, and agent orchestration each solve different problems: MCP provides agents with access to external tools and data, A2A allows agents to communicate as independent services, and orchestration patterns determine how agents collaborate.

2. I learned the importance of giving agents clear responsibilities instead of creating one large agent that tries to handle every task. In this project, separating the Customer Data Agent from the Support Agent improved reliability because each agent had a focused purpose. The data agent was responsible for retrieving accurate information, while the support agent focused on troubleshooting and customer communication.

3. I learned that multi-agent systems require careful design around communication, permissions, and context sharing. Tool filtering was not just a configuration choice; it became a security boundary. Giving the Support Agent fewer MCP tools reduced the risk of unwanted actions, while the A2A architecture allowed agents to remain independent and scalable.

4. Debugging this project also improved my understanding of how complex AI systems are built. Testing each layer independently helped me understand where failures occurred and reinforced the importance of validating tools, agents, and communication protocols separately before integrating everything together.

## Ideas for Improvement

One improvement would be replacing the keyword-based routing logic in the Advanced Router with an LLM-based intent classifier. The current approach works for clear queries, but an LLM classifier would handle ambiguous requests more accurately and understand user intent beyond specific keywords.

Another improvement would be adding more automated integration tests that send real user queries through each `HOST_AGENT_MODE` and validate the final responses. This would help catch issues across the complete workflow, including MCP calls, A2A communication, and response synthesis.

The parallel router could also be improved by adding structured output schemas instead of relying on free-form text responses. For example, the Customer Data Agent could return structured customer information, the Support Agent could return troubleshooting actions, and the summary agent could combine those fields into a consistent response format for a user interface.

A future enhancement would be adding monitoring and observability across the agents. Tracking agent decisions, tool usage, response time, and failures would make it easier to manage a production multi-agent system.

Overall, this assignment helped me see that the future of AI applications will likely involve multiple specialized agents working together rather than one general-purpose agent handling every responsibility. The next step would be building more production-ready systems with better routing, monitoring, and structured communication between agents.        