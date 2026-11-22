# Nálezy revízie hlavnej vetvy Astra 6.2

[English](../REVIEW_FINDINGS.md) · [Čeština](../cs/REVIEW_FINDINGS.md) · [Slovenčina](REVIEW_FINDINGS.md) · [Русский](../ru/REVIEW_FINDINGS.md)

Záznam revízie Astra 6.2 s nízkym úsilím pre v0.18.0, commit `252acc588700e46f0df5f76c9a31879104924fa2`. Súbor zostane záznamom riešenia; stav meň až po overení opravy. Vetva: `fix/main-review-findings`. Záznam nepovoľuje zlúčenie ani vydanie.

| ID | Priorita | Stav | Nález | Požadované správanie |
| --- | --- | --- | --- | --- |
| A62-01 | P2 | Opravené vo vetve | Starší formulár predmetu prepíše popis alebo termín zmenený v inom okne. | Porovnať pôvodný obsah pod zápisovým zámkom a zachovať odmietnutý koncept. |
| A62-02 | P2 | Opravené vo vetve | Staré potvrdenie vymazania odstráni otázku zmenenú v inom okne; témy používajú rovnaký postup. | Atomicky porovnať zobrazený obsah; zmena vyžaduje nové potvrdenie. |
| A62-03 | P2 | Opravené vo vetve | Návrat do banky otázok rovnakého predmetu stratí rozpísanú otázku. | Zachovať editor, pôvodnú identitu a koncept pri návrate k rovnakému predmetu. |
| A62-04 | P3 | Opravené vo vetve | Oznámenie zlyhania zálohy zostáva po úspechu dnešnej zálohy v inom okne. | Načítať novšie potvrdenie úspechu a odstrániť len prekonané oznámenie chyby. |

## Riešenie a overenie

Všetky štyri nálezy sú opravené a overené vo vetve `fix/main-review-findings`; zostávajú nevydané do zlúčenia PR a schválenia vydania. Záznam po vyriešení zachovaj.

Miestny Docker/Xvfb: prešlo **306 testov** (dve platformové preskočenia) a **18 GUI skriptov**. Nezávislá revízia Sol so stredným úsilím nenašla ďalšie blokujúce problémy. Ručná kontrola hardvéru zostáva samostatná.

- A62-01: `test_subject_draft_does_not_overwrite_concurrent_description_or_exam`; `check_state_fixes.py`.
- A62-02: `test_question_deletion_requires_reconfirmation_after_changed_answers`, `test_topic_rename_invalidates_delete_warning_without_removing_questions`, `test_disappearing_record_clears_old_confirmation_and_does_not_retry_delete`; `check_state_fixes.py`.
- A62-03: `check_state_fixes.py` — nové/upravené koncepty, opakovanie prvého čítania, premenovanie/vymazanie/obnovenie témy, výslovné zrušenie a zmena predmetu.
- A62-04: `test_real_external_worker_success_reconciles_failed_window`, `test_older_or_invalid_receipt_does_not_clear_unresolved_failure`; `check_scheduled_backups.py`.

[Jednotkové testy](../../tests/test_review_findings.py) · [Kontroly stavov GUI](../../soskuska/check_state_fixes.py) · [Kontroly GUI záloh](../../soskuska/check_scheduled_backups.py).
