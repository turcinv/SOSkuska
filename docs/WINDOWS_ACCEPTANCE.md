# Windows acceptance checklist

[English](WINDOWS_ACCEPTANCE.md) · [Čeština](cs/WINDOWS_ACCEPTANCE.md) · [Slovenčina](sk/WINDOWS_ACCEPTANCE.md) · [Русский](ru/WINDOWS_ACCEPTANCE.md)

**Manual clean-machine status: NOT RUN.** Automated CI reports are separate evidence. Fill this record on a Windows x64 desktop without Python installed, using the exact checked portable artifact. Do not use real/private study data.

Record: Windows edition/build, CPU architecture, display resolution/scaling, artifact commit, SHA-256, date, tester and outcomes. Attach screenshots and reproduction details for failures. Mark each row PASS/FAIL and note the evidence; unchecked rows are not verified.

- [ ] Download, verify checksum, extract both ZIP layers and launch without Python/admin rights.
- [ ] Empty start: no sample subjects, scores or study time. Confirm the data path and restart persistence.
- [ ] Create/edit a Unicode subject, topic and four-option question; search/filter and restart.
- [ ] Import question/card CSVs, reject an invalid file, cancel preview, retry a failed write safely.
- [ ] Create/reveal/rate flashcards; confirm the schedule/history persists.
- [ ] Start a timed/untimed practice, save answers, close/reopen to resume, finish and inspect results. Browse more than 20 completed attempts and filter history.
- [ ] Run/pause/finish a focus session; verify saved real time and Statistics.
- [ ] Save/restart in English, Czech, Slovak and Russian; check long/Cyrillic labels, preserved content and independent AI answer language.
- [ ] At 1440×900 and 1024×700, check resizing, scrolling including nested text, keyboard navigation, dialogs and 100%/125%/150% scaling where supported.
- [ ] With Ollama absent/offline, study still works. If available, explicitly connect to a real local model, stream/Stop/reconnect and reopen saved chat; record model and hardware separately.
- [ ] Export/validate/restore a disposable backup, confirm the safety copy, close/reopen and verify data. Keep other instances closed for restore.
- [ ] Close from the title bar and taskbar; re-open. Move/update the app folder without losing user data. Exercise a second instance/locked data failure and verify a useful message.

Use [portable setup](WINDOWS_PORTABLE.md) for running/building, or [source first run](https://github.com/turcinv/SOSkuska/blob/main/docs/WINDOWS_FIRST_RUN.md) if testing the Python development route. The hosted CI report checks startup/helpers; it does not mark this manual list complete.
