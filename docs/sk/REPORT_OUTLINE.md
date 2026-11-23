# Osnova semestrálnej práce

[English](../REPORT_OUTLINE.md) · [Čeština](../cs/REPORT_OUTLINE.md) · [Slovenčina](REPORT_OUTLINE.md) · [Русский](../ru/REPORT_OUTLINE.md)

Návrh z **23. novembra 2026**, základ **SOSkúška v0.18.1**, schéma 10. Navrhovaná téma: **SOSkúška: návrh a implementácia lokálneho študijného asistenta**. Schválenie témy, jazyk práce a údaje študenta/predmetu čakajú na potvrdenie. Toto nie je výsledný dokument Word. [Kontrolný zoznam](SEMESTER_CHECKLIST.md) uvádza zdroj zadania, formátovanie a otvorené body.

## Úvodné časti a rozsah

Vytvor obal/titulnú stranu podľa vzoru, automatický obsah a vygenerované zoznamy obrázkov/tabuliek. Použi skutočné štýly nadpisov a polia popisov. Úvodné časti, literatúru a prílohy konzervatívne nezapočítavaj do hlavného textu.

| Hlavná kapitola | Cieľ strán | Účel |
| --- | --- | --- |
| 1 Úvod | 1 | Problém štúdia, používateľ a cieľ projektu. |
| 2 Ciele a rozsah | 1 | Oddeliť zadanie, zvolené funkcie a hranice. |
| 3 Výber technológií | 1 | Python, CustomTkinter, SQLite, voliteľná Ollama a kompromisy. |
| 4 Architektúra a dáta | 2 | Toky, úložisko, historické snímky a migrácie. |
| 5 Implementácia | 3 | Reprezentatívne postupy a chyby/opakovanie. |
| 6 Overenie a vyhodnotenie | 2 | Skutočné dôkazy, ručné medzery, opravy a obmedzenia. |
| 7 Záver a ďalší rozvoj | 1 | Zhodnotiť ciele a priority. |
| **Hlavný text spolu** | **11** | Iba plán; skutočné zalomenie overiť voči minimu 10 strán. |

Každá hlavná kapitola začína na novej strane. Nadpisy úrovní 1–3 čísluj arabsky viacúrovňovo. Existujúci návod v repozitári nie je napísaná kapitola práce.

## Obsah kapitol a podklady

### 1 Úvod

Vysvetli organizovanie vlastných predmetov, otázok a prípravy. Cieľom je lokálny desktopový asistent s voliteľnou AI. Urči používateľa a offline použitie. Bez dôkazov netvrď zlepšenie známok, overenú účinnosť učenia ani zmerané zvládnutie učiva.

### 2 Ciele a rozsah

- **2.1 Zadanie a voľby projektu:** S1 vyžaduje formátovanú prácu a prezentáciu, nie konkrétne technológie/funkcie. Uviesť schválenie témy a prípadnú ďalšiu rubriku.
- **2.2 Funkcie:** predmety/otázky, testy, kartičky, sústredenie/štatistiky, nastavenia, zálohy/import a voliteľný Tutor; použiť [mapovanie dôkazov](SEMESTER_CHECKLIST.md).
- **2.3 Hranice:** miestne dáta bez povinného účtu/cloudu, bez inštalátora/synchronizácie, vlastné pravidlá opakovania, textová AI a čakajúce ručné kontroly. Oddeliť implementáciu od [plánov](PLANNED_ARCHITECTURE.md).

### 3 Výber technológií

Vysvetli úlohu a kompromis každej technológie: natívne GUI a platformové správanie Tk; transakčné SQLite a zámky; voliteľné HTTP/HTTPS Ollama, zastavenie a výstup závislý od modelu. Cituj použité zdroje. Kapitola je analýza rozhodnutí; reprodukciu inštalácie rieši [vývojový návod](DEVELOPMENT.md).

### 4 Architektúra a dáta

- **4.1 Beh:** hlavné vlákno Tk obsluhuje widgety, krátke operácie Store a výsledky siete cez front. CSV/zálohy používajú izolované procesy s vlastnými pripojeniami a súborovým výstupom. Sieťové vlákna nepoužívajú Tk/SQLite; súborové procesy SQLite používajú. Overiť a použiť diagramy [aktuálnej architektúry](CURRENT_ARCHITECTURE.md).
- **4.2 Úložisko:** schéma 10, transakčné migrácie, predmety/témy/otázky, nemenné snímky testov/hodnotení/chatu, mazanie a nastavenia. Vysvetli zachovanie historických mien/odpovedí. Ukázať vybrané vzťahy, nie celý SQL výpis.
- **4.3 Spoľahlivosť:** atomické zápisy, porovnanie pôvodného obsahu, opakovanie čítania bez opakovania potvrdeného zápisu, vlastníctvo sústredenia a miestny plán záloh. Oddeliť SQLite od `<database>.backup-plan.json`, ktorý nie je súčasťou exportu databázy.

### 5 Implementácia

