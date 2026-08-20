# Step 1 — every tool the triage loop can currently see

Counted, not estimated: a real session opened anywhere in this monorepo (this one
included) has **12 built-in tools** always present, plus **245 more tools** offered by
attached MCP connectors and surfaced on demand -- **257 total**. These aren't
hypothetical; they're the exact roster this very session was handed at startup, tallied
with `wc -l` against the list the harness printed. Any triage loop living in this repo,
including one built for `harness-eng/the-tool-diet/`, inherits the same 257 by default,
because connector attachment is an account/environment setting, not a per-folder one
(confirmed the hard way in the Loop Engineering course: removing a connector from one
routine required an Edit -> remove -> Save pass through the UI, never a repo file).

## The 12 built-ins

`Agent`, `AskUserQuestion`, `Bash`, `Edit`, `Glob`, `Grep`, `Read`, `ReportFindings`,
`ScheduleWakeup`, `Skill`, `ToolSearch`, `Write`.

## The 245 connector tools, by group

| Connector | Tool count | What it's for |
| --- | --- | --- |
| `mcp__plugin_playwright_playwright__*` + `mcp__playwright__*` | 48 | Browser automation, twice over (two near-identical plugin registrations) |
| `mcp__claude_ai_Vercel__*` | 36 | Deploys, domains, billing, toolbar threads |
| `mcp__plugin_serena_serena__*` | 27 | Symbol-level code navigation/editing (LSP-backed) |
| `mcp__plugin_everything-claude-code_github__*` | 26 | Issues, PRs, repo search |
| `mcp__claude_ai_Gmail__*` | 22 | Read/send/label/trash email |
| `mcp__claude-in-chrome__*` | 22 | Drive a real Chrome tab |
| `mcp__claude_ai_Google_Drive__*` | 10 | Search, read, share, trash Drive files |
| `mcp__claude_ai_Zia_Tutor_AI__*` | 7 | A tutoring persona's own session/lesson tools |
| Standalone deferred tools (`WebFetch`, `WebSearch`, `NotebookEdit`, `Monitor`, `RemoteTrigger`, `LSP`, `EnterWorktree`/`ExitWorktree`, `CronCreate`/`CronDelete`/`CronList`, `SendMessage`, `TaskOutput`/`TaskStop`, `EndConversation`, `EnterPlanMode`/`ExitPlanMode`, `DesignSync`, `PushNotification`, `ListMcpResourcesTool`, `ReadMcpResource*`) | ~19 | One-off platform/session controls |
| `mcp__claude_ai_Agent_Factory_System_of_Record__*` | 3 | This course's own content lookup |
| `mcp__ide__*` | 2 | IDE diagnostics/code execution |
| `mcp__plugin_context7_context7__*` | 2 | Library docs lookup |
| `mcp__claude_ai_Cloudinary__*`, `mcp__claude_ai_Netlify__*`, `mcp__claude_ai_Hugging_Face__*`, `mcp__claude_ai_Google_Calendar__*` | 2 each (auth + complete_authentication) | OAuth handshakes for connectors not otherwise used here |
| `mcp__plugin_everything-claude-code_exa__*` | 2 | Web search/fetch, a second implementation |

## Step 2 — what the morning-brief skill actually needs

Read `.claude/skills/morning-brief/SKILL.md`: the entire job is one command,
`py .claude/skills/morning-brief/scripts/brief.py`, which itself only ever reads
`progress.md` and shells out to `git`. That is the whole dependency graph.

**Kept -- 2 tool categories, not 257:**

| Tool | Why |
| --- | --- |
| `Read` | So the loop (or a human debugging it) can open `progress.md` directly if needed. |
| `Bash`, narrowed to exactly `py .claude/skills/morning-brief/scripts/brief.py` | The one command the skill ever runs. |

Everything else -- all 245 connector tools, `Write`/`Edit`/`NotebookEdit`, `WebFetch`/
`WebSearch`, the GitHub connector, the browser tools, Gmail/Drive/Calendar, Vercel,
`Agent`, `AskUserQuestion`, the lot -- is either irrelevant to this one job or actively
answers a question the skill never asks. None of it is "might be handy someday" kept
on the list; per Concept 7, a tool a competent stranger couldn't say for certain the job
needs is a tool that shouldn't be on the list.

That's a cut from **257 -> 2 categories** (in practice, one Bash *pattern*, not even
the whole Bash surface). See `.claude/agents/triage-diet.md` and `.claude/settings.json`
for how that's enforced structurally, not just described.
