# AI improvements: question explanations

[English](AI_IMPROVEMENTS.md) · [Čeština](cs/AI_IMPROVEMENTS.md) · [Slovenčina](sk/AI_IMPROVEMENTS.md) · [Русский](ru/AI_IMPROVEMENTS.md)

Planning decision · 26 November 2026. Baseline: v0.24.0, schema 10. This document proposes future work; the feature is not implemented and this planning PR does not authorize implementation, merging or publication.

## Purpose

Connect completed Practice results to AI Tutor through **Explain this question**. The student previews one saved question and explicitly prepares a Tutor draft, then uses the existing Connect and Send controls. Ordinary study stays offline; Ollama remains optional.

## Implementation steps

### 1. Define the first feature and its boundaries

Support one question from a completed result, including a result reopened from history. Do not add it to running tests, setup, Question Bank or automatic completion. AI explains reasoning; it never changes the answer key, score, questions or statistics. A stored answer key is course data, not a guarantee of factual correctness. Keep modes, note generation, attachments and richer rendering out of this first PR.

### 2. Build a bounded, immutable explanation prompt

Use the saved practice snapshot identified by `(attempt_id, position)`, not `question_id` or the current Question Bank row. Recheck that the attempt exists and is completed; copy prompt, A–D choices, selected answer or Unanswered, correct answer and stored explanation. Add a short request to explain the reasoning and why the selected answer differs, or explain the correct approach if unanswered. A missing record/read failure gives a retry notice without replacing current UI state. Source edits/deletion must not change the prepared explanation.

### 3. Respect the existing input budget

The Tutor currently allows 4,000 characters per prompt; a valid question plus four choices and explanation can exceed that. Count the complete generated prompt, including labels/instructions. If it is too long, do not prepare or send it; show the measured length and the limit, keep the result usable and explain that the full-context shortcut cannot handle this item yet. Do not silently truncate choices/explanations or increase existing limits. Long-context attachments are later work. Test exactly-at-limit and over-limit input.

### 4. Add a local preview in completed results

Put Explain this question beside each completed result item, reachable with long text and compact layouts. Show the exact proposed prompt and what will be shared, with Prepare in Tutor and Cancel. Opening/closing the preview performs no HTTP, saves no conversation, changes no result and does not connect. Capture the original attempt/position in callbacks and guard against stale or hidden result actions. Revalidate eligibility when preparing the draft.

### 5. Hand off without clearing another conversation

Prepare only when Tutor is idle, has no unsaved reply or pending recovery/confirmation, and is a clean New chat with an empty prompt. If a chat/draft/request exists, keep it intact and explain how to finish or explicitly use the existing confirmed New chat action before retrying. Do not automatically clear, open another conversation, change endpoint/model, stop a job or queue a deferred send. After successful handoff, navigate to Tutor with the prepared draft visible; the student may edit it. A repeated action must not duplicate text or replace a changed draft.

### 6. Reuse the existing connection, Send and persistence paths

The endpoint/model and answer-language controls stay visible. Connect remains explicit when needed; only Send starts generation. Save the generated prompt through the normal pending-turn transaction before HTTP, so history retains the supplied snapshot as prompt text; no new context table or schema migration is planned. Keep Stop, partial replies, save retry, interrupted recovery, context bounds and endpoint/model ownership. Do not alter the network client or broaden what is automatically attached. If code inspection shows a schema change is necessary, revise this plan before implementing it.

### 7. Translate and make the flow usable

Add UI copy in English, Czech, Slovak and Russian; keep user question/answer text unchanged. Answer language remains independent of interface language. For Automatic, ask the model to follow the supplied question language and evaluate mixed-language cases; explicit language selection remains the reliable user control, and model detection quality is not guaranteed. Check keyboard order, readable preview/errors and action reachability at 1024×700 and 1440×900, Light/Dark/System and 100/150% startup scaling. Preserve result and Tutor scroll/drafts when another page is active.

### 8. Verify behavior and failures

Add focused pure tests for snapshot formatting, unanswered/wrong/correct answers, exact limits, invalid identity and missing/completed status. GUI checks must cover reopened history after source edit/deletion, preview Cancel, zero network activity before explicit Connect/Send, busy/dirty/unsaved Tutor rejection, idempotent handoff, initial question-save failure, streamed/Stop reply and terminal save retry without duplicate turns. Exercise real loopback FakeOllama for request content and persistence; it does not establish model answer quality. Use disposable databases and container GUI checks.

### 9. Review and deliver one focused feature PR

Start a fresh feature branch from current main, for example `feature/ai-question-explanation`. Implement the pure builder first, result preview second, guarded handoff third, then integration checks and documentation; keep these dependent commits in one reviewable PR. Run appropriate unit/container checks and inspect CI. Request independent Sol review at medium effort, fix findings on the same branch and re-review relevant changes. Update AI Tutor, Practice history, architecture and all four documentation languages. Keep version/release labels unchanged until publication is authorized.

### 10. Evaluate, then decide on follow-ups

Before calling the feature ready for the semester demo, run a small real-model evaluation using disposable correct, wrong, unanswered, ambiguous and multilingual questions. Record Ollama/model version, hardware, selected language, latency/Stop behavior and explanation usefulness. Distinguish this evidence from automated checks. The existing final platform acceptance and demo work remains outstanding. Merge and release require a separate user decision; a future feature release would normally be the next available 0.x minor, not a version reserved by this document.

## Likely code touchpoints

Likely touchpoints, to verify at implementation time: `soskuska/practice_page.py` (`render_result` and guarded actions); a new pure helper such as `soskuska/question_explanation.py`; `soskuska/app.py` (navigation handoff); `soskuska/tutor_page.py` (guarded draft preparation); existing Store read APIs in `soskuska/storage.py`; `soskuska/tutor.py` only if a bounded language instruction needs adjustment; four catalogs in `soskuska/i18n/`; focused unit/GUI checks and `tools/run_checks.py`. Avoid unrelated refactoring, Settings changes and migrations.

## Acceptance criteria

Done means: one completed snapshot is previewed locally, existing work is preserved, explicit Send produces an ordinary saved Tutor turn, failed/stopped paths remain recoverable, scores/history are unchanged, tests/review pass and docs accurately state limitations. Large questions rejected by the existing 4,000-character bound are a documented MVP limitation, not silently shortened content.

## Later AI improvements

After separate prioritization: (A) study modes—explain simply, hints, quiz me; (B) native answer formatting—lists, headings and code blocks; (C) question/flashcard generation from pasted notes, with structured validation, editable preview and explicit atomic Save. Generation needs its own plan for invalid output, duplicates, retries and content review. File retrieval/RAG, automatic database context and cloud fallback are not part of this plan.
