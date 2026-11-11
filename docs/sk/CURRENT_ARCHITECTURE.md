# Súčasná architektúra

Stav k 11. novembru 2026. Implementované sú Dashboard a My Subjects; ďalšie kroky opisuje [plánovaná architektúra](PLANNED_ARCHITECTURE.md).

## Technológie a súbory

Python, CustomTkinter 5.2.2, Pillow a štandardná SQLite. Jeden proces a hlavné vlákno Tk; bez sieťových požiadaviek a klienta Ollama. Vstup je `python soskuska/app.py`; inštalovateľný balík zatiaľ nie je.

| Súbor | Zodpovednosť |
| --- | --- |
| `soskuska/app.py` | Dashboard, navigácia dvoch obrazoviek, metriky, časovač, výber databázy a CLI |
| `soskuska/subjects.py` | My Subjects, inline formulár, validácia a potvrdenie vymazania |
| `soskuska/storage.py` | Verzia schémy, migrácie, CRUD predmetov, úlohy, relácie a prehľady |
| `soskuska/scrolling.py` | Kompatibilita kolieska a trackpadu Tk 9 |
| `tests/test_storage.py`, `tests/test_subjects.py` | Úložisko, kompatibilita pôvodnej databázy, migrácie a pravidlá predmetov |
| `soskuska/check_dashboard.py` | Natívna integračná kontrola s dočasnými údajmi |
| `soskuska-local/index.html` | Historický vizuálny návrh; nie je súčasťou behu aplikácie |

## Tok údajov

```mermaid
flowchart LR
    User[Používateľ] --> Dashboard[Dashboard / app.py]
    User --> Subjects[SubjectPage / subjects.py]
    Subjects --> Store[Store / storage.py]
    Dashboard --> Store
    Store --> DB[(SQLite)]
    Clock[time.monotonic] --> Dashboard
```

Obe obrazovky volajú `Store` priamo. Samostatná servisná/doménová vrstva a spoločný modul motívu zostávajú plánované. `SubjectPage` využíva existujúce pomocné metódy aplikácie pre štýl.

## Schéma a migrácie

`PRAGMA user_version` teraz označuje verziu **2**. Otvorenie pôvodnej databázy verzie 0 vytvorí/rozpozná pôvodné tabuľky a v jednej transakcii doplní predmety a väzby. Databáza s novšou verziou sa odmietne otvoriť namiesto pokusu o downgrade. Cudzie kľúče sú zapnuté pre každé pripojenie.

```sql
CREATE TABLE tasks (
    day TEXT NOT NULL, name TEXT NOT NULL, done INTEGER NOT NULL,
    PRIMARY KEY (day, name)
);
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, name_key TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '', exam_date TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY, day TEXT NOT NULL,
    seconds INTEGER NOT NULL CHECK(seconds >= 0),
    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
    subject_name TEXT
);
CREATE INDEX sessions_subject ON sessions(subject_id);
```

Staré úlohy a relácie sa zachovajú. Pôvodné relácie nemajú vymyslený predmet: nové stĺpce sú `NULL`, UI ich označí ako Unassigned session. Pri vymazaní predmetu sa zachová čas aj názov predmetu uložený pri novej relácii; cudzí kľúč sa nastaví na `NULL`. ID predmetu sa znovu nepoužíva.

Názov predmetu má 1–120 znakov; medzery sa zjednotia, jedinečný kľúč používa Unicode NFKC a `casefold()`. Popis má najviac 1 000 znakov. Dátum je voliteľný, musí presne zodpovedať platnému `YYYY-MM-DD`. Minulý dátum možno uložiť, ale nezobrazí sa medzi nadchádzajúcimi skúškami.

## Ukladanie a časovač

| Platforma | Predvolená databáza |
| --- | --- |
| macOS | `~/Library/Application Support/SOSkuska/dashboard.sqlite3` |
| Windows | `%LOCALAPPDATA%\SOSkuska\dashboard.sqlite3`; náhradný základ `~/AppData/Local` |
| Linux | `$XDG_DATA_HOME/SOSkuska/dashboard.sqlite3`; náhradný základ `~/.local/share` |

