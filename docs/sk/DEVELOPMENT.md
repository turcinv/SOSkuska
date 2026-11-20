# Vývoj a spustenie

[English](../DEVELOPMENT.md) · [Čeština](../cs/DEVELOPMENT.md) · [Slovenčina](DEVELOPMENT.md) · [Русский](../ru/DEVELOPMENT.md)

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

Kontrolu banky otázok spustíš príkazom nižšie. Používa dočasnú databázu a krátko otvorí okno. Overuje CRUD, validáciu, kombinované filtre, kompaktný editor a posúvanie, izoláciu predmetov, mazanie a opätovné otvorenie. `tests/test_questions.py` navyše overuje migráciu zo schémy 2, Unicode a konzistenciu počtov. Spolu je 234 testov bez GUI a štrnásť natívnych kontrol. Všetky prešli na macOS; Windows/Linux a fyzický trackpad týmto nie sú overené.

```sh
.venv-macos/bin/python soskuska/check_question_bank.py
```

## Opravy po kontrole hlavnej vetvy

Nová kontrola `check_review_fixes.py` používa dočasné databázy a overuje zrušenie starého potvrdenia, zmenu obsahu z druhého pripojenia, skutočný exkluzívny SQLite zámok pri polnoci, opakovanie obnovy, dátum, dokončenie časovača a syntetické posúvanie v dlhom aj krátkom poli. Na macOS navyše v oddelenom procese vyvolá skutočnú položku Quit, overí zachovanie relácie pri chybe zápisu a uloženie pri opakovaní. Spolu je 234 testov bez GUI a štrnásť natívnych kontrol. Prešli na macOS; Windows/Linux a fyzický trackpad týmto nie sú overené.

```sh
.venv-macos/bin/python soskuska/check_review_fixes.py
```

Kontrola navyše overuje súčasné zlyhanie uloženia relácie a polnočného čítania, zachovanie pokynu na ručné uloženie po obnove, skutočný SQLite zámok až po úspešnom zápise relácie počas rovnakého dňa, automatickú obnovu metrík/výberu bez duplicitného záznamu a syntetické gestá nad posuvníkom aj okrajom editora.

## Practice Tests — precvičovanie (v0.4.0)

Nová kontrola check_practice.py overuje konfiguráciu, filtre, ukladanie odpovedí vrátane chyby zápisu, potvrdenie/opakovanie dokončenia, nemennú históriu, automatické dokončenie po limite, kompaktné okno a pokračovanie v novom procese. test_practice.py overuje migráciu schémy 3, uchovanie obsahu, skóre, idempotenciu, termíny, validáciu a rollback. Spolu je 234 testov a štrnásť natívnych kontrol. Zmena je overená na macOS; Windows/Linux a fyzické gestá nie sú prakticky overené.

```sh
.venv-macos/bin/python soskuska/check_practice.py
```

Kontrola tiež overuje, že dokončenie testu na pozadí neposunie otvorenú banku otázok a nezmení rozpísaný text.

## Priebežná integrácia (CI)

GitHub Actions kontroluje pull requesty do main, nové commity na main a ručné spustenie. Workflow `.github/workflows/ci.yml` inštaluje závislosti, overuje ich kompatibilitu, syntax Pythonu a všetky jednotkové testy s Pythonom 3.12 na Ubuntu, Windows a macOS. Samostatná úloha spúšťa štrnásť natívnych kontrolných skriptov na Ubuntu pod virtuálnym displejom Xvfb; každý proces má limit 60 sekúnd. Celá úloha má limit 10 minút. Novší beh rovnakej vetvy zruší predchádzajúci. Token má iba čítanie obsahu; workflow nič nenasadzuje ani nevydáva.

