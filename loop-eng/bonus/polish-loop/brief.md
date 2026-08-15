# The brief

Write a 30-second elevator pitch — about yourself, or a project you're building. Someone just
asked "so what do you do?" at a conference. You have one breath.

Save it as `pitch.md` in this folder, plain text, no heading needed — just the pitch itself.

Then run the critic:

```bash
python3 .claude/skills/polish-loop/scripts/critic.py
```

Read what fails. Rewrite. Run it again. Repeat until it says `5/5 passing`.

## What the critic actually checks

It never judges "is this a good pitch" — only five things a script can prove:

1. **Length** — 60 to 90 words. Long enough to say something, short enough to fit one breath.
2. **No buzzwords** — a short banned list (*synergy, leverage, disrupt, cutting-edge,
   world-class,* and friends). They fill space without saying anything.
3. **Opens with a hook** — not "Hi, my name is..." A greeting is not a hook.
4. **One concrete number or fact** — a real detail beats a vague claim every time.
5. **Ends with a clear ask** — a question, an invitation to connect, something the listener can
   actually do next. A pitch that just trails off wastes the moment it built.
