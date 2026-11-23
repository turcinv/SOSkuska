# Kontrolný zoznam odovzdania semestrálneho projektu

[English](../SEMESTER_CHECKLIST.md) · [Čeština](../cs/SEMESTER_CHECKLIST.md) · [Slovenčina](SEMESTER_CHECKLIST.md) · [Русский](../ru/SEMESTER_CHECKLIST.md)

Pripravené **23. novembra 2026** pre **SOSkúška v0.18.1**, commit `f358804f99ce0133d137b035b16bd897b3761142`, schéma 10. Ide o plán odovzdania, nie hotovú prácu ani potvrdenie splnenia zadania. Na písanie použi [osnovu práce](REPORT_OUTLINE.md).

## Zdroj zadania a výklad

**S1:** používateľom dodané `Pokyny pre vypracovanie semestralneho projektu.pdf`, 10 strán PDF. SHA-256: `06aaa6f075665e39cfc9dea855ffd4f1a27f8c854254f8a1b19125db0081fc9a`. Pri overení sa zhodoval súbor v zdrojoch projektu ChatGPT s pôvodným dodaným súborom. PDF zostáva mimo Git repozitára; uchovaj originál medzi podkladmi predmetu. Čísla nižšie označujú **fyzické strany PDF**, nie vytlačené čísla príloh 12 a 18–23.

S1 určuje dokument, formátovanie a odovzdanie. Nepredpisuje Python, SQLite, AI, zoznam funkcií aplikácie, počet testov ani hodnotiacu rubriku softvéru. Mapovanie funkcií je návrh obsahu práce, nie zoznam požiadaviek vyučujúceho. Potvrď prijatie témy SOSkúška a prípadnú ďalšiu rubriku predmetu.

Stav **Čaká** znamená chýbajúci výsledný dôkaz alebo dokument; **Čiastočne** znamená dostupné podklady, ale neoverenú výslednú prácu. Úspešné testy aplikácie nesplnia formálne požiadavky na dokument.

## Formálne požiadavky

| ID | Strana S1 | Požiadavka | Stav | Dôkaz / ďalší krok |
| --- | --- | --- | --- | --- |
| DOC-01 | 1 | Vypracovať vo Worde, Writeri alebo plnohodnotnom editore; odovzdať upraviteľný súbor. | Čaká | Vytvoriť konečný `.docx`; Markdown v repozitári je iba príprava. |
| DOC-02 | 1 | Aspoň 10 strán bez titulnej strany, obsahu a literatúry. | Čaká | Cieľ je 11 strán hlavného textu; konzervatívne nepočítať ani zoznamy obrázkov/tabuliek a prílohy. Overiť výsledné strany. |
| DOC-03 | 1, 4 | Titulný list s témou a menom študenta; použiť vzor obalu. | Čaká | Potvrdiť študenta, školu, fakultu a rok; nastaviť samostatný obal. |
| DOC-04 | 1 | Vygenerovaný obsah. | Čaká | Použiť štýly nadpisov, automatický obsah a aktualizovať polia po zalomení strán. |
| DOC-05 | 1–2 | Vygenerované zoznamy obrázkov a tabuliek. | Čaká | Použiť skutočné polia popisov a generovať zoznamy; ručný zoznam nestačí. |
| DOC-06 | 1 | Úvod, hlavné kapitoly a podkapitoly. | Čiastočne | Podklady existujú v návodoch; napísať súvislú prácu podľa kapitol 1–7 osnovy. |
| DOC-07 | 1, 5–10 | Literatúra a citácie podľa dodaných príkladov. | Čaká | Vybrať skutočne použité zdroje; pozri citačné rozhodnutia nižšie. |
| DOC-08 | 2 | Formátovanie základných odsekov. | Čaká | V konečnom editore použiť špecifikáciu nižšie. |
| DOC-09 | 2 | Hierarchia nadpisov, arabské číslovanie a nová strana hlavnej kapitoly. | Čaká | Použiť úrovne 1–3, viacúrovňové číslovanie a overiť zlomy strán. |
| DOC-10 | 2 | Zarovnanie a popisy obrázkov/tabuliek/grafov; odsadené odrážky. | Čaká | Vložiť podklady so štýlmi popisov; overiť umiestnenie a zoznamy. |
| DOC-11 | 3 | Okraje a vzdialenosti záhlavia/zápätia; osobitné okraje obalu. | Čaká | Oddeliť obal a hlavný dokument sekciami, skontrolovať všetky strany. |
| DOC-12 | 3 | Čísla strán dole vpravo alebo v strede, Times New Roman 12 pt. | Čaká | Vložiť automatické polia; potvrdiť začiatok viditeľného číslovania. |
| DOC-13 | 1 | Názov `Priezvisko_Meno_kruzok_cislo.doc` alebo `.docx`; iný formát editora je dovolený. | Čaká | Pred pomenovaním potvrdiť meno a identifikátory krúžku. |
| DOC-14 | 1 | Odovzdať ku skúške v Moodle, sekcia `Semestrálny projekt a prezentácia`. | Čaká | Potvrdiť termín/prístup, nahrať súbor a uchovať potvrdenie. S1 povoľuje e-mail vyučujúcemu pri zlyhaní Moodle. Táto úloha nič neposiela. |
| DOC-15 | 1 | Prezentovať projekt na skúške. | Čaká | Nacvičiť ukážku; potvrdiť dĺžku a formát prezentácie. |

