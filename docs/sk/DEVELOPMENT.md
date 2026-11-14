# Vývoj a spustenie

Projekt ešte nemáš? Začni [klonovaním a základmi Gitu](GIT_GUIDE.md). Pravidlá pre zmeny sú v [CONTRIBUTING](CONTRIBUTING.md).

Príkazy spúšťaj z koreňa projektu. Dnešná aplikácia používa skripty v `soskuska/`, nie inštalovateľný balík.

## Tento Mac — najrýchlejšia cesta

```sh
cd "$HOME/Documents/SOSkuska"
.venv-macos/bin/python soskuska/app.py --data .local-data/dev.sqlite3
```

Vývojová databáza je oddelená od bežných používateľských údajov. Rodičovský adresár sa vytvorí automaticky a `.local-data/` je ignorovaný v Gite. Bez `--data` aplikácia použije štandardnú používateľskú databázu; nejde o rovnaký súbor. Spúšťač `soskuska/run-macos.command` prijíma rovnaké argumenty.

## Požiadavky

Overené prostredie je Python 3.12.13 / Tk 9.0 / CustomTkinter 5.2.2. Na reprodukovanie použi Python 3.12 s Tk. Na macOS aplikácia vyžaduje aspoň Tk 8.6. Samotné číslo Pythonu nezaručuje prítomnosť Tk.

Externé závislosti sú v `soskuska/requirements.txt`. Úplný lockfile zatiaľ nie je, tranzitívne verzie rieši inštalátor. Inštalácia potrebuje internet raz; beh Dashboardu potom funguje offline. Ollama sa zatiaľ nevyžaduje. Kontroly GUI potrebujú grafickú desktopovú reláciu.

## Nové prostredie na macOS

```sh
python3.12 -c "import sys, tkinter; print(sys.executable); print(sys.version); print('Tk', tkinter.TkVersion)"
python3.12 -m venv .venv-macos
.venv-macos/bin/python -m pip install -r soskuska/requirements.txt
.venv-macos/bin/python soskuska/app.py --data .local-data/dev.sqlite3
```

Na tomto Macu je vhodný interpret aj `/Users/turcinv/.local/bin/python3.12`. `/usr/bin/python3` používa staré systémové Tk 8.5; Homebrew `python3` pri overení nemal `_tkinter`. Potlačenie varovania cez `TK_SILENCE_DEPRECATION` prázdne okno neopraví.

Ak prostredie už existuje s iným Pythonom, vytvor nové pod iným názvom a uprav príkazy; inštalácia knižníc nevymení základný Python existujúceho prostredia. Spúšťač očakáva konkrétne `.venv-macos`.

## Windows — PowerShell

Ak nemáš nainštalovaný ani Python, začni podrobným návodom [Windows od nuly](WINDOWS_FIRST_RUN.md). Nasledujúci skrátený postup predpokladá už pripravený Python.

