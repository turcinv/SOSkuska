# Nálezy revízie hlavnej vetvy Astra 6.2

[English](../REVIEW_FINDINGS.md) · [Čeština](../cs/REVIEW_FINDINGS.md) · [Slovenčina](REVIEW_FINDINGS.md) · [Русский](../ru/REVIEW_FINDINGS.md)

Záznam revízie Astra 6.2 s nízkym úsilím pre v0.18.0, commit `252acc588700e46f0df5f76c9a31879104924fa2`. Súbor zostane záznamom riešenia; stav meň až po overení opravy. Vetva: `fix/main-review-findings`. Záznam nepovoľuje zlúčenie ani vydanie.

| ID | Priorita | Stav | Nález | Požadované správanie |
| --- | --- | --- | --- | --- |
| A62-01 | P2 | Vydané vo v0.18.1 | Starší formulár predmetu prepíše popis alebo termín zmenený v inom okne. | Porovnať pôvodný obsah pod zápisovým zámkom a zachovať odmietnutý koncept. |
| A62-02 | P2 | Vydané vo v0.18.1 | Staré potvrdenie vymazania odstráni otázku zmenenú v inom okne; témy používajú rovnaký postup. | Atomicky porovnať zobrazený obsah; zmena vyžaduje nové potvrdenie. |
| A62-03 | P2 | Vydané vo v0.18.1 | Návrat do banky otázok rovnakého predmetu stratí rozpísanú otázku. | Zachovať editor, pôvodnú identitu a koncept pri návrate k rovnakému predmetu. |
| A62-04 | P3 | Vydané vo v0.18.1 | Oznámenie zlyhania zálohy zostáva po úspechu dnešnej zálohy v inom okne. | Načítať novšie potvrdenie úspechu a odstrániť len prekonané oznámenie chyby. |

## Riešenie a overenie

