# Vývoj a spuštění

Projekt ještě nemáš? Začni [klonováním a základy Gitu](GIT_GUIDE.md). Pravidla pro změny jsou v [CONTRIBUTING](../CONTRIBUTING.md).

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

Nativní kontrola funkčnosti s vlastní dočasnou databází:

```sh
.venv-macos/bin/python soskuska/check_dashboard.py
```

Na Windows/Linux zaměň interpret za cestu ze svého prostředí. Skript krátce otevře okno, ověří mapované widgety, hledání/prázdný stav, sidebar, kompaktní rozložení, kolečko, v Tk 9 trackpad, časovač a uložení času. Při úspěchu vypíše `PASS` a okno zavře. Nepoužívá běžnou databázi.

Má 12sekundovou pojistku přes Tk; nejde o tvrdý limit procesu při zamrznutí GUI smyčky. V takovém případě ukonči proces přes Ctrl+C. Syntaxe ani syntetické události nejsou ruční vizuální kontrola nebo test fyzického trackpadu.

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

Kontrolu banky otázek spustíš příkazem níže. Používá dočasnou databázi a krátce otevře okno. Ověřuje CRUD, validaci, kombinované filtry, kompaktní editor a posouvání, izolaci předmětů, mazání a opětovné otevření. `tests/test_questions.py` navíc ověřuje migraci ze schématu 2, Unicode a konzistenci počtů. Celkem je 106 testů bez GUI a osm nativních kontrol. Všechny prošly na macOS; Windows/Linux a fyzický trackpad nejsou tímto ověřené.

```sh
.venv-macos/bin/python soskuska/check_question_bank.py
```

## Opravy po kontrole hlavní větve

Nová kontrola `check_review_fixes.py` používá dočasné databáze a ověřuje zrušení starého potvrzení, změnu obsahu z druhého připojení, skutečný exkluzivní SQLite zámek při půlnoci, opakování obnovy, datum, dokončení časovače a syntetické posouvání v dlouhém i krátkém poli. Na macOS navíc v odděleném procesu vyvolá skutečnou položku Quit, ověří zachování sezení při chybě zápisu a uložení při opakování. Celkem je 106 testů bez GUI a osm nativních kontrol. Prošly na macOS; Windows/Linux a fyzický trackpad nejsou tímto ověřené.

```sh
.venv-macos/bin/python soskuska/check_review_fixes.py
```

Kontrola navíc ověřuje současné selhání uložení sezení a půlnočního čtení, zachování pokynu k ručnímu uložení po obnově, skutečný SQLite zámek až po úspěšném zápisu sezení během stejného dne, automatickou obnovu metrik/výběru bez duplicitního záznamu a syntetická gesta nad posuvníkem i okrajem editoru.

## Practice Tests — procvičování (v0.4.0)

Nová kontrola check_practice.py ověřuje konfiguraci, filtry, ukládání odpovědí včetně chyby zápisu, potvrzení/opakování dokončení, neměnnou historii, automatické dokončení po limitu, kompaktní okno a pokračování v novém procesu. test_practice.py ověřuje migraci schématu 3, uchování obsahu, skóre, idempotenci, termíny, validaci a rollback. Celkem je 106 testů a osm nativních kontrol. Změna je ověřená na macOS; Windows/Linux a fyzická gesta nejsou prakticky ověřené.

```sh
.venv-macos/bin/python soskuska/check_practice.py
```

Kontrola také ověřuje, že dokončení testu na pozadí neposune otevřenou banku otázek a nezmění rozepsaný text.

## Průběžná integrace (CI)

GitHub Actions kontroluje pull requesty do main, nové commity na main a ruční spuštění. Workflow `.github/workflows/ci.yml` instaluje závislosti, ověřuje jejich kompatibilitu, syntaxi Pythonu a všechny jednotkové testy s Pythonem 3.12 na Ubuntu, Windows a macOS. Samostatná úloha spouští osm nativních kontrolních skriptů na Ubuntu pod virtuálním displejem Xvfb; každý proces má limit 60 sekund. Celá úloha má limit 10 minut. Novější běh stejné větve zruší předchozí. Token má pouze čtení obsahu; workflow nic nenasazuje ani nevydává.

