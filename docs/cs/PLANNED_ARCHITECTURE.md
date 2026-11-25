# Plánovaná architektura

[English](../PLANNED_ARCHITECTURE.md) · [Čeština](PLANNED_ARCHITECTURE.md) · [Slovenčina](../sk/PLANNED_ARCHITECTURE.md) · [Русский](../ru/PLANNED_ARCHITECTURE.md)

**Budoucí návrh, nikoli dnešní implementace.** Zde uvedené moduly a tabulky zatím neexistují, pokud je nepotvrzuje [současná architektura](CURRENT_ARCHITECTURE.md). Tento plán sám neznamená zahájení implementace všech funkcí.

Vydaná základní verze je v0.22.0 s jazyky rozhraní, uloženými konverzacemi AI a schématem 10. Průvodci níže popisují implementované funkce. Uložení nastavení nespouští síťové připojení.

Nastavení se ukládá do stejné databáze jako studijní data. [Settings](SETTINGS.md). Nastavení se ukládá transakčně ve schématu 6 s ochranou před přepsáním změn jiného okna. Migrace z verze 5 zachová všechny předchozí tabulky i data; starší aplikace novější schéma odmítne otevřít.
## Směr

Zachovat Python + CustomTkinter, místní SQLite a volitelnou AI přes Ollamu. Primární platformy Windows/Linux, ponechat funkční vývoj na macOS. Běžné studium nesmí vyžadovat cloudový účet, placené API ani spuštěnou AI. Vizuální jazyk dál rozvíjet z dnešního Dashboardu.

Oddělovat UI, studijní pravidla a ukládání postupně podle potřeb konkrétních funkcí. Nevytvářet nový UI framework ani webový backend.

## Vrstvy

```mermaid
flowchart TD
    UI[Obrazovky a UI komponenty] --> Services[Studijní služby a stav obrazovek]
    Services --> Domain[Modely a studijní pravidla]
    Services --> Repos[Repozitáře a migrace]
    Repos --> DB[(SQLite)]
    Services --> Jobs[Úlohy mimo UI vlákno]
    Jobs --> Ollama[Místní Ollama / HTTP]
    Jobs --> Files[Import a export]
    Jobs --> Queue[Fronta výsledků]
    Queue --> Main[Tk after / hlavní vlákno]
    Main --> UI
```

| Vrstva | Odpovědnost |
| --- | --- |
| UI | Widgety, navigace, zaměření, zobrazení stavů; bez SQL a blokujícího HTTP |
| Services | Spuštění studia, hodnocení, přehledy a kontext AI; bez manipulace widgety |
| Domain | Předměty, otázky, odpovědi a pravidla opakování; bez závislosti na Tk |
| Persistence | Dotazy, transakce, mapování dat a migrace |
| Integrations | Ollama a formáty souborů |

Stav obrazovky může zůstat jednoduchou datovou strukturou. Není potřeba hned zavádět rozsáhlý MVVM framework.

## Navrhované soubory

```text
pyproject.toml
src/soskuska/
    __main__.py
    bootstrap.py
    domain/             models.py, repetition.py
    services/           dashboard.py, study.py, practice.py, tutor.py
    persistence/        database.py, migrations/, repositories/
    integrations/       ollama.py, import_export.py
    ui/
        app.py, theme.py, navigation.py
        components/
        screens/        dashboard, subjects, flashcards, practice,
                        tutor, statistics, settings
    i18n/               en.json, cs.json, sk.json, ru.json
tests/
docs/
```

Přesun provádět po malých funkčních krocích. Do vytvoření balíčku zůstává platný dnešní příkaz `python soskuska/app.py`; budoucí `python -m soskuska` zatím nefunguje.

## Navrhovaný datový model

| Oblast | Návrh tabulek |
| --- | --- |
| Obsah | `subjects`, `topics`, `questions`, `answer_options` |
| Kartičky | `decks`, `flashcards`, `review_events`, `card_schedule` |
| Testy | `test_attempts`, `attempt_answers` |
| Studium | `study_sessions` s předmětem a časovými údaji |
| Plán a nastavení | `exams`, `daily_tasks`, `settings` |
| AI | `conversations`, `messages`, reference připojeného kontextu |
| Údržba | Verze schématu / evidence provedených migrací |

