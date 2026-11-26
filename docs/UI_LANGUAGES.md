# Interface language

[English](UI_LANGUAGES.md) · [Čeština](cs/UI_LANGUAGES.md) · [Slovenčina](sk/UI_LANGUAGES.md) · [Русский](ru/UI_LANGUAGES.md)

Choose **Settings → Interface language (applies after restart)**: English, Čeština, Slovenčina or Русский. Save settings, finish or save your current work, close SOSkúška normally and reopen it. The chosen language applies at startup. Saving does not rebuild screens, lose drafts or interrupt an active study/AI task. Language changes remain a draft until Save and do not synchronize to another open window.

Interface language and AI answer language are independent. For example, use a Czech interface while asking Ollama to answer in Russian. Interface Save never connects to Ollama. Existing installations default to English. The language belongs to the selected local database and is included in backups.

Navigation, forms, controls, status messages, confirmations, preview headings and domain choices have English/Czech/Slovak/Russian catalogs. Dropdowns show translated labels but retain canonical values for filtering, scoring, scheduling, models and database records. Native language names make the interface selector recognizable from any language. Unknown OS/server errors remain in their original text rather than being guessed or discarded. Native file-dialog system buttons follow the operating system's language; app-provided titles/file-type labels are translated.

Subject/topic/deck names, questions, answers, explanations, chat content, model identifiers, URLs, paths, CSV headers and stored ISO dates are not translated. The Dashboard uses a numeric date in non-English interfaces. No process-wide locale is changed. Translated buttons expand to fit their labels; the minimum window remains 1024 × 700 and lower content stays scrollable.

Schema **8** adds `preferences.ui_language` with an English default. Migration preserves existing content, chat history, answer language and preference revisions. Saving remains explicit, atomic and protected against stale edits. Restore accepts standalone schema 10 backups; keep older originals and convert a separate copy by opening it with the new app through `--data`, then export a current backup. See [Backup and restore](BACKUP_RESTORE.md).

Guides use English UI labels as the shared reference. The app uses the matching translated controls when another interface language is selected.
