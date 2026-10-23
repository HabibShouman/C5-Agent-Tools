# Campus Study Toolkit — C5

**Habib Shouman | EECE 503P/798S: Agentic Systems**

A small MCP toolkit for reading a fictional campus space catalogue and saving personal study-session records. The catalogue is teaching data authored for this project, not AUB data. The SQLite writes are real local effects. No room is reserved and no calendar or notification service is contacted.

**Repository:** https://github.com/HabibShouman/C5-Agent-Tools

**Status:** application checks passed; dependency installation, MCP integration and live model routing remain unverified in the authoring environment. GitHub Actions supplies a connected integration-test environment; inspect its actual result. The required 5–7-minute video remains to be completed. See `VERIFICATION.md` before submission.

## Assignment requirements

- [x] Read the three-page C5 brief and assigned article, including its linked full version.
- [x] Explore an existing server: Fetch documentation and source.
- [x] Supply a 300–400-word summary in Markdown (`SUMMARY.md`).
- [x] Implement exactly one Data, one Action, and one Orchestration tool.
- [x] Provide descriptions, typed arguments/results and predictable failures.
- [x] Implement a FastMCP server and OpenAI Agents SDK host/client.
- [x] Supply tests, setup instructions and a two-paragraph reflection.
- [ ] Run the dependency-backed and live-model checks on a connected machine.
- [x] Publish code and add the real repository URL to `SUBMISSION_LINKS.md`.
- [ ] Record, upload and link the actual 5–7-minute screencast.

No separate rubric, lecture notes or starter code was supplied. There is no bonus task, required filename, UI requirement or mandated notebook/Colab format in the supplied brief. Filenames here are project conventions. Tool categories follow the definitions in C5; no additional course-specific definition is assumed.

## Part 1 — Reading and exploration

Submit `SUMMARY.md`. Sources distinguish the assigned Hugging Face introduction from the full article it links to and the official architecture documentation used to clarify roles. Fetch was inspected, not executed.

## Part 2 — Implementation

| MCP tool | Category | Input | Output | Predictable failures |
|---|---|---|---|---|
| `lookup_space` | Data | `space_id: str` | `Space` | `SPACE_NOT_FOUND` |
| `save_study_session` | Action | `title: str`, `location: str`, `minutes: int`, `request_id: str` | `SavedSession` | invalid input, `IDEMPOTENCY_CONFLICT`, `STORAGE_ERROR` |
| `plan_study_session` | Orchestration | `space_id: str`, `title: str`, `minutes: int`, `request_id: str` | `Plan` | lookup failure stops before write; inherits Action errors |

All three are callable capabilities registered with `@mcp.tool`. The Data tool performs a parameterized lookup. No optional pure-data MCP resources are exposed, so no `@mcp.resource` is necessary. The database inspection script is a developer utility, not a fourth MCP tool.

| Catalogue ID | Name | Quiet | Catalogue seat count |
|---|---|---|---|
| quiet-1 | Cedar Quiet Room | yes | 12 |
| group-1 | Olive Group Room | no | 6 |
| quiet-2 | Pine Reading Corner | yes | 4 |

Seat counts describe fictional spaces; they are not current free seats.

### Architecture and limits

`host.py` is the Host. Its `MCPServerStdio` adapter is the Client; the SDK launches `server.py` as a subprocess and discovers the three tools. `Agent` and `Runner` send the model tool descriptions, execute its selected calls over MCP, then return the tool results to the model. `VisibleServer` prints the actual client calls/results. Server lifecycle and orchestration-step logs go to stderr so stdout remains available for MCP messages.

This is one tool-using agent, not a multi-agent system. Its environment is the catalogue plus a local SQLite database. Observations are user messages and tool results; actions are the three calls. Conversation history supplies temporary memory; SQLite supplies persistent task records. The objective is to answer a lookup or save an explicitly requested study record accurately. The model chooses the tool and arguments; the coordinator's internal lookup-then-write sequence is a deterministic workflow, not an additional agent or an optimizing planner. Plain CLI commands would suffice for this small domain; the model adds a natural-language interface, and MCP supplies the assignment's interoperable boundary.

The agent cannot observe real occupancy, operating hours or calendar conflicts, and must not infer them. `minutes` is a duration, not a scheduled timestamp. The server validates schema constraints, whitespace-only input and duplicate-ID conflicts. Repeated writes use a client-supplied idempotency key and compare normalized payloads. The SQLite unique constraint and transaction protect concurrent retries. This is not a universal exactly-once guarantee: changing the key can create another record, and a timeout can occur after commit. Reuse the same key to reconcile a retry. No automatic write retries are implemented.

An unknown space fails before saving; an Action storage failure is returned as a tool error. The orchestration uses the same service methods as the primitive tools, not duplicated operations or a nested MCP connection. The catalogue is fixed, so lookup/write consistency does not require a distributed transaction. A live catalogue would require a fresh design for changing data.

Tools run locally without HTTP service credentials. The optional model backend requires internet unless a local compatible model is configured. The server is a trusted, single-user teaching process, not a multi-tenant security boundary. User intent is enforced by the host prompt, not a formal authorization proof. The agent does not accept arbitrary SQL or file paths as tool arguments; `STUDY_DB` is trusted host configuration. Trace export is disabled. Terminal tool logs can contain user-entered session information; use non-sensitive examples when recording.

Each run has a six-turn cap, a 120-second outer deadline, a 15-second MCP request timeout, and a five-second SQLite lock timeout. Provider calls use a 45-second timeout with retries disabled. Conversation history resets after 40 items at a completed run boundary. These limits bound waiting and context growth, but do not prove model reliability or cancel an already committed write. The orchestration saves one external MCP round trip compared with two separate primitive calls. No latency, cost or quality superiority is claimed; model latency and token costs have not been measured.