Konkrétní schémata musí doplnit cizí klíče, mazací pravidla, indexy a transakce. Migrace musí zachovat dnešní `tasks` a `sessions`; existující čas nesmí dostat vymyšlený předmět. Lokální profil nemá vyžadovat serverový účet.

Obnova soustředění po pádu je dostupná ve v0.17.0; viz [Obnova soustředění](FOCUS_RECOVERY.md). Rozdělení přes půlnoc zůstává návrhem. Veškerý čas nyní patří místnímu dni dokončení.

## Funkční celky

**Předměty a skutečný Dashboard:** správa předmětů, témat/otázek a skutečné součty sezení jsou implementované. Úspěšnost jednotlivých pokusů je v Practice Tests; základní celkové statistiky jsou implementované. Nová databáze je prázdná.

**Kartičky:** balíčky, editor, odhalení odpovědi, Again / Hard / Good / Easy, uložený termín a historie jsou implementované. Pravidla jsou v repetition.py a dokumentu FLASHCARDS.md; nejde o SM-2 ani FSRS. CSV import je implementovaný; pokročilejší plánování zůstává možností do budoucna.

**Testy:** výběr tématu, obtížnosti, počtu a času; uložený pokus, skóre a rozbor odpovědí jsou implementované. Import otázek z CSV je implementovaný; stránkovaná historie s filtry předmětu a dat je implementovaná.

**AI Tutor:** samostatný Ollama klient s časovým limitem, seznamem dostupných modelů, streamováním a zrušením generování. Výchozí spojení místní, adresa nastavitelná a viditelná; žádný automatický cloudový fallback. Modely načítat z Ollamy, nevyžadovat jeden pevný model.

AI stavy: nedostupná služba, žádný model, načítání, připraveno, generování, zastaveno, nedostatek paměti, model nenalezen. Samotné selhání připojení nesmí být vydáváno za jistotu, že Ollama není nainstalovaná.

Dlouhé operace běží mimo hlavní UI vlákno. Výsledky přicházejí přes frontu a `after`; pracovní vlákno nesmí volat widgety. SQLite připojení bez návrhu nesdílet mezi vlákny. První řešení může ponechat krátké zápisy v hlavním vlákně; případné pracovní úlohy dostanou vlastní připojení.

AI odpovědi nejdříve jako text, monospaced bloky kódu a Unicode matematika; pokročilé HTML/LaTeX není podmínka. Jazyk UI oddělit od jazyka odpovědi AI. Plánované jazyky: English, Czech, Slovak, Russian; AI navíc Automatic s možností ručního přepsání chybné detekce. Počítat s delšími texty a Cyrilicí.

**Statistiky a nastavení:** jednoduché Matplotlib grafy až nad skutečnými měřeními. Nastavení vzhledu, jazyka, studia, AI a správy dat. Import nejprve validovat; zálohy vytvářet jako konzistentní SQLite kopie. Obnovu provádět se zavřeným připojením a možností návratu k předchozímu souboru.

## Etapy a kritéria dokončení

| Etapa | Rozsah | Výsledek |
| --- | --- | --- |
| 1. Stabilizace | Oddělit téma/UI, chyby úložiště, migrace | Dashboard funguje a existující data zůstanou zachovaná |
| 2. Předměty | Správa předmětů, témat, zkoušek, skutečné přehledy | Nový předmět přežije restart; prázdná data se zobrazí pravdivě |
| 3. Obsah a kartičky | Editor/import, balíčky, opakování | Odpověď vytvoří záznam a plán příštího opakování |
| 4. Testy | Nastavení, průchod, výsledky a chyby | Výsledek lze otevřít a znovu spočítat z odpovědí |
| 5. AI | Ollama klient a chat | UI nezamrzá, generování jde zastavit, offline stav je srozumitelný |
| 6. Dokončení | Statistiky, jazyky, motiv, zálohy a balíčky | Ověřené instalace na cílových systémech |

Obrazovky rozvíjet iterativně po zpětné vazbě podle původního zadání. Tento návrh nevyžaduje okamžitý přepis nynějšího Dashboardu.

## Nastavení

Konverzace se ukládají do místní databáze a záloh. Volby spojení lze výslovně uložit v [Settings](SETTINGS.md); bez Save jsou dočasné.

[Nastavení](SETTINGS.md).

## Záloha a obnova

