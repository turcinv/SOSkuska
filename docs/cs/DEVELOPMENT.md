# Vývoj a spuštění

[English](../DEVELOPMENT.md) · [Čeština](DEVELOPMENT.md) · [Slovenčina](../sk/DEVELOPMENT.md) · [Русский](../ru/DEVELOPMENT.md)

[Testy v kontejneru](CONTAINER_TESTS.md).

```sh
docker build -f Dockerfile.tests -t soskuska-tests .
docker run --rm --init --network none --cpus 2 --memory 2g soskuska-tests
```

Projekt ještě nemáš? Začni [klonováním a základy Gitu](GIT_GUIDE.md). Pravidla pro změny jsou v [CONTRIBUTING](CONTRIBUTING.md).

Příkazy spouštěj z kořene projektu. Dnešní aplikace používá skripty v `soskuska/`, nikoli instalovatelný balíček.

## Tento Mac — nejrychlejší cesta

```sh
cd "$HOME/Documents/SOSkuska"
.venv-macos/bin/python soskuska/app.py --data .local-data/dev.sqlite3
```

Vývojová databáze je oddělená od běžných uživatelských dat. Rodičovský adresář se vytvoří automaticky a `.local-data/` je ignorovaná v Gitu. Bez `--data` aplikace použije standardní uživatelskou databázi; nejde o tentýž soubor. Spouštěč `soskuska/run-macos.command` přijímá stejné argumenty.

## Požadavky

Ověřené prostředí je Python 3.12.13 / Tk 9.0 / CustomTkinter 5.2.2. Pro reprodukování použij Python 3.12 s Tk. Na macOS aplikace vyžaduje alespoň Tk 8.6. Samotné číslo Pythonu nezaručuje přítomnost Tk.

Externí závislosti jsou v `soskuska/requirements.txt`. Úplný lockfile zatím není, tranzitivní verze řeší instalátor. Instalace potřebuje internet jednou; běh Dashboardu pak funguje offline. Ollama se zatím nevyžaduje. GUI kontroly potřebují grafickou desktopovou relaci.

## Nové prostředí na macOS

```sh
python3.12 -c "import sys, tkinter; print(sys.executable); print(sys.version); print('Tk', tkinter.TkVersion)"
python3.12 -m venv .venv-macos
.venv-macos/bin/python -m pip install -r soskuska/requirements.txt
.venv-macos/bin/python soskuska/app.py --data .local-data/dev.sqlite3
```

Na tomto Macu je vhodný interpret také `/Users/turcinv/.local/bin/python3.12`. `/usr/bin/python3` používá staré systémové Tk 8.5; Homebrew `python3` při ověření postrádal `_tkinter`. Potlačení varování přes `TK_SILENCE_DEPRECATION` prázdné okno neopraví.

Pokud prostředí už existuje s jiným Pythonem, vytvoř nové pod jiným názvem a uprav příkazy; instalace knihoven nevymění základní Python existujícího prostředí. Spouštěč očekává konkrétně `.venv-macos`.

## Windows — PowerShell

Pokud nemáš nainstalovaný ani Python, začni podrobným návodem [Windows od nuly](WINDOWS_FIRST_RUN.md). Následující zkrácený postup předpokládá již připravený Python.