Ak nová databáza nie je a existuje pôvodná `ExamPrep/dashboard.sqlite3`, použije sa pôvodný súbor bez presunu alebo prepisu. `--data` má prednosť. Údaje sa nešifrujú, nezálohujú ani nesynchronizujú. Zápisy bežia na hlavnom vlákne.

Časovač vyžaduje existujúci predmet. Počas relácie drží jeho ID a kópiu názvu; premenovanie nemení históriu. Má limit 900 sekúnd, meranie cez `time.monotonic()`, aktualizáciu cez `after(250, tick)`, pauzu a dokončenie. Mazanie aktívneho predmetu UI zablokuje do dokončenia relácie. Finish, dosiahnutie limitu a bežné zatvorenie ukladajú čas. Pri chybe zápisu sa relácia pozastaví a možno skúsiť Finish znovu; okno sa nezatvorí s neuloženou reláciou.

Čas nie je priebežne ukladaný a po páde sa nemusí obnoviť. Relácia sa pripisuje ku dňu uloženia a nerozdeľuje sa cez polnoc. Zmena dňa za behu obnoví prehľad a dnešný zoznam úloh. Nový zoznam používa kľúče `review_subject` a `focus`; staré riadky zostávajú v databáze, ale nie sú mapované na nové úlohy.

## Skutočný Dashboard

Pevné vzorové predmety, percentá, profil, termíny aj základy 24 h 35 min / 45 min boli odstránené. Nová databáza je prázdna. Metriky sú celkový čas, počet uložených relácií, séria študijných dní a počet predmetov. Séria môže končiť dnes alebo včera; staršia prerušená séria ukáže nulu. Cieľ zostáva 60 minút denne; karta ukazuje uložené minúty, pruh má presnosť na sekundy.

Karty ukazujú počet relácií a uložený čas predmetu, nie vymyslený pokrok v učení. Skúšky pochádzajú z uložených termínov, nedávna aktivita z posledných uložených relácií. Neexistujúce údaje majú prázdne stavy. AI, otázky, testy, kartičky, štatistická obrazovka a nastavenia zatiaľ nie sú implementované.

## Rozloženie a ovládanie

Okno 1440 × 900, minimum 1024 × 700. Bočný panel 230 px / zbalený 72 px; pri zvyšnej šírke pod 1100 px sa Dashboard usporiada na metriky 2 × 2 a pravý panel pod obsah. My Subjects prepína medzi jedným a dvoma stĺpcami pri šírke 850 px. Dlhé názvy sa na kartách zalamujú.

Obe obrazovky majú nezávislé vyhľadávanie cez `casefold()`. Ctrl+K / Cmd+K zameria hľadanie aktívnej obrazovky; Escape vymaže dotaz. Formuláre pre nový/upravený predmet aj potvrdenie vymazania sú inline. Podpora `TouchpadScroll`, kolieska a staršieho Linux/X11 zostáva v adaptéri využívajúcom súkromné členy CustomTkinteru; pri aktualizácii ho znovu overiť.

## Overenie a zostávajúce obmedzenia

17 testov úložiska prešlo; integračný skript prešiel na macOS s Pythonom 3.12.13 / Tk 9.0 a dočasnou databázou. Overil CRUD cez formulár, Unicode, hľadanie, prázdne stavy, naviazanie časovača, zachovanie histórie, opätovné otvorenie, kompaktný režim a syntetické posúvanie. Nenahrádza ručné vizuálne/hardvérové overenie; Windows/Linux nie sú overené.

Zostáva správa tém/otázok, testy, kartičky, Ollama, preklady UI, nastavovanie cieľa, úplná obnova po páde, zálohy, balíky a komplexné logovanie. Základné databázové operácie majú chybové hlásenia, ale úplné spracovanie chýb pri každom čítaní ešte chýba.


Verzia schémy sa číta až po získaní `BEGIN IMMEDIATE`, aby súbežné štarty nepoužili zastaranú hodnotu. Rozloženie My Subjects spracúva skutočné Configure udalosti CustomTkinteru; integračná kontrola overuje dva stĺpce vo veľkom okne a jeden v kompaktnom.
