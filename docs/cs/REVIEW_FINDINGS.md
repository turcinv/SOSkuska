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


## Úplná revize main · 26. listopadu 2026 · Astra 6.2 medium

`main` · v0.26.0 · `db38e08802058480bbed250c16eeffc23bad143b`

| ID | Priorita | Stav | Nález | Reprodukce / místo | Požadované chování |
| --- | --- | --- | --- | --- | --- |
| A62-05 | P2 | Vydáno ve v0.26.1 | Starší editor balíčku při uložení názvu vrátí původní popis, přestože jiné okno uložilo nový. | `flashcard_page.py:291`, `storage.py:713`. Otevřít úpravu balíčku, jinde uložit nový popis, v původním formuláři změnit jen název a uložit: oba zápisy uspějí a nový popis se ztratí. | Pod zápisovým zámkem porovnat původní upravovaný snímek a zachovat odmítnutý koncept. |
| A62-06 | P2 | Vydáno ve v0.26.1 | Starší formulář přejmenování tématu přepíše novější název z jiného okna. | `question_bank.py:284`, `storage.py:402`. Otevřít přejmenování, jinde téma přejmenovat a poté uložit původní formulář: bez upozornění přepíše aktuální název. | Atomicky porovnat původní identitu a název tématu; zachovat odmítnutý koncept. |
| A62-07 | P3 | Vydáno ve v0.26.1 | Obnovená kartička s přijatým časem mimo UTC může chybět ve frontě a odmítat hodnocení, i když už je splatná. | `storage.py:687,811,823`, `flashcard_page.py:388`. Čas před pěti minutami uložit s `+10:00`, zálohovat, ověřit, obnovit a otevřít: fronta je prázdná a hodnocení tvrdí, že kartička ještě není splatná. | Ve všech počtech, frontách a kontrolách hodnotit skutečné časové okamžiky. |
| A62-08 | P3 | Vydáno ve v0.26.1 | Statistiky vynechají obnovený dokončený test s přijatým posunem UTC obsahujícím sekundy. | `study_statistics.py:42,45`, `backup_validation.py:28`. Po obnově času s `+03:00:07` historie počítá 1 a Statistiky za celé období 0; SQLite vrací NULL. | Sjednotit čtení časů statistik s povoleným formátem záloh a historie pro testy i opakování. |
| A62-09 | P3 | Vydáno ve v0.26.1 | Návody historie Tutora a jazyků stále uvádějí obnovu schématu 9. | `docs/TUTOR_HISTORY.md:31`, `docs/UI_LANGUAGES.md:13` a překlady; `backup.py:102` vyžaduje schéma 10. | Opravit aktuální požadavky obnovy ve čtyřech jazycích; zachovat historický popis migrací. |

CI přesného commitu prošlo všemi pěti úlohami: 322 jednotkových testů na každé platformě a všech 23 kontrol rozhraní v Linuxu. Cílené kontroly na dočasných datech reprodukovaly oba formuláře skutečnými tlačítky Uložit v Docker/Xvfb a oba časové případy přes ověření zálohy, obnovu a opětovné otevření; hlavní agent je nezávisle zopakoval. Časové nálezy vyžadují povolené formáty odlišné od běžného zápisu UTC aplikace. Širší revize pokryla běh, úložiště/migrace, studium, Tutor/režimy, předvolby, přenosy, CI/balení Windows a dokumentaci. Jde o nálezy, nikoli opravy; aplikační kód se nezměnil. Test skutečného modelu zůstává odložený a ruční přejímka hardwaru/platformy neproběhla.


## Řešení na opravné větvi

A62-05 a A62-06 porovnávají původní upravované snímky pod BEGIN IMMEDIATE. Konflikt zachová koncept, načtení je výslovné. Potvrzené uložení balíčku spotřebuje zápis před obnovením zobrazení, zablokuje uložený formulář a nabídne Obnovit balíček pouze pro čtení, i po změně v jiném okně. A62-07 používá přesné celé mikrosekundy UTC pro počty a pořadí a časové okamžiky pro hodnocení/opakování. A62-08 sdílí místní den s historií a zachová všechny čtecí dotazy v jedné transakci, bez přepsání časů nebo změny schématu 10. Krajní povolená data zůstávají dostupná a při nemožném místním převodu mají omezený náhradní výpis. A62-09 opravuje aktuální požadavky obnovy ve všech osmi návodech.

Cílené ověření: osm případů v `tests/test_astra026_fixes.py` (také ve třech časových pásmech), stávající regresní testy Statistik a `check_astra026_fixes.py` v Docker/Xvfb ve čtyřech jazycích při počátečním měřítku 100/150 %. Kontroly pokrývají zachování cizích změn i konceptů, výslovné načtení, chybu obnovení po zápisu, nezměněné obnovené řádky, pořadí a posuny se sekundami. Úplné a hostované výsledky jsou v opravném PR. Tento záznam nepovoluje sloučení ani vydání; skutečný model a ruční testy hardwaru/platformy zůstávají odložené.


