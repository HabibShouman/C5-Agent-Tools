# C5 — Reading and exploration

**Habib Shouman | EECE 503P/798S: Agentic Systems**

## Summary

The assigned Hugging Face article presents MCP as an open integration standard addressing the difficulty of connecting language models to information and operations outside their training data [1]. Its linked full article explains that reusable connectors can reduce bespoke integration work and complement agent frameworks and retrieval systems [2]. MCP does not itself supply reasoning, guarantee useful tool choices, or remove the need for authentication and monitoring. The article's enthusiasm should therefore be separated from evidence of application reliability.

In the architecture, the Host is the AI application coordinating model interaction and access to external capabilities. It creates a Client for each connected Server; that Client handles protocol communication, while the Server exposes capabilities [3]. Tools are executable operations, resources expose contextual data, and prompts provide reusable interaction templates. A host connects to an explicitly configured server and discovers its advertised capabilities; discovery does not imply unrestricted automatic access to every server on a network. In this project, the Python application is the Host, the Agents SDK's stdio adapter supplies the Client, and a separate FastMCP process is the Server.

I explored the reference Fetch MCP server's README and Python implementation [4,5]. Its fetch tool accepts a URL, an output-length bound, a starting offset, and a raw-content option. The function checks fetching policy, retrieves content, optionally simplifies HTML, and returns a bounded portion. Descriptions and argument constraints make the interface inspectable. Network failures and policy refusals produce explicit tool errors. These choices support predictable caller behavior, although remote content can change between requests.

Fetch remains cohesive: retrieval and conversion serve one objective, making a webpage usable as context. Nevertheless, the raw switch introduces two output modes, and repeated chunk requests may retrieve a changed page. I would prefer explicit output metadata identifying the representation, truncation, and retrieval time. Its implementation separates retrieval helpers from the public capability, avoiding a large multipurpose tool. This informed my own separation: one read-only lookup, one persistent write, and one deterministic coordinator. Narrow contracts simplify validation and testing, while the coordinator offers a higher-level operation without hiding which primitive effects occur. Protocol compatibility is valuable, but tool design and application-level verification remain necessary.

## References

Accessed 23 October 2026. Summary word count excludes heading, author line, and references.

1. Ksenia Se, [assigned Hugging Face MCP article](https://huggingface.co/blog/Kseniase/mcp), 17 March 2025.
2. Ksenia Se, [full article linked by the assigned page](https://www.turingpost.com/p/mcp).
3. Model Context Protocol, [Architecture overview](https://modelcontextprotocol.io/docs/learn/architecture). Used to clarify Host/Client/Server roles.
4. MCP reference servers, [Fetch README](https://github.com/modelcontextprotocol/servers/blob/main/src/fetch/README.md).
5. MCP reference servers, [Fetch implementation](https://github.com/modelcontextprotocol/servers/blob/main/src/fetch/src/mcp_server_fetch/server.py), main branch as inspected on the access date. Review was source-based; Fetch itself was not run.
