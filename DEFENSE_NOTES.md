# C5 — Concepts and design decisions

**Habib Shouman**

**Why MCP instead of ordinary Python calls?** Python service methods implement behavior. MCP adds a discoverable, typed process boundary reusable by compatible hosts. A single application could call these methods directly, but C5 specifically asks for MCP interoperability. The model does not execute Python directly.

**Host, Client and Server:** the Host is the whole application coordinating the model and user. Its MCP Client is the protocol component connected to a particular Server. The Server implements capabilities. The language model itself is not the MCP Client.

**Where is the agent?** `Agent` and `Runner` let the model select a tool from descriptions, construct arguments and interpret feedback over multiple turns. This supports calling it a bounded tool-using agent. The lookup/save coordinator is a fixed workflow. There are no cooperating agents, learning loop or autonomous scheduling claims.

**Why is saving a local record an Action?** It changes persistent SQLite state outside the model context. An external network service is not necessary for a genuine effect. Returning a JSON object without persisting anything would not demonstrate that effect; independent database inspection matters.

**Why not split the Orchestration tool because its description contains “and”?** Its sole higher-level objective is creating a study plan at a catalogue space. It delegates two distinct responsibilities to the Data and Action implementations. The assignment explicitly asks for this kind of coordination. Conversely, the Action tool does not also select or look up a location.

**Do the tools call one another?** The coordinator invokes the exact same application methods used by the two MCP wrappers. It does not send nested MCP messages to its own server. This avoids transport overhead and decorator-version pitfalls while preserving functional reuse. Server logs show both internal steps; these are not extra external tools/call messages.

**What does idempotent mean here?** If the same request_id and normalized payload are retried, persistent state gains at most one row. The response may differ (`created` becomes false). Reusing an ID with a different payload is an error. Distinct IDs can create duplicate-looking sessions by design. The key is scoped to one database; this is not a distributed exactly-once claim.

**What is verified?** Local deterministic checks establish specific application behaviors. Protocol tests would establish schema/discovery/transport behavior. Only live model runs can provide evidence about natural-language routing. Nine passing tests cannot prove general correctness, safe authorization or unseen-request accuracy.

**Why fictional data?** It makes lookup outcomes repeatable without misrepresenting real occupancy or institutional information. This assignment permits an original toolkit and supplies no requirement for a public dataset. The catalogue is not a held-out evaluation dataset. A live booking product would need authoritative data and concurrency-aware reservation semantics.

**Most important limitation:** a saved study plan is a personal record, not a booking, reminder or calendar event. Do not use those terms interchangeably in the screencast.
