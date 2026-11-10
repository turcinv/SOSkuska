# Vývoj a spuštění

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

Má 10sekundovou pojistku přes Tk; nejde o tvrdý limit procesu při zamrznutí GUI smyčky. V takovém případě ukonči proces přes Ctrl+C. Syntaxe ani syntetické události nejsou ruční vizuální kontrola nebo test fyzického trackpadu.

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