### Setup — Windows PowerShell

Use Python 3.11 or newer. From this directory:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install --upgrade -r requirements.txt
.\.venv\Scripts\python.exe -m pip freeze > installed-versions.txt
.\.venv\Scripts\python.exe check_core.py
.\.venv\Scripts\python.exe -m pytest -q
```

If `py -3.11` is unavailable, use the full path to an installed Python 3.11+ interpreter. No activation is needed. On macOS/Linux, use `python3 -m venv .venv` and `.venv/bin/python` for subsequent commands. The same interpreter launches the server.

The brief requests the latest FastMCP and Agents SDK. `--upgrade` resolves the latest mutually compatible published releases at installation time; they could not be resolved here. Save `installed-versions.txt` from the successful run and commit it for repeatability. It can then be used as a lock-style input (`pip install -r installed-versions.txt`) on the same platform/Python. This project does not present an unexecuted dependency list as a verified lockfile. `uv sync` is an alternative using `pyproject.toml`; preserve its generated lockfile if used.

### Select a model provider

OpenAI Agents SDK is used regardless of model provider. No keys are bundled or read from old projects. This program reads process environment variables, not `.env` files. Use one configuration below and select an available tool-calling model in your account.

Gemini, using Google's documented OpenAI-compatible endpoint:

```powershell
$env:MODEL_PROVIDER = 'gemini'
$env:GEMINI_API_KEY = [System.Net.NetworkCredential]::new('', (Read-Host 'Gemini API key' -AsSecureString)).Password
$env:MODEL_NAME = Read-Host 'Available Gemini tool-calling model ID'
.\.venv\Scripts\python.exe host.py --db demo-study.db
```

This path avoids requiring an OpenAI API key. Provider quotas and account eligibility still apply; no free quota is promised. Gemini compatibility has not been live-tested for this project.

OpenAI:

```powershell
$env:MODEL_PROVIDER = 'openai'
$env:OPENAI_API_KEY = [System.Net.NetworkCredential]::new('', (Read-Host 'OpenAI API key' -AsSecureString)).Password
$env:MODEL_NAME = Read-Host 'Available OpenAI tool-calling model ID'
.\.venv\Scripts\python.exe host.py --db demo-study.db
```

For a tool-calling OpenAI-compatible local service, set `MODEL_PROVIDER=compatible`, `MODEL_BASE_URL` to its API base URL, `MODEL_NAME` to its installed model ID, and `MODEL_API_KEY` if required. Local compatibility is an unverified option, not a substitute for testing. The backend must support Chat Completions tools; servers rejecting `parallel_tool_calls` may require adaptation.

The CLI supports conversation and `exit`. For a single request:

```powershell
.\.venv\Scripts\python.exe host.py --db demo-study.db --prompt 'Look up quiet-1. Do not save anything.'
```

Do not launch `server.py` separately for this mode; the host starts and stops it. Running it alone waits for protocol messages and is not a chat interface.

### Tests and independent evidence

- `check_core.py`: nine unittest checks requiring only Python and Pydantic. Executed locally; covers persistence, boundaries, failure behavior, ordering and concurrent retries.
- `tests/test_core.py`: pytest checks of application behavior, including invalid inputs and persistence. Supplied, not executed here.
- `tests/test_mcp.py`: real subprocess/stdio discovery, schemas, all three tool round trips and failure cases using the Agents SDK client. Supplied, not executed here. No model key needed.
- `inspect_sessions.py --db demo-study.db`: reads SQLite independently of tool outputs. Use after exiting the agent to confirm actual effects.
- `.github/workflows/tests.yml`: runs both test layers on a push or manually after publication. Workflow execution has not occurred here.

These development cases are not held-out model evaluation. No expected answer is inserted into the agent or sent to the model as an answer key.

## Part 3 — Demonstration

Follow `DEMO_GUIDE.md` for a six-minute recording with real user prompts, visible calls/results and independent effect inspection. A scripted transport test does not satisfy the live agent screencast requirement. Add actual accessible links to `SUBMISSION_LINKS.md`; placeholders are not valid deliverables.

## Submission contents

Submit the source repository, `SUMMARY.md`, `REFLECTION.md`, and the video link as requested by the instructor. `COVERAGE.md` maps the brief to evidence; `DEFENSE_NOTES.md` explains the design. `VERIFICATION.md` records exactly which checks were executed. No notebook or report PDF is required because Markdown is explicitly permitted.

The published repository is https://github.com/HabibShouman/C5-Agent-Tools. To obtain its current contents:

```powershell
git clone https://github.com/HabibShouman/C5-Agent-Tools.git
cd C5-Agent-Tools
```

The repository contains both test modules and `.github/workflows/tests.yml`. Keep credentials, virtual environments and private session databases excluded from future commits.

## API references

Official documentation consulted 23 October 2026:

- [FastMCP tool declarations, structured outputs, annotations and errors](https://gofastmcp.com/servers/tools)
- [OpenAI Agents SDK MCP stdio integration](https://openai.github.io/openai-agents-python/mcp/)
- [Google Gemini OpenAI compatibility and function calling](https://ai.google.dev/gemini-api/docs/openai)
- [MCP architecture](https://modelcontextprotocol.io/docs/learn/architecture)

This implementation used generative AI assistance for drafting, coding and review. Habib should understand the work and follow any course AI-use policy; none was supplied with C5.
