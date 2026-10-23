# C5 — Six-minute screencast guide

**Habib Shouman**

This is a recording guide, not a completed video or evidence of a successful live run. Rehearse after installing dependencies and passing the tests. Use an available tool-calling model, confirm quota, and hide API keys. Keep the editor and terminal text readable. Narrate in your own words; show actual responses, including failures.

Use a fresh database filename for each rehearsal/recording (for example `recording-01.db`), rather than reusing old IDs with changed payloads. Start `python host.py --db recording-01.db` with the configured provider. The environment's Python command should be the project's `.venv` interpreter.

| Time | Show | Suggested explanation |
|---|---|---|
| 0:00–0:40 | README and three-tool table | “I am Habib Shouman. This toolkit looks up campus study spaces and saves personal study-session records. It uses a fictional catalogue and does not reserve rooms. The tools are lookup_space, Data; save_study_session, Action; and plan_study_session, Orchestration.” |
| 0:40–1:20 | `host.py` and `server.py` | “The application is the MCP Host. The Agents SDK stdio adapter is its Client. It launches this separate FastMCP Server. The model sees discovered schemas and chooses a tool; I have not written keyword-based routing. The coordinator itself is a fixed workflow.” |
| 1:20–2:00 | First prompt and actual tool response | Enter: `Look up quiet-1 and tell me its name and whether it is quiet. Do not save anything.` Show discovery, the `HOST -> MCP` call, server log and return. Explain that this operation must not create a database row. |
| 2:00–2:50 | Action prompt and response | Enter: `Save a study session titled MCP review at Home for 45 minutes. Use request_id video-action-1.` Highlight the Action tool call, `created: true`, returned row ID and local-record-only effect. |
| 2:50–3:50 | Orchestration prompt and logs | Enter: `Look up group-1 and save a study session there titled Agent tools practice for 60 minutes. Use request_id video-plan-1.` Show one external orchestration call and server logs `STEP lookup_space` then `STEP save_study_session`. Explain reuse of the primitive service methods. |
| 3:50–4:40 | Failure and retry | Enter: `Look up missing-room.` Show `SPACE_NOT_FOUND`. Then enter: `Repeat the same MCP review save at Home for 45 minutes with request_id video-action-1.` Confirm `created: false` and the same row ID. If the model avoids a repeat call based on conversation memory, explicitly request a tool recheck with the same inputs; do not pretend a call occurred. |
| 4:40–5:15 | Exit and inspect storage | Enter `exit`, then run `python inspect_sessions.py --db recording-01.db`. There should be two rows, with catalogue-derived location “Olive Group Room” for the plan. This independently checks effects, rather than relying on the model's wording. |
| 5:15–6:00 | Tests, limitations and real links | Show the actual test result. Explain predictable errors, idempotency and the separation of tool correctness from model routing. Show the real GitHub repository and video submission location. State the actual provider/model used and any observed failures. |

Aim for 5–7 minutes in the finished recording, including real inference waiting time. If calls are slow, shorten narration; do not substitute fabricated output. A terminal or recording failure should be fixed before recording again. Upload the final recording to a platform of your choice and check its access in a signed-out browser if sharing by link.

## Live-run checklist

- [ ] Clean dependency install completed; `installed-versions.txt` saved.
- [ ] Core checks and pytest integration checks pass.
- [ ] All three model-selected tool calls visibly occur.
- [ ] Unknown-space failure visibly returns an error.
- [ ] Retry is observed, or the explanation accurately distinguishes model behavior from an actual retry call.
- [ ] Database inspection matches intended effects.
- [ ] Actual model ID, provider and date recorded in verification notes.
- [ ] Code and video links work for the instructor.
- [ ] Final duration is within 5–7 minutes.
