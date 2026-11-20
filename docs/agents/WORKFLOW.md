# Development workflow

English instructions for development agents, referenced by [AGENTS.md](../../AGENTS.md). Read this file when its routing rule applies. Paths and commands in this file are relative to the repository root.

## Start here in a new session

1. Read this file, `README.md`, `docs/CURRENT_ARCHITECTURE.md`, and `docs/DEVELOPMENT.md` before changing the application. English is primary; Czech, Slovak and Russian translations are under `docs/cs/`, `docs/sk/` and `docs/ru/`.
2. Distinguish implemented behavior from proposals in `docs/PLANNED_ARCHITECTURE.md`. A roadmap is not an instruction to implement every feature.
3. Check the user's latest message for their current language and requested scope. Do not assume access to other chats or decisions not recorded in this workspace.
4. For users with a clean Windows machine, use `docs/WINDOWS_FIRST_RUN.md` or its Czech/Slovak/Russian equivalent. These guides cover installing Python, obtaining/extracting sources, creating a Windows-local environment, installing dependencies, and launching the app. Never assume a Mac virtual environment can be copied to Windows or that the user has access to a private repository.

5. Read `CONTRIBUTING.md` for contribution checks and `docs/GIT_GUIDE.md` (or its Czech/Slovak/Russian version) for cloning and repository workflow. Keep the language versions aligned.

## Conversation languages

- The user may write instructions, answers, corrections, and follow-up messages in **Czech, Slovak, English, or Russian**, and may switch languages between messages. Treat all four languages as supported conversation languages.
- Respond in the language of the user's **most recent message**, unless they explicitly request a different response language. Do not force English merely because this file or the source code is in English.
- Do not translate or restate the user's messages in English unless asked. Ask a concise clarification only when meaning is genuinely ambiguous.
- Conversation language, application UI language, and documentation language are independent. The default application UI is **English**; a saved interface language selects Czech, Slovak or Russian after restart. Do not change UI labels just because the user writes in another language.
- Keep this AGENTS.md in **English**. English is the primary documentation language: root README.md, CONTRIBUTING.md, CHANGELOG.md and guides in `docs/`. Keep Czech translations in `docs/cs/`, Slovak in `docs/sk/` and Russian in `docs/ru/`. Keep matching-page language links on all guides and all four versions aligned. Do not mix languages within localized documents; preserve code identifiers, commands, paths, and literal UI labels as needed.

## Verification and documentation

- The native smoke check opens a real window and requires a graphical session. It uses a temporary database and must not modify normal user data.
- Add focused checks for persistence, timer, and scrolling changes. Avoid tests that merely duplicate static style values.
- Report what was actually verified. Syntax checking is not UI testing; synthetic events are not a manual hardware test; macOS checks do not establish Windows/Linux compatibility.
- Update current architecture, developer instructions, and known limitations with material changes. Keep English, Czech, Slovak, and Russian versions aligned; do not silently update only one language. Current code is the source of truth for implemented behavior.
- Preserve offline operation without mandatory cloud services or paid APIs. Ollama is optional and connects only after an explicit Connect/Send.
- GitHub repository: `https://github.com/turcinv/SOSkuska`. Keep it private unless the user requests a visibility change. Use the code and checked Git state to report publication status.

## Branch and pull-request policy

- For implementation work, create a feature branch and open a pull request for review.
- Never commit or push directly to `main`. Merge through a pull request only after the user explicitly authorizes merging that PR and its review findings are resolved and validated. Passing tests alone is not merge authorization.
- Keep review fixes on the existing feature branch. Start a new feature branch for subsequent work after a PR is merged.

## Continuous integration

- `.github/workflows/ci.yml` runs for PRs targeting main, pushes to main and manual dispatch. Python 3.12 unit tests/syntax/dependency checks run on Linux, Windows and macOS; fourteen GUI checks run under Xvfb on Ubuntu.
- Keep action references pinned to verified release commit SHAs, contents permission read-only, and process/job timeouts. CI does not publish releases or deploy. Avoid duplicate feature-branch push and PR runs.
- CI results are automated coverage, not manual platform or hardware verification. Native Aqua Quit and Tk 9 trackpad behavior still require the Mac checks. Do not claim those are tested by the Linux GUI job.
- Read failed job logs, fix the cause and keep fixes on the same PR branch. Do not disable a meaningful failing check to obtain a green status. Branch protection is not configured by this workflow.


## Review and release workflow learned from this project

- For implementation features, run the relevant checks and request an independent Sol review at medium effort; apply findings on the same feature branch and re-review affected fixes. Use another reviewer/model only when requested. Documentation-only maintenance does not automatically need a subagent or GUI suite.
- Open a PR with concrete behavior, actual validation and remaining limitations. Attach it to the current chat when the app provides that tool. Inspect CI and fix meaningful failures on the same branch; do not weaken checks to get green results.
- The user authorizes merging and publishing separately from ordinary feature implementation. A request to merge and create a release authorizes the necessary release-label PR and publication steps. Never infer merge authorization just from green CI.
- A new feature normally increments the minor version while the project is 0.x; a fix-only release increments the patch. Check existing tags/releases before choosing the next number. Never invent historical release tags.
- Align `APP_VERSION` and the footer in `soskuska/app.py`, all four READMEs, changelog headings and architecture status. Preserve previous release entries. Make release-label changes through a branch/PR, then tag the exact merged commit and publish release notes for that tag. Do not publish a tag with stale footer/unreleased labels.
- For label/documentation-only release alignment, the user has preferred focused local checks without waiting for the entire hosted suite again; this does not waive failing checks or apply to feature changes.
- After publication verify the release URL, tag target, clean local main and synchronization with origin. Branch cleanup is a separate request; preserve unmerged work, main and release tags.
- Keep AGENTS.md concise. Put durable decisions in these topic files and dated lessons in `docs/SESSION_LESSONS.md`; do not copy the full chat or duplicate entire guides into the startup instructions.
