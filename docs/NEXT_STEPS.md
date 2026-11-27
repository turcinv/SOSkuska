# Next steps · 27 November 2026

[English](NEXT_STEPS.md) · [Čeština](cs/NEXT_STEPS.md) · [Slovenčina](sk/NEXT_STEPS.md) · [Русский](ru/NEXT_STEPS.md)

Current release: **v0.30.1**, schema **10**.

## Since 26 November 2026

- **v0.27.0:** study-studio Dashboard.
- **v0.28.0:** app logo.
- **v0.29.0:** cat brand redesign ([handoff](agents/design/cat-brand/README.md)).
- **v0.30.0:** AI drafting of flashcards and questions from notes ([guide](AI_NOTE_GENERATION.md)).
- **v0.30.1:** fixes from the first real-model evaluation ([record](agents/design/ai-note-generation/EVALUATION.md)). The fixes cover app-placed answers, prompt-injection hardening, a warning for drafts not found in the notes, and study-mode language.
- **Merged, not released:** the read-only MCP server [plan](agents/MCP_SERVER_PLAN.md) and its Phase 1, a headless read-only query layer (`soskuska/study_queries.py`, PR #76). There is no MCP server yet.
- The earlier bright UI Steps 1–5 are historical; the cat brand supersedes their visual direction.

## Recommended order

1. **Native visual acceptance of v0.29–v0.30.1.** The design and AI panels have only been checked in Linux/Xvfb captures.
   - On the Mac, and ideally a Windows PC at 100% and 150% scaling, use disposable data (`--data .local-data/acceptance.sqlite3`).
   - Check Light/Dark, four languages, 1440 × 900 and 1024 × 700, sidebar collapse, the Dashboard banner, and Generate with AI in a deck and a question bank.
   - Record OS/build, scaling and findings in the [Windows checklist](WINDOWS_ACCEPTANCE.md). Fix problems through reviewed PRs.
2. **Broader AI evaluation.** Re-run `tools/evaluate_ai.py` with at least one more model (for example `llama3.2:3b`) and with long notes and 20 items. Compare with the 26 November record. Tutor streaming/Stop/reconnect/history with a real model still needs a manual pass.
3. **Teacher demo and semester report.**
   - Script a short demo: create a subject, generate questions from notes, practise, review flashcards, open Statistics.
   - Refresh screenshots from disposable data.
   - Keep identity, course, language and deadline placeholders until supplied, and inspect final pagination.
4. **MCP Phase 2.** The stdio server with the optional pinned `mcp` dependency, tests, CI/container setup, a four-language user guide and a recorded run with a real MCP host. See the [plan](agents/MCP_SERVER_PLAN.md).
5. **Housekeeping.** Delete merged remote branches only on explicit request; keep `main` and release tags.

Before v1.0.0, resolve acceptance findings through reviewed PRs and rerun the relevant checks. New work, merge and publication need their own authorization. No manual result is marked passed by this status update.