## Štýly výsledného dokumentu

Ide o pravidlá S1, nie štýly už aplikované na Markdown.

| Prvok | Nastavenia | Strana S1 |
| --- | --- | --- |
| Základný text | Times New Roman 12 pt; riadkovanie 1,5; do bloku; pred 6 pt, za 0 pt. Prvý odsek po nadpise bez odsadenia prvého riadka, ostatné 0,5 cm. | 2 |
| Nadpis 1 | Times New Roman 16 pt tučné, vľavo; riadkovanie 1,5; pred/za 6 pt; bez odsadenia; arabské čísla; nová strana. | 2 |
| Nadpis 2 | Times New Roman 14 pt tučné, vľavo; rovnaké riadkovanie a medzery; bez odsadenia; napr. 1.1. | 2 |
| Nadpis 3 | Times New Roman 12 pt tučné, vľavo; rovnaké riadkovanie a medzery; bez odsadenia; napr. 1.1.1. | 2 |
| Nadpis 4 | Times New Roman 12 pt obyčajné, vľavo; rovnaké medzery. S1 opakuje číslovanie 1.1.1; osnova sa tejto úrovni vyhýba namiesto tichej zmeny pravidla. | 2 |
| Obrázky | Na stred, pred 6 pt. Popis pod obrázkom, Times New Roman 11 pt, riadkovanie 1,5, pred/za 6 pt, bez odsadenia; `Obrázok 1 Názov`. | 2 |
| Tabuľky | Vľavo. Popis nad tabuľkou, Times New Roman 11 pt, riadkovanie 1,5, pred/za 6 pt, bez odsadenia; `Tabuľka 1`. | 2 |
| Grafy, ak sa použijú | Na stred, popis dole s rovnakým 11 pt štýlom; `Graf 1 Názov`. S1 vyžaduje zoznam obrázkov/tabuliek, nie samostatný zoznam grafov. | 2 |
| Odrážky | Odsadenie zľava 0,5 cm. | 2 |
| Hlavné strany | Hore/dole 2,5 cm; vľavo 3,5 cm; vpravo 2 cm; záhlavie/zápätie 1,25 cm. | 3 |
| Obal | Všetky okraje 2,5 cm; upraviť vzor zo strany 4 po potvrdení školy/fakulty. | 3–4 |
| Čísla strán | Dole vpravo alebo v strede, Times New Roman 12 pt; S1 neurčuje prvé zobrazované číslo. | 3 |

S1 najprv uvádza text bez odsadenia a potom konkrétne pravidlo 0,5 cm okrem odseku po nadpise; tabuľka používa toto konkrétnejšie pravidlo. Iný výklad potvrď s vyučujúcim. Pri inom jazyku konečnej práce potvrď aj jazyk popisov.

## Podklady aplikácie pre prácu

Každý riadok znamená **implementované vo v0.18.1; text a obrázky práce ešte čakajú**. Ide o voľby projektu, nie ďalšie požiadavky S1.