Výsledky a logy sú v [Actions](https://github.com/turcinv/SOSkuska/actions/workflows/ci.yml) a v kontrolách PR. Otvor červený stav a prečítaj prvý neúspešný krok. Po oprave pushni do rovnakej vetvy a kontroly sa spustia znovu. Ručné spustenie Run workflow je dostupné po zlúčení workflow do predvolenej vetvy. Branch protection týmto nie je zapnutá.

Automatické testy nie sú ručným overením Windows/macOS/Linux ani fyzického trackpadu. Linuxový CI beh neoveruje natívnu ponuku Quit v macOS ani Tk 9 gestá; tie treba naďalej kontrolovať na Macu.

## Kartičky a opakovanie (v0.5.0)

check_flashcards.py overuje formuláre, opakované hľadanie, zachovanie rozpísaného textu pri navigácii, odhalenie pred hodnotením, odmietnutie zastaraného hodnotenia, opakovanie po chybe zápisu, termíny, uchovanie histórie a nové spustenie procesu. test_flashcards.py a historický fixtures/schema_v4.sql overujú migráciu a transakcie. Spolu je 234 jednotkových testov a štrnásť natívnych kontrol; CI spúšťa testy na troch systémoch a GUI na Ubuntu/Xvfb.

[Podrobný návod a pravidlá](FLASHCARDS.md).

```sh
.venv-macos/bin/python soskuska/check_flashcards.py
.venv-macos/bin/python soskuska/check_statistics.py
.venv-macos/bin/python soskuska/check_state_fixes.py
.venv-macos/bin/python soskuska/check_tutor.py
```

## Štatistiky (v0.6.0)

V ponuke **Statistics** zvoľ Last 7 days, Last 30 days alebo All time. Prehľad ukazuje uložený čas a relácie, úspešnosť dokončených testov váženú otázkami, počty vlastných hodnotení kartičiek, čas podľa predmetu a dennú aktivitu. Refresh alebo návrat na obrazovku načíta novú snímku. Nejde o meranie zvládnutia učiva.

Nových 16 testov overuje obdobia, miestne dni, váhu otázok, úplnú históriu, zachovanie po zmazaní, iba čítanie, súbežnú snímku a opakovanie po chybe. Natívna kontrola overuje prázdny stav, filtre, chybu a opakovanie, navigáciu, kompaktné rozloženie, posúvanie a otvorenie v novom procese. Celkovo 234 jednotkových testov a štrnásť natívnych kontrol; používajú dočasné údaje.

```sh
.venv-macos/bin/python soskuska/check_statistics.py
.venv-macos/bin/python soskuska/check_state_fixes.py
.venv-macos/bin/python soskuska/check_tutor.py
```

[Podrobné pravidlá](STATISTICS.md).

## Opravy súbežných zmien (v0.6.2)

Osem nových jednotkových testov pokrýva termíny vrátane čakania na zámok, rollback, konflikty otázok a odlíšenie odstráneného testu. check_state_fixes.py navyše overuje skutočné formuláre, zachovanie rozpísaného obsahu, konflikt a nové načítanie, zachovanie výsledku po termíne a obnovu po odstránení z inej inštancie. Celkovo 234 jednotkových testov a štrnásť natívnych kontrol s dočasnými údajmi.

```sh
.venv-macos/bin/python soskuska/check_state_fixes.py
.venv-macos/bin/python soskuska/check_tutor.py
```

## AI Tutor s Ollamou (v0.7.0)

V AI Tutor pripoj vlastný server Ollama cez Connect / refresh, vyber model a jazyk odpovede a zadaj otázku. Odpoveď prichádza priebežne; Stop ju zastaví. Ostatné obrazovky zostávajú použiteľné počas generovania aj bez Ollamy. Chat sa ukladá do miestnej databázy a možno ho otvoriť po reštarte; pozri sprievodcu históriou.

23 nových testov a check_tutor.py používajú výhradne fake server Ollama na loopbacku a dočasné údaje. Overujú protokol, Unicode, chybné odpovede, prerušenie streamu/TLS handshake, limity, kontext, navigáciu a zatvorenie počas generovania. Celkovo 234 jednotkových testov a štrnásť GUI kontrol. Tieto testy neoverujú kvalitu skutočného modelu ani jeho hardvérové nároky.

```sh
.venv-macos/bin/python soskuska/check_tutor.py
```

[Návod AI Tutor](AI_TUTOR.md).

## Nastavenia

Konverzácie sa ukladajú do miestnej databázy a záloh. Voľby spojenia možno výslovne uložiť v [Settings](SETTINGS.md); bez Save sú dočasné.

[Nastavenia](SETTINGS.md).

Nastavenia sa ukladajú transakčne v schéme 6 s ochranou pred prepísaním zmien iného okna. Migrácia z verzie 5 zachová všetky predchádzajúce tabuľky aj údaje; staršia aplikácia novšiu schému odmietne otvoriť.

`tests/test_preferences.py`, `tests/fixtures/schema_v5.sql`, `check_settings.py`.

```sh
.venv-macos/bin/python soskuska/check_settings.py
```

```powershell
.venv\Scripts\python.exe soskuska/check_settings.py
```

## Záloha a obnova

Settings teraz ponúka ručnú miestnu zálohu a overenú obnovu s bezpečnostnou kópiou pred nahradením. Aktuálna schéma je 8. Obnova zatvorí aplikáciu; potom ju spusti znovu. Pozri [Záloha a obnova](BACKUP_RESTORE.md).

`tests/test_backup.py`, `tests/test_backup_review.py`, `soskuska/check_backup.py`.

```sh
.venv-macos/bin/python soskuska/check_backup.py
```

```powershell
.\.venv\Scripts\python.exe soskuska/check_backup.py
```

## Import otázok z CSV

Banka otázok teraz podporuje import UTF-8 CSV do existujúceho predmetu: šablóna s hlavičkou, stránkovaný náhľad, odmietnutie presných duplicít a jedno atomické uloženie. Maximum 2 MiB / 500 záznamov; zoznam ukazuje 50 otázok na stránku. Aktuálna schéma je 8. [Import otázok z CSV](QUESTION_CSV_IMPORT.md).

`tests/test_csv_import.py`, `soskuska/check_csv_import.py`.

```sh
.venv-macos/bin/python soskuska/check_csv_import.py
```

```powershell
.\.venv\Scripts\python.exe soskuska/check_csv_import.py
```

## Import kartičiek z CSV

Flashcards teraz podporuje import UTF-8 CSV do existujúceho balíčka: šablónu s hlavičkou, stránkovaný náhľad, odmietnutie presných duplicít a jedno atomické uloženie. Maximum 2 MiB / 500 záznamov. Nové kartičky sú ihneď splatné; pôvodné termíny a história hodnotení zostávajú zachované. Aktuálna schéma je 8. [Import kartičiek z CSV](FLASHCARD_CSV_IMPORT.md).

`tests/test_flashcard_csv_import.py`, `soskuska/check_flashcard_import.py`.

```sh
.venv-macos/bin/python soskuska/check_flashcard_import.py
```

```powershell
.\.venv\Scripts\python.exe soskuska/check_flashcard_import.py
```

## Uložené konverzácie AI Tutor

AI Tutor teraz ukladá konverzácie lokálne vrátane pôvodného servera/modelu a stavu odpovede. Históriu možno otvoriť bez siete, výslovne sa pripojiť na pokračovanie alebo vybranú konverzáciu po potvrdení zmazať. Vydané vo v0.12.0 so schémou 7, ktorá transakčne migruje pôvodné študijné údaje. [Uložené konverzácie AI Tutor](TUTOR_HISTORY.md).

`tests/test_tutor_history.py`, `soskuska/check_tutor_history.py`.

```sh
.venv-macos/bin/python soskuska/check_tutor_history.py
```

```powershell
.\.venv\Scripts\python.exe soskuska/check_tutor_history.py
```

## Jazyk rozhrania

Výber jazyka rozhrania je v tejto vetve implementovaný: angličtina, čeština, slovenčina a ruština. Ukladá sa osobitne od jazyka AI a použije sa po reštarte. Aktuálna schéma je 8; vydaná verzia zostáva v0.12.0 do schválenia vydania. [Jazyk rozhrania](UI_LANGUAGES.md).

`tests/test_localization.py`, `soskuska/check_ui_languages.py`.

```sh
.venv-macos/bin/python soskuska/check_ui_languages.py
```

```powershell
.\.venv\Scripts\python.exe soskuska/check_ui_languages.py
```