Predpoklad: nainštalovaný Python 3.12 s Tcl/Tk a spúšťačom `py`.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r soskuska/requirements.txt
.\.venv\Scripts\python.exe -c "import tkinter; print(tkinter.TkVersion)"
.\.venv\Scripts\python.exe soskuska/app.py --data .local-data/dev.sqlite3
```

Nie je potrebná aktivácia prostredia ani zmena execution policy. Windows ešte nie je prakticky overený.

## Linux

Použi Python s podporou Tk a virtuálnych prostredí. Systémové balíky bývajú `python3-tk` a `python3-venv`; presné názvy závisia od distribúcie a musia zodpovedať vybranému Pythonu.

```sh
python3 -c "import sys, tkinter; print(sys.version); print('Tk', tkinter.TkVersion)"
python3 -m venv .venv
.venv/bin/python -m pip install -r soskuska/requirements.txt
.venv/bin/python soskuska/app.py --data .local-data/dev.sqlite3
```

Linux ešte nie je prakticky overený. Na serveri bez grafickej relácie sa okno neotvorí.

## Kontroly

Syntax bez otvorenia okna:

```sh
.venv-macos/bin/python -m compileall -q soskuska
```

Natívna kontrola funkčnosti s vlastnou dočasnou databázou:

```sh
.venv-macos/bin/python soskuska/check_dashboard.py
```

Na Windows/Linux zameň interpret za cestu zo svojho prostredia. Skript krátko otvorí okno, overí zobrazené prvky, vyhľadávanie/prázdny stav, bočný panel, kompaktné rozloženie, koliesko, v Tk 9 trackpad, časovač a uloženie času. Pri úspechu vypíše `PASS` a okno zatvorí. Nepoužíva bežnú databázu.

Má 12-sekundovú poistku cez Tk; nejde o pevný časový limit procesu pri zamrznutí slučky GUI. V takom prípade ukonči proces cez Ctrl+C. Syntax ani syntetické udalosti nie sú ručná vizuálna kontrola alebo test fyzického trackpadu.

Po zmene UI ručne over 1440 × 900 aj 1024 × 700, dosiahnutie spodného obsahu, skutočné gesto/koliesko, bočný panel, vyhľadávanie, Ctrl+K / Cmd+K a Escape. Po zmene ukladania zmeň zoznam úloh a dokonči krátku reláciu; reštartuj a skontroluj údaje. Automatické opätovné načítanie kódu nie je implementované — aplikáciu treba reštartovať.

## Riešenie problémov

| Prejav | Postup |
| --- | --- |
| Prázdne okno / system Tk warning | Skontroluj interpret a verziu Tk; na tomto Macu použi `.venv-macos` |
| `No module named _tkinter` | Vyber Python zostavený s Tk; samotná inštalácia CustomTkinteru to neopraví |
| `No module named customtkinter` | Inštaluj requirements cez rovnaký interpret, ktorým spúšťaš aplikáciu |
| Trackpad neposúva obsah | Použi aktuálny `scrolling.py` a reštartuj; Tk 9 potrebuje `TouchpadScroll` |
| Chyba zápisu SQLite | Cez `--data` vyber zapisovateľnú cestu, over oprávnenia a voľné miesto |
| Chýbajú predchádzajúce údaje | Porovnaj `--data` s predvolenou používateľskou databázou |

## Ďalší vývoj a GitHub

UI je dnes v `app.py`, SQL v `storage.py`, posúvanie v `scrolling.py`. Kvôli zmene natívnej aplikácie nemusíš upravovať HTML návrh. Postupné členenie opisuje [plánovaná architektúra](PLANNED_ARCHITECTURE.md).

Do repozitára nepatria virtuálne prostredia, SQLite súbory, cache a miestna konfigurácia nástrojov. Zdrojový kód je v súkromnom repozitári [turcinv/SOSkuska](https://github.com/turcinv/SOSkuska).

Kompatibilita s pôvodným názvom: ak nová databáza v `SOSkuska` neexistuje a pôvodná `ExamPrep/dashboard.sqlite3` existuje, aplikácia použije tento pôvodný súbor. Nič automaticky nekopíruje, nepresúva ani neprepisuje. Výslovné `--data` má vždy prednosť.

Kontrola úložiska bez GUI (vrátane zachovania údajov pôvodnej aplikácie):

```sh
.venv-macos/bin/python -m unittest discover -s tests -v
```


Nová integračná kontrola tiež vytvára a upravuje predmet cez UI, overuje prázdnu databázu bez vzorových metrík, termín skúšky, väzbu relácie a vymazanie predmetu so zachovaním histórie. Migráciu pôvodných tabuliek a validáciu predmetov overujú `tests/test_subjects.py`. Všetko používa dočasné údaje.


Integračná kontrola po novom overuje aj skutočné prepnutie stĺpcov pri zmene šírky, pokračovanie plánovania časovača po chybe automatického uloženia a obnovenie zoznamu úloh pri zmene dňa. Test súbežných migrácií používa iba dočasné databázy.

## Banka tém a otázok

Kontrolu banky otázok spustíš príkazom nižšie. Používa dočasnú databázu a krátko otvorí okno. Overuje CRUD, validáciu, kombinované filtre, kompaktný editor a posúvanie, izoláciu predmetov, mazanie a opätovné otvorenie. `tests/test_questions.py` navyše overuje migráciu zo schémy 2, Unicode a konzistenciu počtov. Spolu je 32 testov bez GUI a tri natívne kontroly. Všetky prešli na macOS; Windows/Linux a fyzický trackpad týmto nie sú overené.

```sh
.venv-macos/bin/python soskuska/check_question_bank.py
```

## Opravy po kontrole hlavnej vetvy

Nová kontrola `check_review_fixes.py` používa dočasné databázy a overuje zrušenie starého potvrdenia, zmenu obsahu z druhého pripojenia, skutočný exkluzívny SQLite zámok pri polnoci, opakovanie obnovy, dátum, dokončenie časovača a syntetické posúvanie v dlhom aj krátkom poli. Na macOS navyše v oddelenom procese vyvolá skutočnú položku Quit, overí zachovanie relácie pri chybe zápisu a uloženie pri opakovaní. Spolu je 32 testov bez GUI a tri natívne kontroly. Prešli na macOS; Windows/Linux a fyzický trackpad týmto nie sú overené.

```sh
.venv-macos/bin/python soskuska/check_review_fixes.py
```

Kontrola navyše overuje súčasné zlyhanie uloženia relácie a polnočného čítania, zachovanie pokynu na ručné uloženie po obnove, skutočný SQLite zámok až po úspešnom zápise relácie počas rovnakého dňa, automatickú obnovu metrík/výberu bez duplicitného záznamu a syntetické gestá nad posuvníkom aj okrajom editora.
