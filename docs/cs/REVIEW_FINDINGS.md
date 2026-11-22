# Nálezy revize hlavní větve Astra 6.2

[English](../REVIEW_FINDINGS.md) · [Čeština](REVIEW_FINDINGS.md) · [Slovenčina](../sk/REVIEW_FINDINGS.md) · [Русский](../ru/REVIEW_FINDINGS.md)

Záznam revize Astra 6.2 s nízkým úsilím pro v0.18.0, commit `252acc588700e46f0df5f76c9a31879104924fa2`. Soubor zůstane záznamem řešení; stav měň až po ověření opravy. Větev: `fix/main-review-findings`. Záznam nepovoluje sloučení ani vydání.

| ID | Priorita | Stav | Nález | Požadované chování |
| --- | --- | --- | --- | --- |
| A62-01 | P2 | Vydáno ve v0.18.1 | Starší formulář předmětu přepíše popis nebo termín změněný v jiném okně. | Porovnat původní obsah pod zápisovým zámkem a zachovat odmítnutý koncept. |
| A62-02 | P2 | Vydáno ve v0.18.1 | Staré potvrzení smazání odstraní otázku změněnou v jiném okně; témata používají stejný postup. | Atomicky porovnat zobrazený obsah; změna vyžaduje nové potvrzení. |
| A62-03 | P2 | Vydáno ve v0.18.1 | Návrat do banky otázek stejného předmětu ztratí rozepsanou otázku. | Zachovat editor, původní identitu a koncept při návratu ke stejnému předmětu. |
| A62-04 | P3 | Vydáno ve v0.18.1 | Oznámení selhání zálohy zůstává po úspěchu dnešní zálohy v jiném okně. | Načíst novější potvrzení úspěchu a odstranit jen překonané oznámení chyby. |

## Řešení a ověření

Všechny čtyři nálezy byly opravené ve větvi `fix/main-review-findings`, sloučené přes [PR #38](https://github.com/turcinv/SOSkuska/pull/38) a vydané ve [v0.18.1](https://github.com/turcinv/SOSkuska/releases/tag/v0.18.1). Soubor zůstává záznamem řešení a ověření.

Místní Docker/Xvfb: prošlo **306 testů** (dvě platformní přeskočení) a **18 GUI skriptů**. Nezávislá revize Sol se středním úsilím nenašla další blokující problémy. Ruční kontrola hardwaru zůstává samostatná.

- A62-01: `test_subject_draft_does_not_overwrite_concurrent_description_or_exam`; `check_state_fixes.py`.
- A62-02: `test_question_deletion_requires_reconfirmation_after_changed_answers`, `test_topic_rename_invalidates_delete_warning_without_removing_questions`, `test_disappearing_record_clears_old_confirmation_and_does_not_retry_delete`; `check_state_fixes.py`.
- A62-03: `check_state_fixes.py` — nové/upravené koncepty, opakování prvního čtení, přejmenování/smazání/obnovení tématu, výslovné zrušení a změna předmětu.
- A62-04: `test_real_external_worker_success_reconciles_failed_window`, `test_older_or_invalid_receipt_does_not_clear_unresolved_failure`; `check_scheduled_backups.py`.

[Jednotkové testy](../../tests/test_review_findings.py) · [Kontroly stavů GUI](../../soskuska/check_state_fixes.py) · [Kontroly GUI záloh](../../soskuska/check_scheduled_backups.py).
