# Osnova semestrální práce

[English](../REPORT_OUTLINE.md) · [Čeština](REPORT_OUTLINE.md) · [Slovenčina](../sk/REPORT_OUTLINE.md) · [Русский](../ru/REPORT_OUTLINE.md)

Návrh z **23. listopadu 2026**, základ **SOSkúška v0.18.1**, schéma 10. Navržené téma: **SOSkúška: návrh a implementace lokálního studijního asistenta**. Schválení tématu, jazyk práce a údaje studenta/předmětu čekají na potvrzení. Nejde o výsledný dokument Word. [Kontrolní seznam](SEMESTER_CHECKLIST.md) uvádí zdroj zadání, formátování a otevřené body.

## Úvodní části a rozsah

Vytvoř obal/titulní stranu podle vzoru, automatický obsah a vygenerované seznamy obrázků/tabulek. Použij skutečné styly nadpisů a pole popisků. Úvodní části, literaturu a přílohy konzervativně nepočítej do hlavního textu.

| Hlavní kapitola | Cíl stran | Účel |
| --- | --- | --- |
| 1 Úvod | 1 | Problém studia, uživatel a cíl projektu. |
| 2 Cíle a rozsah | 1 | Oddělit zadání, zvolené funkce a hranice. |
| 3 Výběr technologií | 1 | Python, CustomTkinter, SQLite, volitelná Ollama a kompromisy. |
| 4 Architektura a data | 2 | Toky, úložiště, historické snímky a migrace. |
| 5 Implementace | 3 | Reprezentativní postupy a chyby/opakování. |
| 6 Ověření a vyhodnocení | 2 | Skutečné důkazy, ruční mezery, opravy a omezení. |
| 7 Závěr a další rozvoj | 1 | Zhodnotit cíle a priority. |
| **Hlavní text celkem** | **11** | Pouze plán; skutečné zalomení ověřit vůči minimu 10 stran. |

Každá hlavní kapitola začíná na nové straně. Nadpisy úrovní 1–3 čísluj arabsky víceúrovňově. Existující návod v repozitáři není napsaná kapitola práce.

## Obsah kapitol a podklady

### 1 Úvod

Vysvětli organizování vlastních předmětů, otázek a přípravy. Cílem je místní desktopový asistent s volitelnou AI. Urči uživatele a offline použití. Bez důkazů netvrď zlepšení známek, ověřenou účinnost učení ani změřené zvládnutí učiva.

### 2 Cíle a rozsah

- **2.1 Zadání a volby projektu:** S1 vyžaduje formátovanou práci a prezentaci, nikoli konkrétní technologie/funkce. Uvést schválení tématu a případnou další rubriku.
- **2.2 Funkce:** předměty/otázky, testy, kartičky, soustředění/statistiky, nastavení, zálohy/import a volitelný Tutor; použít [mapování důkazů](SEMESTER_CHECKLIST.md).
- **2.3 Hranice:** místní data bez povinného účtu/cloudu, bez instalátoru/synchronizace, vlastní pravidla opakování, textová AI a čekající ruční kontroly. Oddělit implementaci od [plánů](PLANNED_ARCHITECTURE.md).

### 3 Výběr technologií

Vysvětli roli a kompromis každé technologie: nativní GUI a platformní chování Tk; transakční SQLite a zámky; volitelné HTTP/HTTPS Ollama, zastavení a výstup závislý na modelu. Cituj použité zdroje. Kapitola analyzuje rozhodnutí; reprodukci instalace řeší [vývojový návod](DEVELOPMENT.md).

### 4 Architektura a data

- **4.1 Běh:** hlavní vlákno Tk obsluhuje widgety, krátké operace Store a síťové výsledky přes frontu. CSV/zálohy používají oddělené procesy s vlastními připojeními a souborovým výstupem. Síťová vlákna nepoužívají Tk/SQLite; souborové procesy SQLite používají. Ověřit a použít diagramy [aktuální architektury](CURRENT_ARCHITECTURE.md).
- **4.2 Úložiště:** schéma 10, transakční migrace, předměty/témata/otázky, neměnné snímky testů/hodnocení/chatu, mazání a nastavení. Vysvětlit zachování historických jmen/odpovědí. Ukázat vybrané vztahy, nikoli celý SQL výpis.
- **4.3 Spolehlivost:** atomické zápisy, porovnání původního obsahu, opakování čtení bez opakování potvrzeného zápisu, vlastnictví soustředění a místní plán záloh. Oddělit SQLite od `<database>.backup-plan.json`, který není součástí exportu databáze.

### 5 Implementace