Výsledky a logy jsou v [Actions](https://github.com/turcinv/SOSkuska/actions/workflows/ci.yml) a v kontrolách PR. Červený stav otevři a přečti první neúspěšný krok. Po opravě pushni do stejné větve a kontroly se spustí znovu. Ruční spuštění Run workflow je dostupné po sloučení workflow do výchozí větve. Branch protection tímto není zapnutá.

Automatické testy nejsou ruční ověření Windows/macOS/Linux ani fyzického trackpadu. Linuxový CI běh neověřuje nativní nabídku Quit v macOS ani Tk 9 gesta; ty je potřeba dál kontrolovat na Macu.

## Kartičky a opakování (v0.5.0)

check_flashcards.py ověřuje formuláře, opakované hledání, zachování rozepsaného textu při navigaci, odhalení před hodnocením, odmítnutí zastaralého hodnocení, opakování po chybě zápisu, termíny, uchování historie a nové spuštění procesu. test_flashcards.py a historický fixtures/schema_v4.sql ověřují migraci a transakce. Celkem je 106 jednotkových testů a osm nativních kontrol; CI spouští testy na třech systémech a GUI na Ubuntu/Xvfb.

[Podrobný návod a pravidla](FLASHCARDS.md).

```sh
.venv-macos/bin/python soskuska/check_flashcards.py
.venv-macos/bin/python soskuska/check_statistics.py
.venv-macos/bin/python soskuska/check_state_fixes.py
.venv-macos/bin/python soskuska/check_tutor.py
```

## Statistiky (v0.6.0)

V nabídce **Statistics** zvol Last 7 days, Last 30 days nebo All time. Přehled ukazuje uložený čas a sezení, otázkami váženou úspěšnost dokončených testů, počty vlastních hodnocení kartiček, čas podle předmětu a denní aktivitu. Refresh nebo návrat na obrazovku načte nový snímek. Nejde o měření zvládnutí učiva.

Nových 16 testů ověřuje období, místní dny, váhu otázek, úplnou historii, zachování po smazání, pouze čtení, souběžný snímek a opakování po chybě. Nativní kontrola ověřuje prázdný stav, filtry, chybu a opakování, navigaci, kompaktní rozložení, posouvání a otevření v novém procesu. Celkem 106 jednotkových testů a osm nativních kontrol; používají dočasná data.

```sh
.venv-macos/bin/python soskuska/check_statistics.py
.venv-macos/bin/python soskuska/check_state_fixes.py
.venv-macos/bin/python soskuska/check_tutor.py
```

[Podrobná pravidla](STATISTICS.md).

## Opravy souběžných změn (v0.6.2)

Nových osm jednotkových testů pokrývá termíny včetně čekání na zámek, rollback, konflikty otázek a odlišení odstraněného testu. check_state_fixes.py navíc ověřuje skutečné formuláře, zachování rozepsaného obsahu, konflikt a nové načtení, zachování výsledku po termínu a obnovu po odstranění z jiné instance. Celkem 106 jednotkových testů a osm nativních kontrol s dočasnými daty.

```sh
.venv-macos/bin/python soskuska/check_state_fixes.py
.venv-macos/bin/python soskuska/check_tutor.py
```

## AI Tutor s Ollamou (nevydáno)

V AI Tutor připoj vlastní Ollama server přes Connect / refresh, vyber model a jazyk odpovědi a zadej otázku. Odpověď přichází průběžně; Stop ji zastaví. Ostatní obrazovky zůstávají použitelné během generování i bez Ollamy. Chat je pouze pro aktuální spuštění aplikace, neukládá se do databáze.

22 nových testů a check_tutor.py používají výhradně fake Ollama server na loopbacku a dočasná data. Ověřují protokol, Unicode, chybné odpovědi, přerušení streamu/TLS handshake, limity, kontext, navigaci a zavření při generování. Celkem 106 jednotkových testů a osm GUI kontrol. Tyto testy neověřují kvalitu skutečného modelu ani jeho hardwarové nároky.

```sh
.venv-macos/bin/python soskuska/check_tutor.py
```

[Návod AI Tutor](AI_TUTOR.md).