Settings nyní nabízí ruční místní zálohu a ověřenou obnovu s bezpečnostní kopií před nahrazením. Aktuální schéma je 10. Obnova zavře aplikaci; potom ji spusť znovu. Viz [Záloha a obnova](BACKUP_RESTORE.md).

## Import otázek z CSV

Banka otázek nyní podporuje import UTF-8 CSV do existujícího předmětu: šablona s hlavičkou, stránkovaný náhled, odmítnutí přesných duplicit a jedno atomické uložení. Maximum 2 MiB / 500 záznamů; seznam ukazuje 50 otázek na stránku. Aktuální schéma je 10. [Import otázek z CSV](QUESTION_CSV_IMPORT.md).

## Import kartiček z CSV

Flashcards nyní podporuje import UTF-8 CSV do existujícího balíčku: šablonu s hlavičkou, stránkovaný náhled, odmítnutí přesných duplicit a jedno atomické uložení. Maximum 2 MiB / 500 záznamů. Nové kartičky jsou ihned splatné; původní termíny a historie hodnocení zůstávají zachované. Aktuální schéma je 10. [Import kartiček z CSV](FLASHCARD_CSV_IMPORT.md).

## Uložené konverzace AI Tutor

AI Tutor nyní ukládá konverzace lokálně včetně původního serveru/modelu a stavu odpovědi. Historii lze otevřít bez sítě, výslovně se připojit pro pokračování nebo vybranou konverzaci po potvrzení smazat. Vydáno ve v0.12.0 se schématem 7, které transakčně migruje původní studijní data. [Uložené konverzace AI Tutor](TUTOR_HISTORY.md).

## Jazyk rozhraní

Výběr jazyka rozhraní je dostupný ve v0.13.0: angličtina, čeština, slovenština a ruština. Ukládá se zvlášť od jazyka AI a použije se po restartu. Aktuální schéma je 10. [Jazyk rozhraní](UI_LANGUAGES.md).

## Historie testů

Historie testů nyní nabízí všechny dokončené pokusy po 20 na stránku, filtr uloženého názvu předmětu a místních dat včetně obou hranic a otevření uloženého rozboru odpovědí. Koncepty filtrů a použitá stránka přežijí navigaci; chyba čtení zachová předchozí výsledky. Schéma zůstává 8. [Historie testů](PRACTICE_HISTORY.md).

## Přenosná verze Windows a přejímka

v0.15.0 přidává nepodepsaný přenosný ZIP pro Windows x64, sestavený a ověřený pátou úlohou CI. Přibalený pomocný program zachová oddělené CSV/zálohovací procesy; cílový počítač nepotřebuje Python. Automatické hostované kontroly a ruční seznam pro čistý počítač jsou oddělené; ruční přejímka zatím není dokončená. Vydaná verze je v0.18.1, schéma 10. [Přenosná verze Windows a přejímka](WINDOWS_PORTABLE.md) · [Kontrolní seznam](WINDOWS_ACCEPTANCE.md).

## Nastavení vzhledu

v0.16.0 přidává uložené Light/Dark/System, použité po Save bez obnovy obrazovek a ztráty aktivní práce. System sleduje Windows/macOS, na Linuxu používá Light. Aktuální schéma je 10. Uživatel 22. listopadu 2026 potvrdil dokončení testování základu a schválil sloučení PR #32. [Nastavení vzhledu](APPEARANCE.md).

## Další kroky · 22. listopadu 2026

Stav 22. listopadu 2026: uživatel potvrdil dokončení testování v0.15.0 a schválil PR #32. Tento seznam nyní cílí na v0.19.0; jednotlivé výsledky čistého počítače/DPI zde nejsou zaznamenané. Nezaškrtnuté body zůstávají neověřené; při testování nového vydání doplň důkazy pro konkrétní zařízení. [Další kroky · 22. listopadu 2026](NEXT_STEPS.md).

## Obnova soustředění po pádu

v0.17.0 přidává obnovu soustředění po pádu se schématem **10**. Před otevřením původních dat vytvoř zálohu: migrace je transakční, ale v0.16.0 databázi schématu 10 neotevře. [Obnova soustředění po pádu](FOCUS_RECOVERY.md).

## Plánované místní zálohy

Plánované místní zálohy jsou dostupné ve **v0.18.0**. Schéma SQLite zůstává **10**. Ruční záloha a obnova fungují samostatně. [Plánované místní zálohy](SCHEDULED_BACKUPS.md).