## Záznam vydání · v0.26.1

A62-05–A62-09 byly sloučeny přes PR #62 a vydány ve v0.26.1. Nezávislá revize Sol medium prošla; uspělo 330 jednotkových testů (dvě platformní výjimky Linuxu), všech 24 kontejnerových kontrol rozhraní a všech pět CI úloh opravy. Původní kontrolovaný commit i důkazy výše zůstávají historické. Skutečný model a ruční přejímka platforem zůstávají odložené.

## Revize repozitáře · 27. listopadu 2026 · Sol (backend codex)

Revize `main` jen pro čtení na `b1591d7` (v0.31.1) vyžádaná od jiné rodiny modelů. Běžela na backendu `codex` v Kiro Crew, ale potvrzení spuštění uvádělo `claude-sonnet-5.5`, takže rodina modelu není potvrzena. Zpráva byla useknuta po zjištění 7. Každé zjištění níže bylo ověřeno čtením kódu; vlastní reprodukce recenzenta se dvěma Store nebyly znovu spuštěny. Stav se mění až po ověřené opravě.

| ID | Priorita | Stav | Zjištění | Požadované chování |
| --- | --- | --- | --- | --- |
| S27-01 | P2 | Opraveno, nevydáno | Otevřený panel AI generování po změně Nastavení dál ukazuje starý server/model; Generovat obnoví popisek a odešle poznámky v témže kliknutí. | Při změně nastavení AI otevřené panely obnovit; pokud se cíl liší od zobrazeného, vyžadovat další kliknutí. |
| S27-02 | P2 | Opraveno, nevydáno | Zahození (a dokončení) testu ignoruje odpovědi, které jiné okno uložilo po otevření potvrzení. | Porovnat revizi odpovědí pod `BEGIN IMMEDIATE`; při konfliktu test ponechat a zeptat se znovu. |
| S27-03 | P2 | Opraveno, nevydáno | Potvrzení smazání předmětu a balíčku porovnávají jen názvy a počty; nahrazení kartičky počet nezmění a staré potvrzení smaže náhradu. | U obou kaskád potvrzovat podle identit/revizí podřízených záznamů (nebo revize obsahu). |
| S27-04 | P3 | Opraveno, nevydáno | Uložení kartičky se zapíše před obnovením balíčku; když obnovení selže, Uložit zůstane aktivní a druhé kliknutí kartičku znovu upraví a znovu vynuluje plán. | Použít vzor opakování jen čtení po zápisu. |
| S27-05 | P3 | Opraveno, nevydáno | MCP zkracuje možnosti odpovědí na 300 znaků, ačkoli zadávání povoluje 500, takže různé možnosti mohou vypadat stejně. | Vracet celé možnosti v rámci rozpočtu odpovědi; zvážit vyhledání otázky podle ID. |
| S27-06 | P3 | Opraveno, nevydáno | Parser poznámek stále přijímá starší písmeno odpovědi zvolené modelem a potichu zkracuje příliš dlouhá témata. | Vyžadovat aktuální tvar; příliš dlouhá témata hlásit jako chyby validace. |
| S27-07 | P3 | Opraveno, nevydáno | Když se pracovní vlákno generování nespustí, panel zůstane zaneprázdněný a blokuje změny nastavení AI i obnovu. | Zachytit selhání spuštění, vyčistit úlohu a zobrazit chybu. |

### Řešení · větev `fix/review-s27`

Všech sedm bylo opraveno s regresním pokrytím: `tests/test_review_s27.py` (S27-02, S27-03, S27-05), `tests/test_note_generation.py` (S27-06), `tests/test_mcp_server.py` (přesné vyhledání) a GUI kontroly v `check_note_generation.py` (S27-01, S27-07), `check_flashcards.py` (S27-04) a `check_practice.py` (S27-02 v UI). Vrácení každé opravy způsobilo selhání jejího testu (11 z 11 mutantů zachyceno). Linuxový kontejner: 393 jednotkových testů (dvě přeskočené kvůli platformě) a všech 26 GUI skriptů prošlo.

Opakovaná revize `8fbaea9` na backendu codex: S27-01 a S27-04 až S27-07 ověřeny. Dvě navazující věci byly opraveny: když po konfliktu v testu selže opětovné načtení, stránka nechá ovládání zamčené a ukáže chybu načtení místo tvrzení, že jsou zobrazeny aktuální odpovědi; vyhledání podle ID vrací `version` (s klíčem pro každý proces serveru, takže ji nelze použít ke zkoušení možných odpovědí), kterou Quiz me před hodnocením porovná. Dva návrhy byly záměrně odmítnuty: odpověď změněná A → B → A nebo kartička upravená a vrácená zpět stále odpovídá potvrzení, protože potvrzení porovnávají obsah, který uživatel viděl, ne historii úprav. Smaže se přesně to, co bylo zobrazeno, a čítač revizí by vyžadoval změnu schématu.