| Oblasť | Dostupný dôkaz | Použitie |
| --- | --- | --- |
| Predmety a otázky | [Architektúra](CURRENT_ARCHITECTURE.md), `subjects.py`, `question_bank.py`, `tests/test_subjects.py`, `tests/test_questions.py` | CRUD, validácia, vlastníctvo tém a ochrana zastaraných zmien. |
| Testy a kartičky | [História testov](PRACTICE_HISTORY.md), [Kartičky](FLASHCARDS.md), `practice.py`, `repetition.py` a testy | Uložené pokusy, nemenné odpovede a plánovanie podľa vlastného hodnotenia. |
| Sústredenie a štatistiky | [Obnova sústredenia](FOCUS_RECOVERY.md), [Štatistiky](STATISTICS.md), `focus.py`, `study_statistics.py` | Monotónny čas, kontrolné body, pozastavená obnova a súhrny; nie meranie zvládnutia učiva. |
| Voliteľný AI Tutor | [Tutor](AI_TUTOR.md), [Konverzácie](TUTOR_HISTORY.md), `ollama_client.py` a testy | Výslovné pripojenie, streamovanie/Stop, miestna história a offline štúdium; oddeliť protokol od kvality modelu. |
| Nastavenia a rozhranie | [Nastavenia](SETTINGS.md), [Jazyky](UI_LANGUAGES.md), [Vzhľad](APPEARANCE.md) | Štyri jazyky rozhrania, nezávislý jazyk odpovedí a uložený vzhľad. |
| Ochrana a prenos dát | [Obnova](BACKUP_RESTORE.md), [Plánované zálohy](SCHEDULED_BACKUPS.md), [CSV otázok](QUESTION_CSV_IMPORT.md), [CSV kartičiek](FLASHCARD_CSV_IMPORT.md) | Atomický import/obnova, samostatné kópie a miestny súhlas so zálohami. |
| Distribúcia a kvalita | [Windows](WINDOWS_PORTABLE.md), [Kontajner](CONTAINER_TESTS.md), [Vyriešené nálezy](REVIEW_FINDINGS.md) | Balík, päť úloh CI, regresné kontroly a platformové obmedzenia. |

## Hranice dôkazov a zostávajúca práca

- **Dostupné:** uvedený commit v0.18.1, [vydanie](https://github.com/turcinv/SOSkuska/releases/tag/v0.18.1) a [úspešné CI](https://github.com/turcinv/SOSkuska/actions/runs/45065149649). Zaznamenané overenie implementácie: 306 testov, dve platformové preskočenia a 18 Linux/Xvfb GUI skriptov. Táto dokumentačná úloha tento historický beh neopakuje ani neoznačuje novým dátumom.
- **Dostupné:** JSON kontroly balíka Windows a ZIP/kontrolný súčet. Hostované kontroly nenahrádzajú čistý počítač, mierku displeja ani hardvér.
- **Čaká:** [ručná kontrola Windows](WINDOWS_ACCEPTANCE.md) s OS, hardvérom, mierkou, verziou/hashom, dátumom a výsledkami. Staršie potvrdenie v0.15.0 nie je položkovým dôkazom pre v0.18.1.
- **Čaká:** skutočný model Ollama s verziou, hardvérom, serverom, dátumom a výsledkami. Falošný server neoveruje kvalitu odpovedí ani výkon reálneho modelu.
- **Čaká:** upraviteľná práca, reálne snímky a polia popisov, vygenerované zoznamy, zdroje, prezentácia a potvrdenie Moodle. Diagramy Mermaid sú podklady, nie obrázky už vložené do práce.

## Citácie a údaje na potvrdenie

S1 na stranách 5–10 uvádza príklady autor–rok/harvardského systému podľa ISO 690. Použi ich jednotne; plán netvrdí, ktoré vydanie normy je dnes záväzné. Zaznamenaj autora/organizáciu, názov, skutočný rok/vydanie, vydavateľa/identifikátory a pri online zdroji URL/dátum prístupu. Nekopíruj nesúvisiacu vzorovú literatúru. Strana 1 spomína knižné/internetové zdroje: plánuj obe kategórie, ak ich skutočne použiješ, alebo potvrď očakávanie; citáciu knihy nevymýšľaj.

Čakajú: celé meno študenta, škola/fakulta/predmet, krúžok a údaje názvu súboru, skúška/termín, schválená téma/ďalšia rubrika, jazyk práce a dĺžka/formát prezentácie. Účet repozitára neurčuje identitu študenta. S1 neuvádza presný termín ani čas prezentácie.

## Poradie dokončenia

1. Potvrdiť údaje a tému/rubriku, vybrať skutočné zdroje.
2. Vytvoriť upraviteľnú prácu so štýlmi, automatickými poľami a [11-stranovou osnovou](REPORT_OUTLINE.md).
3. Zachytiť obrázky s dočasnými dátami, doplniť dôkazy a skutočné ručné/modelové kontroly.
4. Aktualizovať polia, skontrolovať vykreslené strany, počet a názov súboru, nacvičiť a odovzdať požadovaným spôsobom. Publikovanie tohto PR nie je odovzdaním semestrálnej práce.
