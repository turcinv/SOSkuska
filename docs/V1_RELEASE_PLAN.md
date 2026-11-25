# Acceptance steps before v1.0.0

[English](V1_RELEASE_PLAN.md) · [Čeština](cs/V1_RELEASE_PLAN.md) · [Slovenčina](sk/V1_RELEASE_PLAN.md) · [Русский](ru/V1_RELEASE_PLAN.md)

Decision recorded **23 November 2026**. Validate the published **v0.18.1**, schema **10**, before preparing v1.0.0. Core implementation is complete for the current semester scope; manual Windows and real-model evidence is still pending. This plan does not mark checks passed or authorize a merge/release. Pause new features while completing acceptance. The semester report and presentation can proceed separately and do not block the application release.

## 1 Obtain the Windows build

On a Windows x64 computer without Python, download `SOSkuska-windows-x64.zip` and its `.sha256` from [v0.18.1](https://github.com/turcinv/SOSkuska/releases/tag/v0.18.1). Private repository access is required. Verify the checksum and fully extract the ZIP into a writable folder. Keep `SOSkuska.exe`, `_internal` and `SOSkuska-worker.exe` together. Follow [portable setup](WINDOWS_PORTABLE.md); record any security-policy block without disabling protection.

## 2 Use disposable data

Open PowerShell in the extracted application folder and run:

```powershell
$acceptanceDb = Join-Path $env:TEMP ("SOSkuska-acceptance-" + [guid]::NewGuid().ToString() + ".sqlite3")
.\SOSkuska.exe --data "$acceptanceDb"
```

Record the value of `$acceptanceDb`. For every reopen in this test, rerun only the launch line with the **same path**; do not generate a new GUID. If PowerShell closes, restore the recorded path to the variable. Test backup/restore only against this disposable database and close other app instances before restore. Normal study data must remain untouched.

## 3 Complete Windows acceptance

Use the full [Windows checklist](WINDOWS_ACCEPTANCE.md), not just a startup smoke check. Verify an empty start; Unicode subjects/topics/questions; CSV preview/import; practice and saved results; flashcard ratings/history; focus pause/finish and saved time. Close/reopen with the same database and confirm persistence. For focus crash recovery, interrupt only the disposable test instance after a checkpoint, then confirm paused recovery without credit for closed time; also check discard. Check backup/restore and its safety copy, opt-in daily backups while open, language/appearance changes, scrolling, nested editors, 1440×900/1024×700 layouts and supported 100%/125%/150% scaling. Record unsupported combinations explicitly.

## 4 Check a real Ollama model

Ollama remains optional for normal study, but the Tutor needs real-model evidence before declaring this acceptance complete. Record server/model versions, model identifier, hardware, date and endpoint without credentials. Explicitly Connect and Send; verify streaming, Stop, reconnect and reopening saved conversations. Stop the server and confirm offline study still works. Note response-quality or performance limitations; fake-server CI is not real-model evidence. If a check cannot run, leave it NOT RUN with the reason rather than calling acceptance complete.

## 5 Record results

Copy this record per device/run and reference evidence for each checklist item. Use PASS / FAIL / NOT RUN; an empty field is not a pass. Keep screenshots free of personal study content and credentials.

| Field | Value |
| --- | --- |
| Date and tester | [DATE / TESTER] |
| Windows edition/build and CPU architecture | [WINDOWS / ARCHITECTURE] |
| Hardware, resolution and scaling | [HARDWARE / RESOLUTION / SCALING] |
| App version, artifact commit and ZIP SHA-256 | [VERSION / COMMIT / SHA-256] |
| Disposable database path | [PATH] |
| Checklist item, expected and actual behaviour | [ITEM / EXPECTED / ACTUAL] |
| Result and screenshot/log reference | NOT RUN — [EVIDENCE / REASON] |
| Ollama server/model versions and endpoint | [SERVER / MODEL / ENDPOINT] |
| Defect reproduction and fix PR | [STEPS / PR OR NONE] |

## 6 Resolve findings

Fix defects in a new branch and PR, retain their reproduction steps, obtain independent Sol review at medium effort and run relevant container checks and CI. Retest failed acceptance cases on the corrected Windows artifact; do not reuse an earlier pass for changed behaviour. Keep all unresolved or untested items visible. Merge only with explicit user approval.

## 7 Prepare v1.0.0

After acceptance passes and findings are resolved, prepare version/footer, four README release links, architecture status and changelog alignment through a PR. Inspect CI and obtain merge/release approval. Tag the exact merged commit, obtain its checked Windows ZIP/checksum/report from main CI and publish release notes with features, changes and known limitations. Verify the tag, asset checksum and download. Do not relabel the v0.18.1 binary as v1.0.0. No installer, macOS EXE support, automatic updater or bug-free guarantee is implied.