Předpoklad: nainstalovaný Python 3.12 s Tcl/Tk a launcherem `py`.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r soskuska/requirements.txt
.\.venv\Scripts\python.exe -c "import tkinter; print(tkinter.TkVersion)"
.\.venv\Scripts\python.exe soskuska/app.py --data .local-data/dev.sqlite3
```

Není potřeba aktivace prostředí ani změna execution policy. Windows ještě není prakticky ověřený.

## Linux

Použij Python s podporou Tk a virtuálních prostředí. Systémové balíčky bývají `python3-tk` a `python3-venv`; přesné názvy závisí na distribuci a musejí odpovídat vybranému Pythonu.

```sh
python3 -c "import sys, tkinter; print(sys.version); print('Tk', tkinter.TkVersion)"
python3 -m venv .venv
.venv/bin/python -m pip install -r soskuska/requirements.txt
.venv/bin/python soskuska/app.py --data .local-data/dev.sqlite3
```

Linux ještě není prakticky ověřený. Na serveru bez grafické relace se okno neotevře.

## Kontroly

Syntaxe bez otevření okna:

```sh
.venv-macos/bin/python -m compileall -q soskuska
```

Nativní kontroly používají dočasné databáze a otevírají skutečná okna. Úplný seznam GUI skriptů je v `tools/run_checks.py` (26 ve v0.30.1); raději je spouštěj v [testovacím kontejneru](CONTAINER_TESTS.md), aby se na ploše neotevírala okna. Jeden skript nativně spustíš takto:

```sh
.venv-macos/bin/python soskuska/check_dashboard.py
```

Na Windows/Linux zaměň interpret za cestu ze svého prostředí. Skript krátce otevře okno, ověří mapované widgety, hledání/prázdný stav, sidebar, kompaktní rozložení, kolečko, v Tk 9 trackpad, časovač a uložení času. Při úspěchu vypíše `PASS` a okno zavře. Nepoužívá běžnou databázi.

Má 12sekundovou pojistku přes Tk; nejde o tvrdý limit procesu při zamrznutí GUI smyčky. V takovém případě ukonči proces přes Ctrl+C. Syntaxe ani syntetické události nejsou ruční vizuální kontrola nebo test fyzického trackpadu.

Základ ve v0.30.1: 351 jednotkových testů (dvě přeskočené kvůli platformě Linux) a všech 26 GUI skriptů prošlo v linuxovém kontejneru a prošlo všech pět úloh CI. Staré výsledky nevydávej za ověření netestovaných změn kódu. Hlavní pokrytí:

| Kontrola / testy | Hlavní pokrytí |
| --- | --- |
| `check_dashboard.py`, `test_storage.py`, `test_subjects.py` | Prázdná databáze, skutečné metriky, CRUD předmětů/Unicode/termíny zkoušek, vazby sezení/historie, široké/kompaktní sloupce, hledání, syntetické posouvání, opakování časovače, půlnoční checklist, souběžné migrace |
| `check_focus_recovery.py`, `test_focus.py` | Pád procesu/znovuotevření, obnova pozastaveného sezení, výhradní vlastnictví, omezené počty chyb, atomické dokončení/zahození a migrace schématu 9 |
| `check_question_bank.py`, `test_questions.py` | CRUD témat/otázek, kombinované filtry, izolace předmětů, kompaktní editor, zachovaná historie, migrace fixture schématu 2 |
| `check_review_fixes.py` | Varování u zastaralého mazání, skutečné zámky SQLite, selhání čtení/zápisu, denní záhlaví/opakování, žádná duplicitní sezení, gesta ve vnořeném editoru/posuvníku; nativní macOS Quit v ohraničeném podřízeném procesu |
| `check_practice.py`, `test_practice.py` | Nastavení, uložení odpovědi/opakování, bodování, neměnné snímky, termíny v UTC, idempotentní dokončení, pokračování v novém procesu, žádná změna posouvání/konceptu na jiné obrazovce |
| `check_flashcards.py`, `test_flashcards.py` | Zachování konceptu, opakované hledání, ochrana odhalení/hodnocení, zastaralé revize, opakování zápisu, plánování/historie, nový proces, migrace zmrazeného schématu 4 |
| `check_statistics.py`, `test_statistics.py` | Prázdný stav, místní období, vážená úspěšnost, úplná historie, konzistentní snímek čtení, opakování, kompaktní rozložení, posouvání a nový proces |
| `check_state_fixes.py` | Konflikty otázek/opětovné načtení, obnovené volby předmětu balíčku, zachování po vypršeném zahození, obnova po chybějícím pokusu a přechodné chyby |
| `check_tutor.py`, `test_tutor.py` | Fake Ollama na loopbacku, chyby Unicode/streamu, Stop/zrušení TLS, meze kontextu, navigace, vymazání a zavření při generování |
| `check_settings.py`, `test_preferences.py`, `test_settings_ui.py` | Atomické/zastaralé zápisy předvoleb, migrace/rollback ze zmrazeného schématu 5, zachované koncepty, cíl aktivního časovače, perzistence v novém procesu, žádné automatické připojení, volba modelu podle serveru |
| `check_note_generation.py`, `test_note_generation.py` | AI generování z poznámek: žádný požadavek před Generovat, strukturovaná data, parsování/validace, odpovědi umístěné aplikací, upozornění na nepodložené návrhy, atomické uložení, duplicity, zahození/přejmenování/Stop/zavření, angličtina a ruština |
| `test_mcp_server.py` | Server MCP (přeskočen bez `mcp`): seznam nástrojů a anotace jen pro čtení v bezstavovém režimu i s handshakem, každý nástroj, skryté odpovědi a `--no-answers`, striktní argumenty, limity, uvolnění lease po každém volání, chyby busy/schéma/chybějící, prompty, žádný import Tk, čistota stdout přes stdio, nezměněný soubor |
| `test_study_queries.py` | Bezokenní dotazy jen pro čtení pro MCP server: cesta k uživatelské databázi bez Tk, omezené limity/zkracování, skryté odpovědi a rubové strany kartiček, historie smazaných předmětů, srozumitelné chyby, nezměněný soubor u úložiště jen pro čtení |
| `check_studio_layout.py`, `check_ui_languages.py` | Struktura Dashboardu a banner/scéna s kočičí značkou, přizpůsobení dekorace postranního panelu, čtyři jazyky při počátečním měřítku 100/150 % |

Ostatní skripty v `tools/run_checks.py` pokrývají obnovu soustředění, zálohy a plány, importy CSV, historii Tutora, vysvětlení otázek a studijní režimy, vzhled a responzivní rozložení.

Po změně UI ručně ověř 1440 × 900 i 1024 × 700, dosažení spodního obsahu, skutečné gesto/kolečko, sidebar, hledání, Ctrl+K / Cmd+K a Escape. Po změně ukládání změň checklist a dokonči krátké sezení; restartuj a zkontroluj data. Automatické přenačítání kódu není implementované — aplikaci je nutné restartovat.

## Řešení problémů

| Projev | Postup |
| --- | --- |
| Prázdné okno / system Tk warning | Zkontroluj interpret a verzi Tk; na tomto Macu použij `.venv-macos` |
| `No module named _tkinter` | Vyber Python sestavený s Tk; samotná instalace CustomTkinteru to neopraví |
| `No module named customtkinter` | Instaluj requirements přes stejný interpret, kterým spouštíš aplikaci |
| Trackpad neposouvá obsah | Použij aktuální `scrolling.py` a restartuj; Tk 9 potřebuje `TouchpadScroll` |
| Chyba zápisu SQLite | Přes `--data` vyber zapisovatelnou cestu, ověř oprávnění a volné místo |
| Chybějí dřívější data | Porovnej `--data` s výchozí uživatelskou databází |

## Další vývoj a GitHub

UI je dnes v `app.py`, SQL v `storage.py`, posouvání v `scrolling.py`. Kvůli změně nativní aplikace nemusíš upravovat HTML návrh. Postupné členění popisuje [plánovaná architektura](PLANNED_ARCHITECTURE.md).

Do repozitáře nepatří virtuální prostředí, SQLite soubory, cache a lokální konfigurace nástrojů. Zdrojový kód je v soukromém repozitáři [turcinv/SOSkuska](https://github.com/turcinv/SOSkuska).

Kompatibilita s původním názvem: pokud nová databáze v `SOSkuska` neexistuje a původní `ExamPrep/dashboard.sqlite3` existuje, aplikace použije tento původní soubor. Nic automaticky nekopíruje, nepřesouvá ani nepřepisuje. Explicitní `--data` má vždy přednost.

Kontrola úložiště bez GUI (včetně zachování dat původní aplikace):

```sh
.venv-macos/bin/python -m unittest discover -s tests -v
```


Nová integrační kontrola také vytváří a upravuje předmět přes UI, ověřuje prázdnou databázi bez vzorových metrik, termín zkoušky, vazbu sezení a smazání předmětu se zachováním historie. Migraci původních tabulek a validaci předmětů ověřují `tests/test_subjects.py`. Vše používá dočasná data.


Integrační kontrola nově ověřuje také skutečné přepnutí sloupců při změně šířky, pokračování plánování časovače po chybě automatického uložení a obnovení checklistu při změně dne. Test souběžných migrací používá pouze dočasné databáze.

## Banka témat a otázek

Kontrolu banky otázek spustíš příkazem níže. Používá dočasnou databázi a krátce otevře okno. Ověřuje CRUD, validaci, kombinované filtry, kompaktní editor a posouvání, izolaci předmětů, mazání a opětovné otevření. `tests/test_questions.py` navíc ověřuje migraci ze schématu 2, Unicode a konzistenci počtů. Celkem je 244 testů bez GUI a patnáct nativních kontrol. Všechny prošly na macOS; Windows/Linux a fyzický trackpad nejsou tímto ověřené.

```sh
.venv-macos/bin/python soskuska/check_question_bank.py
```

## Opravy po kontrole hlavní větve

Nová kontrola `check_review_fixes.py` používá dočasné databáze a ověřuje zrušení starého potvrzení, změnu obsahu z druhého připojení, skutečný exkluzivní SQLite zámek při půlnoci, opakování obnovy, datum, dokončení časovače a syntetické posouvání v dlouhém i krátkém poli. Na macOS navíc v odděleném procesu vyvolá skutečnou položku Quit, ověří zachování sezení při chybě zápisu a uložení při opakování. Celkem je 244 testů bez GUI a patnáct nativních kontrol. Prošly na macOS; Windows/Linux a fyzický trackpad nejsou tímto ověřené.

```sh
.venv-macos/bin/python soskuska/check_review_fixes.py
```

Kontrola navíc ověřuje současné selhání uložení sezení a půlnočního čtení, zachování pokynu k ručnímu uložení po obnově, skutečný SQLite zámek až po úspěšném zápisu sezení během stejného dne, automatickou obnovu metrik/výběru bez duplicitního záznamu a syntetická gesta nad posuvníkem i okrajem editoru.

## Practice Tests — procvičování (v0.4.0)

Nová kontrola check_practice.py ověřuje konfiguraci, filtry, ukládání odpovědí včetně chyby zápisu, potvrzení/opakování dokončení, neměnnou historii, automatické dokončení po limitu, kompaktní okno a pokračování v novém procesu. test_practice.py ověřuje migraci schématu 3, uchování obsahu, skóre, idempotenci, termíny, validaci a rollback. Celkem je 244 testů a patnáct nativních kontrol. Změna je ověřená na macOS; Windows/Linux a fyzická gesta nejsou prakticky ověřené.

```sh
.venv-macos/bin/python soskuska/check_practice.py
.venv-macos/bin/python soskuska/check_practice_history.py
```

Kontrola také ověřuje, že dokončení testu na pozadí neposune otevřenou banku otázek a nezmění rozepsaný text.

## Průběžná integrace (CI)

GitHub Actions kontroluje pull requesty do main, nové commity na main a ruční spuštění. Workflow `.github/workflows/ci.yml` instaluje závislosti, ověřuje jejich kompatibilitu, syntaxi Pythonu a všechny jednotkové testy s Pythonem 3.12 na Ubuntu, Windows a macOS. Samostatná úloha spouští GUI skripty uvedené v `tools/run_checks.py` (26 ve v0.30.1) na Ubuntu pod virtuálním displejem Xvfb a pátá úloha sestaví a zkontroluje přenosný ZIP pro Windows. Každý proces má limit 60 sekund (kontroly rozložení v novém procesu uvnitř skriptu mají vlastní kratší meze). Celá úloha má limit 10 minut. Novější běh stejné větve zruší předchozí. Token má pouze čtení obsahu; workflow nic nenasazuje ani nevydává.

Výsledky a logy jsou v [Actions](https://github.com/turcinv/SOSkuska/actions/workflows/ci.yml) a v kontrolách PR. Červený stav otevři a přečti první neúspěšný krok. Po opravě pushni do stejné větve a kontroly se spustí znovu. Ruční spuštění Run workflow je dostupné po sloučení workflow do výchozí větve. Branch protection tímto není zapnutá.

Automatické testy nejsou ruční ověření Windows/macOS/Linux ani fyzického trackpadu. Linuxový CI běh neověřuje nativní nabídku Quit v macOS ani Tk 9 gesta; ty je potřeba dál kontrolovat na Macu. Fake Ollama neprokazuje kvalitu ani výkon skutečného modelu; k tomu použij `tools/evaluate_ai.py` (viz níže).

## Kartičky a opakování (v0.5.0)

check_flashcards.py ověřuje formuláře, opakované hledání, zachování rozepsaného textu při navigaci, odhalení před hodnocením, odmítnutí zastaralého hodnocení, opakování po chybě zápisu, termíny, uchování historie a nové spuštění procesu. test_flashcards.py a historický fixtures/schema_v4.sql ověřují migraci a transakce. Celkem je 244 jednotkových testů a patnáct nativních kontrol; CI spouští testy na třech systémech a GUI na Ubuntu/Xvfb.

[Podrobný návod a pravidla](FLASHCARDS.md).

```sh
.venv-macos/bin/python soskuska/check_flashcards.py
.venv-macos/bin/python soskuska/check_statistics.py
.venv-macos/bin/python soskuska/check_state_fixes.py
.venv-macos/bin/python soskuska/check_tutor.py
```

## Statistiky (v0.6.0)

V nabídce **Statistics** zvol Last 7 days, Last 30 days nebo All time. Přehled ukazuje uložený čas a sezení, otázkami váženou úspěšnost dokončených testů, počty vlastních hodnocení kartiček, čas podle předmětu a denní aktivitu. Refresh nebo návrat na obrazovku načte nový snímek. Nejde o měření zvládnutí učiva.

Nových 16 testů ověřuje období, místní dny, váhu otázek, úplnou historii, zachování po smazání, pouze čtení, souběžný snímek a opakování po chybě. Nativní kontrola ověřuje prázdný stav, filtry, chybu a opakování, navigaci, kompaktní rozložení, posouvání a otevření v novém procesu. Celkem 244 jednotkových testů a patnáct nativních kontrol; používají dočasná data.

```sh
.venv-macos/bin/python soskuska/check_statistics.py
.venv-macos/bin/python soskuska/check_state_fixes.py
.venv-macos/bin/python soskuska/check_tutor.py
```

[Podrobná pravidla](STATISTICS.md).

## Opravy souběžných změn (v0.6.2)

Nových osm jednotkových testů pokrývá termíny včetně čekání na zámek, rollback, konflikty otázek a odlišení odstraněného testu. check_state_fixes.py navíc ověřuje skutečné formuláře, zachování rozepsaného obsahu, konflikt a nové načtení, zachování výsledku po termínu a obnovu po odstranění z jiné instance. Celkem 244 jednotkových testů a patnáct nativních kontrol s dočasnými daty.

```sh
.venv-macos/bin/python soskuska/check_state_fixes.py
.venv-macos/bin/python soskuska/check_tutor.py
```

## AI Tutor s Ollamou (v0.7.0)

V AI Tutor připoj vlastní Ollama server přes Connect / refresh, vyber model a jazyk odpovědi a zadej otázku. Odpověď přichází průběžně; Stop ji zastaví. Ostatní obrazovky zůstávají použitelné během generování i bez Ollamy. Chat se ukládá do místní databáze a lze jej otevřít po restartu; viz průvodce historií.

23 nových testů a check_tutor.py používají výhradně fake Ollama server na loopbacku a dočasná data. Ověřují protokol, Unicode, chybné odpovědi, přerušení streamu/TLS handshake, limity, kontext, navigaci a zavření při generování. Celkem 244 jednotkových testů a patnáct GUI kontrol. Tyto testy neověřují kvalitu skutečného modelu ani jeho hardwarové nároky.

```sh
.venv-macos/bin/python soskuska/check_tutor.py
```

[Návod AI Tutor](AI_TUTOR.md).

## Nastavení

Konverzace se ukládají do místní databáze a záloh. Volby spojení lze výslovně uložit v [Settings](SETTINGS.md); bez Save jsou dočasné.

[Nastavení](SETTINGS.md).

Nastavení se ukládá transakčně ve schématu 6 s ochranou před přepsáním změn jiného okna. Migrace z verze 5 zachová všechny předchozí tabulky i data; starší aplikace novější schéma odmítne otevřít.

`tests/test_preferences.py`, `tests/fixtures/schema_v5.sql`, `check_settings.py`.

```sh
.venv-macos/bin/python soskuska/check_settings.py
```

```powershell
.venv\Scripts\python.exe soskuska/check_settings.py
```

## Záloha a obnova

Settings nyní nabízí ruční místní zálohu a ověřenou obnovu s bezpečnostní kopií před nahrazením. Aktuální schéma je 10. Obnova zavře aplikaci; potom ji spusť znovu. Viz [Záloha a obnova](BACKUP_RESTORE.md).

`tests/test_backup.py`, `tests/test_backup_review.py`, `soskuska/check_backup.py`.

```sh
.venv-macos/bin/python soskuska/check_backup.py
```

```powershell
.\.venv\Scripts\python.exe soskuska/check_backup.py
```

## Import otázek z CSV

Banka otázek nyní podporuje import UTF-8 CSV do existujícího předmětu: šablona s hlavičkou, stránkovaný náhled, odmítnutí přesných duplicit a jedno atomické uložení. Maximum 2 MiB / 500 záznamů; seznam ukazuje 50 otázek na stránku. Aktuální schéma je 10. [Import otázek z CSV](QUESTION_CSV_IMPORT.md).

`tests/test_csv_import.py`, `soskuska/check_csv_import.py`.

```sh
.venv-macos/bin/python soskuska/check_csv_import.py
```

```powershell
.\.venv\Scripts\python.exe soskuska/check_csv_import.py
```

## Import kartiček z CSV

Flashcards nyní podporuje import UTF-8 CSV do existujícího balíčku: šablonu s hlavičkou, stránkovaný náhled, odmítnutí přesných duplicit a jedno atomické uložení. Maximum 2 MiB / 500 záznamů. Nové kartičky jsou ihned splatné; původní termíny a historie hodnocení zůstávají zachované. Aktuální schéma je 10. [Import kartiček z CSV](FLASHCARD_CSV_IMPORT.md).

`tests/test_flashcard_csv_import.py`, `soskuska/check_flashcard_import.py`.

```sh
.venv-macos/bin/python soskuska/check_flashcard_import.py
```

```powershell
.\.venv\Scripts\python.exe soskuska/check_flashcard_import.py
```

## Uložené konverzace AI Tutor

AI Tutor nyní ukládá konverzace lokálně včetně původního serveru/modelu a stavu odpovědi. Historii lze otevřít bez sítě, výslovně se připojit pro pokračování nebo vybranou konverzaci po potvrzení smazat. Vydáno ve v0.12.0 se schématem 7, které transakčně migruje původní studijní data. [Uložené konverzace AI Tutor](TUTOR_HISTORY.md).

`tests/test_tutor_history.py`, `soskuska/check_tutor_history.py`.

```sh
.venv-macos/bin/python soskuska/check_tutor_history.py
```

```powershell
.\.venv\Scripts\python.exe soskuska/check_tutor_history.py
```

## Jazyk rozhraní

Výběr jazyka rozhraní je dostupný ve v0.13.0: angličtina, čeština, slovenština a ruština. Ukládá se zvlášť od jazyka AI a použije se po restartu. Aktuální schéma je 10. [Jazyk rozhraní](UI_LANGUAGES.md).

`tests/test_localization.py`, `soskuska/check_ui_languages.py`.

```sh
.venv-macos/bin/python soskuska/check_ui_languages.py
```

```powershell
.\.venv\Scripts\python.exe soskuska/check_ui_languages.py
```

## Historie testů

Historie testů nyní nabízí všechny dokončené pokusy po 20 na stránku, filtr uloženého názvu předmětu a místních dat včetně obou hranic a otevření uloženého rozboru odpovědí. Koncepty filtrů a použitá stránka přežijí navigaci; chyba čtení zachová předchozí výsledky. Schéma zůstává 8. [Historie testů](PRACTICE_HISTORY.md).

```sh
python soskuska/check_practice_history.py
```

## Přenosná verze Windows a přejímka

v0.15.0 přidává nepodepsaný přenosný ZIP pro Windows x64, sestavený a ověřený pátou úlohou CI. Přibalený pomocný program zachová oddělené CSV/zálohovací procesy; cílový počítač nepotřebuje Python. Automatické hostované kontroly a ruční seznam pro čistý počítač jsou oddělené; ruční přejímka zatím není dokončená. Vydaná verze je v0.30.1, schéma 10. [Přenosná verze Windows a přejímka](WINDOWS_PORTABLE.md) · [Kontrolní seznam](WINDOWS_ACCEPTANCE.md).

Každé vydání přikládá ZIP, kontrolní součet a zprávu o přejímce sestavené během CI na přesně označeném commitu main. Ruční přejímka na čistém počítači zůstává NEPROVEDENA.

## Nastavení vzhledu

v0.16.0 přidává uložené Light/Dark/System, použité po Save bez obnovy obrazovek a ztráty aktivní práce. System sleduje Windows/macOS, na Linuxu používá Light. Aktuální schéma je 10. Uživatel 22. listopadu 2026 potvrdil dokončení testování základu a schválil sloučení PR #32. [Nastavení vzhledu](APPEARANCE.md).

```sh
python soskuska/check_appearance.py
```

## Obnova soustředění po pádu

v0.17.0 přidává obnovu soustředění po pádu se schématem **10**. Před otevřením původních dat vytvoř zálohu: migrace je transakční, ale v0.16.0 databázi schématu 10 neotevře. [Obnova soustředění po pádu](FOCUS_RECOVERY.md).

## Plánované místní zálohy

Plánované místní zálohy jsou dostupné ve **v0.18.0**. Schéma SQLite zůstává **10**. Ruční záloha a obnova fungují samostatně. [Plánované místní zálohy](SCHEDULED_BACKUPS.md).

## Opravy po revizi hlavní větve

Opravy vydané ve v0.18.1 přes PR #38 sleduje [záznam revize Astra](REVIEW_FINDINGS.md). Schéma zůstává 10 a vydaná verze je v0.30.1. Úpravy předmětu porovnají původní obsah pod zápisovým zámkem; konflikt zachová koncept. Před opětovným otevřením úprav pro načtení nejnovější verze si potřebné změny zkopíruj. Smazání otázky/tématu porovná zobrazený obsah a po změně vyžaduje nové potvrzení. Návrat ke stejnému předmětu zachová editor otázky/tématu, filtry i původní identitu, také při opakování čtení; smazané vybrané téma zůstane nedostupné, dokud výslovně nevybereš jiné téma nebo možnost Bez tématu. Jiný předmět editor stále resetuje. Novější potvrzení úspěšné denní zálohy odstraní staré oznámení chyby bez dalšího zápisu zálohy.


## Vysvětlení otázek · v0.25.0

Dokončené výsledky Practice včetně historie nabízejí **Vysvětlit tuto otázku**. Otevřete místní náhled a zvolte **Připravit v Tutorovi**. Použije se uložený snímek otázky, čtyři možnosti, vaše odpověď nebo Unanswered, uložený klíč a vysvětlení, i po smazání původního obsahu. Náhled ani příprava nic nepřipojují a neodesílají. V Tutorovi zkontrolujte server, model a jazyk, podle potřeby výslovně použijte Connect a poté Send. Upravitelný koncept využívá běžnou místní historii, Stop a opakování uložení.

Tutor musí být nečinný, v čistém New chat s prázdným dotazem a bez čekajícího potvrzení či neuložené odpovědi. Stávající práce zůstává zachována; dokončete ji nebo výslovně potvrďte New chat a opakujte akci. Celý dotaz přes 4 000 znaků je odmítnut s uvedením délky, bez zkracování. Klíč i AI se mohou mýlit; skóre ani zdrojová data se nemění. Automatic požaduje jazyk dodané otázky; výslovná volba jazyka má přednost. Pokyny dotazu jsou anglicky, obsah uživatele se nemění. Schéma zůstává 10 a vydaná verze je v0.30.1.

Implementace: `question_explanation.py` sestavuje omezený dotaz ze snímku, `practice_page.py` řídí náhled a kontrolu aktuálního výsledku, `tutor_page.py` chrání vložení konceptu. Send uloží dotaz před HTTP. Automatické testy používají dočasná data a místní FakeOllama; kvalita modelu a nativní ověření platformy/DPI zůstávají ruční.


## Studijní režimy AI · v0.26.0

V dokončeném výsledku otevřete **Vysvětlit tuto otázku** a před **Připravit v Tutorovi** vyberte **Studijní režim**. **Vysvětlit odpověď** zachová dosavadní vysvětlení; **Vysvětlit jednoduše** požaduje krátké kroky pro začátečníka a příklad; **Dát nápovědu** požaduje jednu pojmovou nápovědu a z dotazu vynechá vaši odpověď, uložený klíč i vysvětlení; **Procvičit mě** klade jednu novou doplňující otázku a před zpětnou vazbou čeká na odpověď. Jde o neformální procvičování bez zápisu bodovaného testu nebo změny zdrojů.

Změna režimu obnoví přesný místní náhled a zneplatní jeho předchozí akci přípravy. Připojení, odeslání a vytvoření konverzace vyžadují stávající výslovné ovládání. Odeslaný dotaz se ukládá do běžné místní historie; platí dosavadní jazyk, limit 4 000 znaků, ochrana čistého chatu, Zastavit a opakování uložení. Nápověda stále obsahuje čtyři možnosti: model může odpověď odvodit či prozradit a již zobrazené výsledky zůstávají viditelné. Kvalita a dodržení režimu byly poprvé ověřeny se skutečným modelem 26. listopadu 2026 (viz hodnocení AI níže); širší testování modelů zůstává ruční. Automatické testy používají místní FakeOllama. Vydaná verze je v0.30.1, schéma 10.


## Opravy po revizi Astra · v0.26.1

Editory balíčku a tématu nyní porovnávají původní upravovaný snímek pod zápisovým zámkem. Konflikt zachová koncept a zobrazí upozornění; před opětovným otevřením úpravy balíčku nebo přejmenování tématu zkopírujte potřebné změny. Varování balíčku je také u Uložit. Po potvrzeném uložení balíčku změní chyba načtení tlačítko na Obnovit balíček a opakuje jen čtení, nikoli zápis.

Počty, seřazené fronty, hodnocení a kontroly opakování kartiček porovnávají skutečné časové okamžiky včetně obnovených posunů a mikrosekund. Statistiky a historie sdílejí převod povolených časů ISO na místní den, včetně posunů se sekundami. Uložené časy se nepřepisují. Přesné celočíselné klíče UTC pokrývají celý přijatý rozsah; pokud systém nezvládne místní převod krajního data, použije se den UTC omezený na podporovaný kalendář. Obnova vyžaduje samostatnou zálohu schématu 10; popis migrací zůstává historický. Vydaná verze je v0.30.1, schéma 10.


## Nový studijní prostor · v0.27.0

Nová kompozice Dashboardu nahrazuje předchozí postupné úpravy: čtyři souhrnné dlaždice, výrazná část soustředění s živými kruhovými hodinami, karty předmětů s monogramy a měsíční přehled uložených termínů. Postranní panel používá místně kreslené ikony a vlastní tmavé barvy; sdílené plochy a párový Dark/Light vzhled se mění v celé aplikaci. Tato fáze zavádí Dashboard a společný rámec; ostatní stránky navážou po vizuální zpětné vazbě. [Ukázky a rozsah](../agents/design/study-studio-dashboard/README.md).

Hodiny ukazují skutečný zbývající čas a původní cíl aktivního sezení. Kalendář používá úplný snímek předmětů; nejbližší zkoušky zachovají přesná data a limit pěti položek. Klávesové hledání, chyba uložení a obnova soustředění posunou ovládání do viditelné části kompaktního okna; čekající posun zruší navigace či hledání. Změna rozložení nečte data. Schéma zůstává 10, vydaná verze v0.30.1. Kontejnerové a simulované měřítko neověřují nativní platformu.


## Grafické soubory

V prostředí projektu spusťte `python tools/build_brand_assets.py` pro obnovení souborů SVG, PNG, ICO a ICNS v `soskuska/assets/brand/`. Generátor vyžaduje pouze Pillow; poté aplikaci restartujte. CI Windows kontroluje přibalené soubory, ikonu EXE a spuštění balíčku. Vizuální ověření na skutečné platformě a při různém DPI zůstává ruční.

## Kočičí značka · v0.29.0

`theme.py` obsahuje paletu Charcoal/Lavender/Violet/Cream s párovými rolemi Light/Dark; `studio_widgets.py` pomocí Pillow kreslí scénu banneru, avatar, otisky tlapek, ikony dlaždic a dekoraci postranního panelu. Pravidla kontrastu vynucují `tests/test_appearance.py` a živý audit v `check_appearance.py`. Předání designu a snímky: [kočičí značka](../agents/design/cat-brand/README.md).

## AI generování z poznámek · v0.30.0 / v0.30.1

**Generovat pomocí AI** v sadách kartiček a bankách otázek vytváří návrhy položek z vložených poznámek pomocí uloženého modelu Ollama; viz [uživatelský průvodce](AI_NOTE_GENERATION.md). `note_generation.py` obsahuje prompt, schéma JSON, parsování a kontrolu opory v poznámkách; `ai_generation_panel.py` panel pro kontrolu. Kontroly:

```sh
.venv-macos/bin/python -m unittest discover -s tests -p test_note_generation.py
.venv-macos/bin/python soskuska/check_note_generation.py   # opens windows; prefer the container
```

Prompty lze vyhodnotit se skutečným místním modelem bez otevírání oken a bez zásahu do jakékoli databáze:

```sh
ollama pull qwen3:4b-instruct-2507-q4_K_M
.venv-macos/bin/python tools/evaluate_ai.py --model qwen3:4b-instruct-2507-q4_K_M --output .local-data/ai-eval
```

### Testy serveru MCP

`tests/test_mcp_server.py` se přeskočí, pokud není nainstalováno volitelné SDK. CI ho instaluje v unit jobu na Ubuntu a selže, pokud se tyto testy přeskočí; testovací kontejner ho instaluje také. Lokálně použijte samostatné prostředí, aby prostředí aplikace zůstalo beze změny:

```sh
.venv-macos/bin/python -m venv .local-data/mcp-venv
.local-data/mcp-venv/bin/python -m pip install -r soskuska/requirements-mcp.txt
.local-data/mcp-venv/bin/python -m unittest tests.test_mcp_server -v
```

Nástroj zapíše `ai-evaluation.json` se surovými odpověďmi, počty platných výstupů, časováním a heuristickými příznaky (opora v poznámkách, jazyk, únik nápovědy) pro lidskou kontrolu. Po každé změně promptu nebo schématu jej spusťte znovu a porovnejte se [záznamem z 26. listopadu 2026](../agents/design/ai-note-generation/EVALUATION.md). Je to ruční nástroj, není součástí CI.
