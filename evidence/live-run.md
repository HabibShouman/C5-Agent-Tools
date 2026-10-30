# Live model and MCP demonstration evidence

Date of evidence review: 31 October 2026. Source: terminal output supplied by Habib in the working conversation. The records were also independently inspected by the agent using the local read-only database inspection script. No credentials are included.

Provider: Gemini via the OpenAI-compatible endpoint, hosted by the OpenAI Agents SDK client application. The successful transcript followed instructions selecting `gemini-3.1-flash-lite`, but does not itself print MODEL_NAME. Confirm that variable in the screencast. Server metadata reported FastMCP 4.1.4.

| Demonstration | Observed MCP call | Observed result |
|---|---|---|
| Data | `lookup_space` with `space_id=quiet-1` | `is_error=false`; Cedar Quiet Room, quiet=true, seats=12. The assistant identified the fictional catalogue correctly. |
| Action | `save_study_session` with title MCP review, location Home, minutes 45, request_id live-action-1 | `is_error=false`; session_id=1, created=true. Assistant described a local record, not a reservation. |
| Orchestration | `plan_study_session` with space_id group-1, title Agent tools practice, minutes 60, request_id live-plan-1 | `is_error=false`; Olive Group Room; session_id=2, created=true; steps lookup_space then save_study_session. |
| Predictable failure | `lookup_space` with `space_id=missing-room` | `is_error=true`; SPACE_NOT_FOUND. The assistant reported failure and valid catalogue IDs without inventing a space. |

Independent read-only SQLite inspection confirmed exactly these records at the time of checking:

| session_id | request_id | title | location | minutes |
|---|---|---|---|---|
| 1 | live-action-1 | MCP review | Home | 45 |
| 2 | live-plan-1 | Agent tools practice | Olive Group Room | 60 |

The user also supplied Windows pytest output: 16 passed in 6.37 seconds. A pytest-asyncio configuration deprecation warning was present; it was not a failing check.

Earlier attempts with gemini-2.5-flash returned NotFoundError; attempts with gemini-3.8-flash returned HTTP 503 and a timeout. Successful later examples do not erase these provider failures or establish reliability beyond the demonstrated requests. No response-time or monetary-cost measurements were taken. A recorded 5–7-minute screencast and its accessible link remain required.