- **5.1 Tvorba obsahu:** Unicode predmet/téma/otázka, štyri rôzne odpovede, filtre a bezpečné úpravy/mazanie; zahrnúť zachované koncepty a [opravy revízie](REVIEW_FINDINGS.md).
- **5.2 Testy a kartičky:** uložené odpovede, časované pokračovanie, nemenné výsledky, odhalenie pred hodnotením, vlastné plánovanie a história. Algoritmus neoznačovať SM-2 ani FSRS.
- **5.3 Sústredenie a prehľady:** monotónny čas, pozastavená obnova bez započítania prestávky, idempotentné dokončenie a deň uloženia. Delenie cez polnoc nie je implementované.
- **5.4 Voliteľný Tutor:** Connect/Send, modely, streamovanie/Stop a uložené konverzácie; ohraničený kontext a neoverované odpovede.
- **5.5 Nastavenia a dáta:** nezávislé jazyky rozhrania/AI, vzhľad, CSV náhľad/atomický import, ručná obnova/bezpečnostná kópia a zapínané denné zálohy za behu. Vysvetli uchovávanie a denný limit; používať skutočné návody funkcií.

### 6 Overenie a vyhodnotenie

- **6.1 Reprodukcia:** verzia, commit, schéma, OS/Tk/prostredie a príkaz; dočasné dáta a [kontajner](CONTAINER_TESTS.md).
- **6.2 Automatické dôkazy:** zaznamenané 306 testov/18 GUI a [CI vydania](https://github.com/turcinv/SOSkuska/actions/runs/45065149649). Vysvetli dve preskočenia a päť úloh; odlíšiť Linux GUI, testy na troch OS a hostovaný balík Windows.
- **6.3 Prípad revízie:** A62-01 až A62-04, spúšťač, oprava a regresný dôkaz. Testy dokazujú pokryté prípady, nie neprítomnosť všetkých chýb.
- **6.4 Otvorené overenie:** doplniť skutočné výsledky [Windows](WINDOWS_ACCEPTANCE.md) a Ollama. Dovtedy zostávajú neoverené; falošný server nehodnotí kvalitu modelu.

### 7 Záver a ďalší rozvoj

Porovnaj výsledok s cieľmi, uveď limity a priority: dôkazy/práca/akceptačné overenie, potom vybraný rozvoj. Budúcu architektúru, pokročilé štatistiky, export ani inštalátor neuvádzaj ako hotové. Zahrň údržbu a testovanie.

## Plánované obrázky a tabuľky

ID sú označenia podkladov, nie konečné čísla popisov. Všetko **čaká na zachytenie/export/vloženie**. Použi dočasný obsah, zaznamenaj verziu/dátum/kontext a vlož polia popisov. S1 používa `Obrázok`, `Tabuľka`, `Graf`; pri inom schválenom jazyku potvrď popisky.

| Podklad | Obsah | Miesto / dôkaz |
| --- | --- | --- |
| F-01 | Skutočný tok behu/dát vrátane súborových procesov | Kapitola 4; overiť Mermaid a exportovať. |
| F-02 | Vybrané vzťahy schémy 10 a uchovaná história | Kapitola 4; odvodiť z `storage.py`, nie budúceho modelu. |
| F-03 | Editor predmetu/otázky s označenými dočasnými dátami | Kapitola 5.1; snímka vydanej aplikácie. |
| F-04 | Výsledok testu alebo odhalená kartička s históriou | Kapitola 5.2; uviesť presný postup a dáta. |
| F-05 | Pozastavená obnova alebo ovládanie denných záloh | Kapitola 5.3/5.5; reálna funkcia. |
| T-01 | Ciele a mapovanie funkcií | Kapitola 2; oddeliť S1 od rozsahu projektu. |
| T-02 | Overovacia matica so skutočnými a neoverenými výsledkami | Kapitola 6; OS/prostredie/verzia a preskočenia. |
| T-03 | Štyri nálezy Astra, opravy a kontroly | Kapitola 6.3; zachovaný záznam riešenia. |

Snímky ani výsledky nevymýšľaj. Graf je voliteľný; pri použití vychádzaj z uložených dát, vysvetli jednotky/limity a dodrž štýl popisu grafu. Zoznamy musia zodpovedať skutočne vloženým podkladom.

## Príprava literatúry

Vyber a prečítaj zdroje technológií a študijného kontextu. Použi jednotné citácie autor–rok, skutočné údaje a dátumy online prístupu. Vzorová literatúra PDF nie je zoznam už použitých zdrojov aplikácie. Potvrď očakávanie knižných/internetových zdrojov; nevymýšľajú sa tu autori, roky ani ISBN.

## Návrh nácviku prezentácie

S1 neurčuje čas ani počet snímok; návrh treba potvrdiť s vyučujúcim.

1. Predstaviť problém a prázdne/dočasné prostredie bez AI.
2. Vytvoriť predmet/otázku, dokončiť krátky test a ukázať históriu; podľa času kartičku a hodnotenie.
3. Ukázať uloženie/obnovu sústredenia a nezapočítanie času mimo aplikácie.
4. Predviesť zálohu/obnovu na samostatnej dočasnej databáze. Obnova zavrie aplikáciu; nacvičiť nový štart a nepoužiť bežné študijné dáta.
5. Tutor streamovanie/Stop predviesť až po reálnom overení modelu. Pri nedostupnosti vysvetliť limit a pokračovať offline.
6. Vysvetliť architektúru, jednu opravu, dôkazy a zostávajúce limity.

Nakoniec aktualizuj obsah/zoznamy/odkazy, skontroluj popisy/okraje/čísla strán, aspoň 10 započítaných strán, potvrdený názov súboru a uchovaj potvrdenie Moodle. PDF náhľad môže pomôcť pri kontrole; upraviteľné odovzdanie ešte treba vytvoriť.
