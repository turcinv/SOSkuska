# Ako to funguje — jednoducho

SOSkuska je desktopová aplikácia. Python pomocou CustomTkinteru vytvorí okno a jeho ovládacie prvky. Prehliadač ani webový server na to nepotrebuješ. HTML v priečinku `soskuska-local/` je len samostatný návrh vzhľadu.

## Od spustenia k uloženým údajom

1. **Spustenie:** aplikácia vytvorí okno a otvorí miestnu SQLite databázu. Ak ešte neexistuje, založí ju.
2. **Zoznam úloh:** zaškrtneš úlohu a zmena sa ihneď uloží pre dnešný dátum. Po ďalšom spustení v rovnaký deň zostane zachovaná.
3. **Vyhľadávanie:** zadáš napríklad `Physics`. Aplikácia prefiltruje štyri ukážkové predmety v pamäti; nič neposiela na internet.
4. **Štúdium:** Start Studying aj Resume session spustia nový 15-minútový časovač. Môžeš ho pozastaviť a znovu spustiť.
5. **Dokončenie:** Finish uloží skutočne uplynulé sekundy. Po 15 minútach sa relácia dokončí automaticky. Bežné zatvorenie okna tiež uloží doterajší čas.

Časovač sa medzi spusteniami neobnovuje. Pri násilnom ukončení alebo páde môže rozpracovaný čas zmiznúť, pretože sa zatiaľ priebežne neukladá.

## Skutočné funkcie a ukážkové údaje

| Skutočne funguje | Zatiaľ iba ukážka |
| --- | --- |
| Denný zoznam úloh a jeho uloženie | Profil Alex Morgan |
| Meranie a uloženie študijného času | Séria dní štúdia, počet otázok a úspešnosť |
| Filtrovanie, posúvanie a zmena rozloženia | Predmety a percentá pokroku |
| Pauza a dokončenie časovača | Termíny skúšok a nedávna aktivita |

Prehľad začína na ukážkových **24 h 35 min celkovo** a **45 min dnes**. Skutočne uložený čas sa k týmto základom pripočítava. Ešte nejde o úplnú štatistiku tvojho štúdia.

Na Macu je databáza štandardne v `~/Library/Application Support/SOSkuska/dashboard.sqlite3`. Nikam sa automaticky nesynchronizuje. Aplikácia ju sama nešifruje.

## Čo príde neskôr

Pridáš vlastné predmety, otázky a kartičky. Precvičovanie začne zapisovať odpovede a prehľad bude počítať skutočný pokrok. AI Tutor sa pripojí k miestnej Ollame, ktorá prevádzkuje jazykový model. Bežné štúdium má zostať použiteľné aj bez AI.

To je budúci plán, nie dnešná funkcia. Ďalšie obrazovky v navigácii zatiaľ iba zobrazujú oznámenie o ich budúcej dostupnosti.


Kompatibilita s pôvodným názvom: ak nová databáza v `SOSkuska` neexistuje a pôvodná `ExamPrep/dashboard.sqlite3` existuje, aplikácia použije tento pôvodný súbor. Nič automaticky nekopíruje, nepresúva ani neprepisuje. Výslovné `--data` má vždy prednosť.