- **5.1 Tvorba obsahu:** Unicode předmět/téma/otázka, čtyři různé odpovědi, filtry, bezpečné úpravy/mazání; zahrnout zachované koncepty a [opravy revize](REVIEW_FINDINGS.md).
- **5.2 Testy a kartičky:** uložené odpovědi, časované pokračování, neměnné výsledky, odhalení před hodnocením, vlastní plánování a historie. Algoritmus neoznačovat SM-2 ani FSRS.
- **5.3 Soustředění a přehledy:** monotónní čas, pozastavená obnova bez započítání přestávky, idempotentní dokončení a den uložení. Dělení přes půlnoc není implementováno.
- **5.4 Volitelný Tutor:** Connect/Send, modely, streamování/Stop a uložené konverzace; omezený kontext a neověřované odpovědi.
- **5.5 Nastavení a data:** nezávislé jazyky rozhraní/AI, vzhled, CSV náhled/atomický import, ruční obnova/bezpečnostní kopie a zapínané denní zálohy za běhu. Vysvětlit uchovávání a denní limit; vycházet ze skutečných návodů funkcí.

### 6 Ověření a vyhodnocení

- **6.1 Reprodukce:** verze, commit, schéma, OS/Tk/prostředí a příkaz; dočasná data a [kontejner](CONTAINER_TESTS.md).
- **6.2 Automatické důkazy:** zaznamenaných 306 testů/18 GUI a [CI vydání](https://github.com/turcinv/SOSkuska/actions/runs/45065149649). Vysvětlit dvě přeskočení a pět úloh; odlišit Linux GUI, testy na třech OS a hostovaný balík Windows.
- **6.3 Případ revize:** A62-01 až A62-04, spouštěč, oprava a regresní důkaz. Testy dokazují pokryté případy, nikoli nepřítomnost všech chyb.
- **6.4 Otevřené ověření:** doplnit skutečné výsledky [Windows](WINDOWS_ACCEPTANCE.md) a Ollama. Do té doby zůstávají neověřené; falešný server nehodnotí kvalitu modelu.

### 7 Závěr a další rozvoj

Porovnej výsledek s cíli, uveď limity a priority: důkazy/práce/přejímka, potom vybraný rozvoj. Budoucí architekturu, pokročilé statistiky, export ani instalátor neuváděj jako hotové. Zahrň údržbu a testování.

## Plánované obrázky a tabulky

ID označují podklady, nikoli konečná čísla popisků. Vše **čeká na zachycení/export/vložení**. Použij dočasný obsah, zaznamenej verzi/datum/kontext a vlož pole popisků. S1 používá `Obrázok`, `Tabuľka`, `Graf`; pro jiný schválený jazyk potvrď popisky.

| Podklad | Obsah | Místo / důkaz |
| --- | --- | --- |
| F-01 | Skutečný tok běhu/dat včetně souborových procesů | Kapitola 4; ověřit Mermaid a exportovat. |
| F-02 | Vybrané vztahy schématu 10 a uchovaná historie | Kapitola 4; odvodit z `storage.py`, nikoli budoucího modelu. |
| F-03 | Editor předmětu/otázky s označenými dočasnými daty | Kapitola 5.1; snímek vydané aplikace. |
| F-04 | Výsledek testu nebo odhalená kartička s historií | Kapitola 5.2; uvést přesný postup a data. |
| F-05 | Pozastavená obnova nebo ovládání denních záloh | Kapitola 5.3/5.5; skutečná funkce. |
| T-01 | Cíle a mapování funkcí | Kapitola 2; oddělit S1 od rozsahu projektu. |
| T-02 | Ověřovací matice se skutečnými a neověřenými výsledky | Kapitola 6; OS/prostředí/verze a přeskočení. |
| T-03 | Čtyři nálezy Astra, opravy a kontroly | Kapitola 6.3; zachovaný záznam řešení. |

Snímky ani výsledky nevymýšlej. Graf je volitelný; použij uložená data, vysvětli jednotky/limity a dodrž styl popisku grafu. Seznamy musí odpovídat skutečně vloženým podkladům.

## Příprava literatury

Vyber a přečti zdroje technologií a studijního kontextu. Použij jednotné citace autor–rok, skutečné údaje a data online přístupu. Vzorová literatura PDF není seznam již použitých zdrojů aplikace. Potvrď očekávání knižních/internetových zdrojů; nevymýšlejí se zde autoři, roky ani ISBN.

## Návrh nácviku prezentace

S1 neurčuje čas ani počet snímků; návrh potvrď s vyučujícím.

1. Představit problém a prázdné/dočasné prostředí bez AI.
2. Vytvořit předmět/otázku, dokončit krátký test a ukázat historii; podle času kartičku a hodnocení.
3. Ukázat uložení/obnovu soustředění a nezapočítání času mimo aplikaci.
4. Předvést zálohu/obnovu na samostatné dočasné databázi. Obnova zavře aplikaci; nacvičit nový start a nepoužít běžná studijní data.
5. Tutor streamování/Stop předvést až po skutečném ověření modelu. Při nedostupnosti vysvětlit limit a pokračovat offline.
6. Vysvětlit architekturu, jednu opravu, důkazy a zbývající limity.

Nakonec aktualizuj obsah/seznamy/odkazy, zkontroluj popisky/okraje/čísla stran, alespoň 10 započítaných stran, potvrzený název souboru a uchovej potvrzení Moodle. PDF náhled může pomoci při kontrole; upravitelné odevzdání je ještě třeba vytvořit.