Všetky štyri nálezy boli opravené vo vetve `fix/main-review-findings`, zlúčené cez [PR #38](https://github.com/turcinv/SOSkuska/pull/38) a vydané vo [v0.18.1](https://github.com/turcinv/SOSkuska/releases/tag/v0.18.1). Súbor zostáva záznamom riešenia a overenia.

Miestny Docker/Xvfb: prešlo **306 testov** (dve platformové preskočenia) a **18 GUI skriptov**. Nezávislá revízia Sol so stredným úsilím nenašla ďalšie blokujúce problémy. Ručná kontrola hardvéru zostáva samostatná.

- A62-01: `test_subject_draft_does_not_overwrite_concurrent_description_or_exam`; `check_state_fixes.py`.
- A62-02: `test_question_deletion_requires_reconfirmation_after_changed_answers`, `test_topic_rename_invalidates_delete_warning_without_removing_questions`, `test_disappearing_record_clears_old_confirmation_and_does_not_retry_delete`; `check_state_fixes.py`.
- A62-03: `check_state_fixes.py` — nové/upravené koncepty, opakovanie prvého čítania, premenovanie/vymazanie/obnovenie témy, výslovné zrušenie a zmena predmetu.
- A62-04: `test_real_external_worker_success_reconciles_failed_window`, `test_older_or_invalid_receipt_does_not_clear_unresolved_failure`; `check_scheduled_backups.py`.

[Jednotkové testy](../../tests/test_review_findings.py) · [Kontroly stavov GUI](../../soskuska/check_state_fixes.py) · [Kontroly GUI záloh](../../soskuska/check_scheduled_backups.py).


## Úplná revízia main · 26. novembra 2026 · Astra 6.2 medium

`main` · v0.26.0 · `db38e08802058480bbed250c16eeffc23bad143b`

| ID | Priorita | Stav | Nález | Reprodukcia / miesto | Požadované správanie |
| --- | --- | --- | --- | --- | --- |
| A62-05 | P2 | Vydané vo v0.26.1 | Starší editor balíčka pri uložení názvu vráti pôvodný popis, hoci iné okno uložilo nový. | `flashcard_page.py:291`, `storage.py:713`. Otvoriť úpravu balíčka, inde uložiť nový popis, v pôvodnom formulári zmeniť iba názov a uložiť: oba zápisy uspejú a nový popis sa stratí. | Pod zápisovým zámkom porovnať pôvodnú upravovanú snímku a zachovať odmietnutý návrh. |
| A62-06 | P2 | Vydané vo v0.26.1 | Starší formulár premenovania témy prepíše novší názov z iného okna. | `question_bank.py:284`, `storage.py:402`. Otvoriť premenovanie, inde tému premenovať a potom uložiť pôvodný formulár: bez upozornenia prepíše aktuálny názov. | Atomicky porovnať pôvodnú identitu a názov témy; zachovať odmietnutý návrh. |
| A62-07 | P3 | Vydané vo v0.26.1 | Obnovená kartička s prijatým časom mimo UTC môže chýbať vo fronte a odmietať hodnotenie, hoci už je splatná. | `storage.py:687,811,823`, `flashcard_page.py:388`. Čas pred piatimi minútami uložiť s `+10:00`, zálohovať, overiť, obnoviť a otvoriť: front je prázdny a hodnotenie tvrdí, že kartička ešte nie je splatná. | Vo všetkých počtoch, frontoch a kontrolách porovnávať skutočné časové okamihy. |
| A62-08 | P3 | Vydané vo v0.26.1 | Štatistiky vynechajú obnovený dokončený test s prijatým posunom UTC obsahujúcim sekundy. | `study_statistics.py:42,45`, `backup_validation.py:28`. Po obnove času s `+03:00:07` história počíta 1 a Štatistiky za celé obdobie 0; SQLite vracia NULL. | Zjednotiť čítanie časov štatistík s povoleným formátom záloh a histórie pre testy aj opakovania. |
| A62-09 | P3 | Vydané vo v0.26.1 | Návody histórie Tutora a jazykov stále uvádzajú obnovu schémy 9. | `docs/TUTOR_HISTORY.md:31`, `docs/UI_LANGUAGES.md:13` a preklady; `backup.py:102` vyžaduje schému 10. | Opraviť aktuálne požiadavky obnovy v štyroch jazykoch; zachovať historický popis migrácií. |

CI presného commitu prešlo všetkými piatimi úlohami: 322 jednotkových testov na každej platforme a všetkých 23 kontrol rozhrania v Linuxe. Cielené kontroly na dočasných dátach reprodukovali oba formuláre skutočnými tlačidlami Uložiť v Docker/Xvfb a oba časové prípady cez overenie zálohy, obnovu a opätovné otvorenie; hlavný agent ich nezávisle zopakoval. Časové nálezy vyžadujú povolené formáty odlišné od bežného zápisu UTC aplikácie. Širšia revízia pokryla beh, úložisko/migrácie, štúdium, Tutor/režimy, predvoľby, prenosy, CI/balenie Windows a dokumentáciu. Ide o nálezy, nie opravy; aplikačný kód sa nezmenil. Test skutočného modelu zostáva odložený a ručná akceptácia hardvéru/platformy neprebehla.


## Riešenie na opravnej vetve

A62-05 a A62-06 porovnávajú pôvodné upravované snímky pod BEGIN IMMEDIATE. Konflikt zachová návrh, načítanie je výslovné. Potvrdené uloženie balíčka spotrebuje zápis pred obnovením zobrazenia, zablokuje uložený formulár a ponúkne Obnoviť balíček iba na čítanie, aj po zmene v inom okne. A62-07 používa presné celé mikrosekundy UTC pre počty a poradie a časové okamihy pre hodnotenie/opakovanie. A62-08 zdieľa miestny deň s históriou a zachová všetky čítacie dotazy v jednej transakcii bez prepísania časov alebo zmeny schémy 10. Krajné povolené dátumy zostávajú dostupné a pri nemožnom miestnom prevode majú obmedzený náhradný výpis. A62-09 opravuje aktuálne požiadavky obnovy vo všetkých ôsmich návodoch.

Cielené overenie: osem prípadov v `tests/test_astra026_fixes.py` (aj v troch časových pásmach), existujúce regresné testy Štatistík a `check_astra026_fixes.py` v Docker/Xvfb v štyroch jazykoch pri počiatočnej mierke 100/150 %. Kontroly pokrývajú zachovanie cudzích zmien aj návrhov, výslovné načítanie, chybu obnovenia po zápise, nezmenené obnovené riadky, poradie a posuny so sekundami. Úplné a hostované výsledky sú v opravnom PR. Tento záznam nepovoľuje zlúčenie ani vydanie; skutočný model a ručné testy hardvéru/platformy zostávajú odložené.


## Záznam vydania · v0.26.1

A62-05–A62-09 boli zlúčené cez PR #62 a vydané vo v0.26.1. Nezávislá revízia Sol medium prešla; uspelo 330 jednotkových testov (dve platformové výnimky Linuxu), všetkých 24 kontajnerových kontrol rozhrania a všetkých päť CI úloh opravy. Pôvodný kontrolovaný commit aj dôkazy vyššie zostávajú historické. Skutočný model a ručná akceptácia platforiem zostávajú odložené.

## Revízia repozitára · 27. novembra 2026 · Sol (backend codex)

Revízia `main` len na čítanie na `b1591d7` (v0.31.1) vyžiadaná od inej rodiny modelov. Bežala na backende `codex` v Kiro Crew, ale potvrdenie spustenia uvádzalo `claude-sonnet-5.5`, takže rodina modelu nie je potvrdená. Správa bola odseknutá po zistení 7. Každé zistenie nižšie bolo overené čítaním kódu; vlastné reprodukcie recenzenta s dvoma Store neboli znova spustené. Stav sa mení až po overenej oprave.

| ID | Priorita | Stav | Zistenie | Požadované správanie |
| --- | --- | --- | --- | --- |
| S27-01 | P2 | Opravené, nevydané | Otvorený panel AI generovania po zmene Nastavení ďalej ukazuje starý server/model; Generovať obnoví popis a odošle poznámky v tom istom kliknutí. | Pri zmene nastavení AI otvorené panely obnoviť; ak sa cieľ líši od zobrazeného, vyžadovať ďalšie kliknutie. |
| S27-02 | P2 | Opravené, nevydané | Zahodenie (a dokončenie) testu ignoruje odpovede, ktoré iné okno uložilo po otvorení potvrdenia. | Porovnať revíziu odpovedí pod `BEGIN IMMEDIATE`; pri konflikte test ponechať a opýtať sa znova. |
| S27-03 | P2 | Opravené, nevydané | Potvrdenia zmazania predmetu a balíčka porovnávajú len názvy a počty; nahradenie kartičky počet nezmení a staré potvrdenie zmaže náhradu. | Pri oboch kaskádach potvrdzovať podľa identít/revízií podriadených záznamov (alebo revízie obsahu). |
| S27-04 | P3 | Opravené, nevydané | Uloženie kartičky sa zapíše pred obnovením balíčka; keď obnovenie zlyhá, Uložiť zostane aktívne a druhé kliknutie kartičku znova upraví a znova vynuluje plán. | Použiť vzor opakovania len čítania po zápise. |
| S27-05 | P3 | Opravené, nevydané | MCP skracuje možnosti odpovedí na 300 znakov, hoci zadávanie povoľuje 500, takže rôzne možnosti môžu vyzerať rovnako. | Vracať celé možnosti v rámci rozpočtu odpovede; zvážiť vyhľadanie otázky podľa ID. |
| S27-06 | P3 | Opravené, nevydané | Parser poznámok stále prijíma staršie písmeno odpovede zvolené modelom a potichu skracuje príliš dlhé témy. | Vyžadovať aktuálny tvar; príliš dlhé témy hlásiť ako chyby validácie. |
| S27-07 | P3 | Opravené, nevydané | Keď sa pracovné vlákno generovania nespustí, panel zostane zaneprázdnený a blokuje zmeny nastavení AI aj obnovu. | Zachytiť zlyhanie spustenia, vyčistiť úlohu a zobraziť chybu. |

### Riešenie · vetva `fix/review-s27`

Všetkých sedem bolo opravených s regresným pokrytím: `tests/test_review_s27.py` (S27-02, S27-03, S27-05), `tests/test_note_generation.py` (S27-06), `tests/test_mcp_server.py` (presné vyhľadanie) a GUI kontroly v `check_note_generation.py` (S27-01, S27-07), `check_flashcards.py` (S27-04) a `check_practice.py` (S27-02 v UI). Vrátenie každej opravy spôsobilo zlyhanie jej testu (11 z 11 mutantov zachytených). Linuxový kontajner: 393 jednotkových testov (dva preskočené kvôli platforme) a všetkých 26 GUI skriptov prešlo.

Opakovaná revízia `8fbaea9` na backende codex: S27-01 a S27-04 až S27-07 overené. Dve nadväzujúce veci boli opravené: keď po konflikte v teste zlyhá opätovné načítanie, stránka nechá ovládanie zamknuté a ukáže chybu načítania namiesto tvrdenia, že sú zobrazené aktuálne odpovede; vyhľadanie podľa ID vracia `version` (s kľúčom pre každý proces servera, takže ju nemožno použiť na skúšanie možných odpovedí), ktorú Quiz me pred hodnotením porovná. Dva návrhy boli zámerne odmietnuté: odpoveď zmenená A → B → A alebo kartička upravená a vrátená späť stále zodpovedá potvrdeniu, pretože potvrdenia porovnávajú obsah, ktorý používateľ videl, nie históriu úprav. Zmaže sa presne to, čo bolo zobrazené, a počítadlo revízií by vyžadovalo zmenu schémy.
