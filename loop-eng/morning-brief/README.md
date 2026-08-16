# The Morning Brief with a Memory

**Loop Engineering — unattended schedules (runs while you sleep) + the spine (memory
between runs).**

Once a run, this writes a short brief of what changed in the repo since the **last**
run — new commits, and how many TODO/FIXME comments exist right now. How does it know
what's already been reported? It writes into `progress.md` and reads that file first
next time. That file is the **spine** — the loop's memory.

## Run it

```bash
cd loop-eng/morning-brief
claude
```

Say **yes** when Claude asks whether you trust this folder. Then ask:

```
give me this morning's brief
```

First run — nothing to compare against yet, so it sets a baseline:

```
  🌅  MORNING BRIEF  ·  2026-08-17 08:00 UTC
      first run — establishing a baseline, nothing to compare against yet
  ------------------------------------------------------------
   open TODO/FIXME comments right now: 3
  ------------------------------------------------------------
   saved this to progress.md, so tomorrow's run remembers it.
```

## Now feel the spine — this is the whole lesson

Do some real work in the repo — commit something — then **ask again:**

```
give me this morning's brief
```

This time it reports **only the commits that landed since the first run** — not the
whole repo history again:

```
  🌅  MORNING BRIEF  ·  2026-08-17 08:14 UTC
      1 new commit(s) since last run
  ------------------------------------------------------------
   • a1b2c3d Fix the thing
   open TODO/FIXME comments right now: 3
  ------------------------------------------------------------
   saved this to progress.md, so tomorrow's run remembers it.
```

See for yourself: `cat progress.md` — both entries are there, but the second one lists
only what's new. **Now delete the memory and ask one more time:**

```
rm progress.md
give me this morning's brief
```

It's a "first run" again — the whole history looks new. **No spine, no loop** — that
one file is what turns separate runs into an ongoing brief instead of the same report
twice.

## How it fits the loop

**Spine** → `progress.md`: read first, written last. It holds the commit bookmark and
every prior entry — this is what lets each run report only what's *new*.

**Heartbeat** → a daily schedule, because "once a morning" is a rhythm, not something
you sit and watch for:

```
/schedule every morning at 8am, run the morning-brief skill and show me the summary
```

**Not `/loop`** — an in-session timer dies when you close the terminal, and a morning
brief needs to run while you're asleep. **Not `/goal`** — a brief never "finishes,"
it just reports and waits for tomorrow. A daily schedule is the only heartbeat that
fits.

**Compared to the [ISS project](../iss-loop/):** that one repeats on a timer with no
memory at all — every tick reports the same kind of thing fresh. This one *needs* the
spine, because "what's new" is meaningless without remembering what was already shown.

## What it ships

| File | Job |
| --- | --- |
| `.claude/skills/morning-brief/scripts/brief.py` | Owns the spine: reads `progress.md`, gathers commits + TODOs, writes `progress.md`. |
| `.claude/settings.json` | Pre-granted rule so the loop never stops to ask permission each run. |
| `AGENTS.md` / `CLAUDE.md` | Point any agent at the skill/script. |

`progress.md` itself isn't shipped — it's created by the first run, same as
[paper-watch](../paper-watch/)'s spine.
