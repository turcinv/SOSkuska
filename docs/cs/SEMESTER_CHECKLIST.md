# Kontrolní seznam odevzdání semestrálního projektu

[English](../SEMESTER_CHECKLIST.md) · [Čeština](SEMESTER_CHECKLIST.md) · [Slovenčina](../sk/SEMESTER_CHECKLIST.md) · [Русский](../ru/SEMESTER_CHECKLIST.md)

Připraveno **23. listopadu 2026** pro **SOSkúška v0.18.1**, commit `f358804f99ce0133d137b035b16bd897b3761142`, schéma 10. Jde o plán odevzdání, nikoli hotovou práci nebo potvrzení splnění zadání. Pro psaní použij [osnovu práce](REPORT_OUTLINE.md).

## Zdroj zadání a výklad

**S1:** uživatelem dodané `Pokyny pre vypracovanie semestralneho projektu.pdf`, 10 stran PDF. SHA-256: `06aaa6f075665e39cfc9dea855ffd4f1a27f8c854254f8a1b19125db0081fc9a`. Při ověření se shodoval soubor ve zdrojích projektu ChatGPT s původním souborem. PDF zůstává mimo Git repozitář; originál uchovej mezi podklady předmětu. Čísla níže označují **fyzické strany PDF**, nikoli vytištěná čísla příloh 12 a 18–23.

S1 určuje dokument, formátování a odevzdání. Nepředepisuje Python, SQLite, AI, seznam funkcí aplikace, počet testů ani hodnoticí rubriku softwaru. Mapování funkcí je návrh obsahu práce, nikoli požadavky vyučujícího. Potvrď přijetí tématu SOSkúška a případnou další rubriku předmětu.

**Čeká** znamená chybějící konečný důkaz/dokument; **Částečně** znamená dostupné podklady, ale neověřenou výslednou práci. Úspěšné testy aplikace neplní formální požadavky na dokument.

## Formální požadavky

| ID | Strana S1 | Požadavek | Stav | Důkaz / další krok |
| --- | --- | --- | --- | --- |
| DOC-01 | 1 | Práce ve Wordu, Writeru nebo plnohodnotném editoru; upravitelný soubor. | Čeká | Vytvořit konečný `.docx`; Markdown je pouze příprava. |
| DOC-02 | 1 | Alespoň 10 stran bez titulní strany, obsahu a literatury. | Čeká | Cíl 11 stran hlavního textu; konzervativně nepočítat ani seznamy obrázků/tabulek a přílohy. Ověřit výsledné strany. |
| DOC-03 | 1, 4 | Titulní list s tématem a jménem studenta; vzor obalu. | Čeká | Potvrdit studenta, školu, fakultu a rok; nastavit samostatný obal. |
| DOC-04 | 1 | Vygenerovaný obsah. | Čeká | Použít styly nadpisů, automatický obsah a aktualizovat pole po zalomení. |
| DOC-05 | 1–2 | Vygenerované seznamy obrázků a tabulek. | Čeká | Vložit skutečná pole popisků a generovat seznamy; ruční seznam nestačí. |
| DOC-06 | 1 | Úvod, hlavní kapitoly a podkapitoly. | Částečně | Návody jsou podkladem; napsat souvislou práci podle kapitol 1–7 osnovy. |
| DOC-07 | 1, 5–10 | Literatura a citace podle dodaných příkladů. | Čeká | Vybrat skutečně použité zdroje; viz citační rozhodnutí níže. |
| DOC-08 | 2 | Formátování základních odstavců. | Čeká | Použít specifikaci níže v konečném editoru. |
| DOC-09 | 2 | Hierarchie nadpisů, arabské číslování, nová strana hlavní kapitoly. | Čeká | Úrovně 1–3, víceúrovňové číslování a kontrola zlomů stran. |
| DOC-10 | 2 | Zarovnání a popisky obrázků/tabulek/grafů; odsazené odrážky. | Čeká | Vložit podklady se styly popisků, zkontrolovat umístění a seznamy. |
| DOC-11 | 3 | Okraje, vzdálenosti záhlaví/zápatí a zvláštní okraje obalu. | Čeká | Oddělit obal a hlavní text oddíly, zkontrolovat všechny strany. |
| DOC-12 | 3 | Čísla stran dole vpravo nebo uprostřed, Times New Roman 12 pt. | Čeká | Automatická pole; potvrdit počátek viditelného číslování. |
| DOC-13 | 1 | Název `Priezvisko_Meno_kruzok_cislo.doc` nebo `.docx`; jiný formát editoru je povolen. | Čeká | Před pojmenováním potvrdit jméno a identifikátory skupiny. |
| DOC-14 | 1 | Odevzdat ke zkoušce v Moodle, sekce `Semestrálny projekt a prezentácia`. | Čeká | Potvrdit termín/přístup, nahrát soubor a uchovat potvrzení. S1 při selhání Moodle uvádí e-mail vyučujícímu. Tato úloha nic neposílá. |
| DOC-15 | 1 | Prezentace projektu na zkoušce. | Čeká | Nacvičit ukázku, potvrdit délku a formát prezentace. |

## Styly výsledného dokumentu

Jde o pravidla S1, nikoli styly už aplikované na Markdown.

| Prvek | Nastavení | Strana S1 |
| --- | --- | --- |
| Základní text | Times New Roman 12 pt; řádkování 1,5; do bloku; před 6 pt, za 0 pt. První odstavec po nadpisu bez odsazení prvního řádku, ostatní 0,5 cm. | 2 |
| Nadpis 1 | Times New Roman 16 pt tučné, vlevo; řádkování 1,5; před/za 6 pt; bez odsazení; arabská čísla; nová strana. | 2 |
| Nadpis 2 | Times New Roman 14 pt tučné, vlevo; stejné řádkování a mezery; bez odsazení; např. 1.1. | 2 |
| Nadpis 3 | Times New Roman 12 pt tučné, vlevo; stejné řádkování a mezery; bez odsazení; např. 1.1.1. | 2 |
| Nadpis 4 | Times New Roman 12 pt obyčejné, vlevo; stejné mezery. S1 opakuje 1.1.1; osnova se této úrovni vyhýbá místo tiché změny pravidla. | 2 |
| Obrázky | Na střed, před 6 pt. Popisek dole, Times New Roman 11 pt, řádkování 1,5, před/za 6 pt, bez odsazení; příklad `Obrázok 1 Názov`. | 2 |
| Tabulky | Vlevo. Popisek nahoře, Times New Roman 11 pt, řádkování 1,5, před/za 6 pt, bez odsazení; `Tabuľka 1`. | 2 |
| Grafy, pokud budou | Na střed, popisek dole stejným 11 pt stylem; `Graf 1 Názov`. S1 vyžaduje seznam obrázků/tabulek, nikoli zvláštní seznam grafů. | 2 |
| Odrážky | Odsazení zleva 0,5 cm. | 2 |
| Hlavní strany | Nahoře/dole 2,5 cm; vlevo 3,5 cm; vpravo 2 cm; záhlaví/zápatí 1,25 cm. | 3 |
| Obal | Všechny okraje 2,5 cm; upravit vzor ze strany 4 po potvrzení školy/fakulty. | 3–4 |
| Čísla stran | Dole vpravo nebo uprostřed, Times New Roman 12 pt; S1 neurčuje první zobrazované číslo. | 3 |

S1 nejprve uvádí text bez odsazení a potom konkrétní pravidlo 0,5 cm kromě odstavce po nadpisu; tabulka používá konkrétnější pravidlo. Jiný výklad potvrď s vyučujícím. Pro jiný jazyk konečné práce potvrď i jazyk popisků.

## Podklady aplikace pro práci

Každý řádek znamená **implementováno ve v0.18.1; text a obrázky práce stále čekají**. Jde o volby projektu, nikoli další požadavky S1.

| Oblast | Dostupný důkaz | Použití |
| --- | --- | --- |
| Předměty a otázky | [Architektura](CURRENT_ARCHITECTURE.md), `subjects.py`, `question_bank.py`, `tests/test_subjects.py`, `tests/test_questions.py` | CRUD, validace, vlastnictví témat, ochrana zastaralých změn. |
| Testy a kartičky | [Historie testů](PRACTICE_HISTORY.md), [Kartičky](FLASHCARDS.md), `practice.py`, `repetition.py` a testy | Uložené pokusy, neměnné odpovědi, plánování podle vlastního hodnocení. |
| Soustředění a statistiky | [Obnova soustředění](FOCUS_RECOVERY.md), [Statistiky](STATISTICS.md), `focus.py`, `study_statistics.py` | Monotónní čas, kontrolní body, pozastavená obnova a souhrny; nikoli měření zvládnutí učiva. |
| Volitelný AI Tutor | [Tutor](AI_TUTOR.md), [Konverzace](TUTOR_HISTORY.md), `ollama_client.py` a testy | Výslovné připojení, streamování/Stop, místní historie a offline studium; oddělit protokol od kvality modelu. |
| Nastavení a rozhraní | [Nastavení](SETTINGS.md), [Jazyky](UI_LANGUAGES.md), [Vzhled](APPEARANCE.md) | Čtyři jazyky rozhraní, nezávislý jazyk odpovědí a uložený vzhled. |
| Ochrana a přenos dat | [Obnova](BACKUP_RESTORE.md), [Plánované zálohy](SCHEDULED_BACKUPS.md), [CSV otázek](QUESTION_CSV_IMPORT.md), [CSV kartiček](FLASHCARD_CSV_IMPORT.md) | Atomický import/obnova, samostatné kopie a místní souhlas se zálohami. |
| Distribuce a kvalita | [Windows](WINDOWS_PORTABLE.md), [Kontejner](CONTAINER_TESTS.md), [Vyřešené nálezy](REVIEW_FINDINGS.md) | Balík, pět úloh CI, regresní kontroly a platformní omezení. |

## Hranice důkazů a zbývající práce

- **Dostupné:** uvedený commit v0.18.1, [vydání](https://github.com/turcinv/SOSkuska/releases/tag/v0.18.1) a [úspěšné CI](https://github.com/turcinv/SOSkuska/actions/runs/45065149649). Zaznamenané ověření implementace: 306 testů, dvě platformní přeskočení a 18 Linux/Xvfb GUI skriptů. Tato dokumentační úloha historický běh neopakuje ani nepřeznačuje novým datem.
- **Dostupné:** JSON kontroly Windows a ZIP/kontrolní součet. Hostované kontroly nenahrazují čistý počítač, měřítko displeje ani hardware.
- **Čeká:** [ruční kontrola Windows](WINDOWS_ACCEPTANCE.md) s OS, hardwarem, měřítkem, verzí/hashem, datem a výsledky. Starší potvrzení v0.15.0 není položkovým důkazem pro v0.18.1.
- **Čeká:** skutečný model Ollama s verzí, hardwarem, serverem, datem a výsledky. Falešný server neověřuje kvalitu odpovědí ani výkon reálného modelu.
- **Čeká:** upravitelná práce, skutečné snímky a pole popisků, vygenerované seznamy, zdroje, prezentace a potvrzení Moodle. Diagramy Mermaid jsou podklady, nikoli obrázky už vložené do práce.

## Citace a údaje k potvrzení

S1 na stranách 5–10 uvádí příklady autor–rok/harvardského systému podle ISO 690. Použij je jednotně; plán netvrdí, které vydání normy je dnes závazné. Zaznamenej autora/organizaci, název, skutečný rok/vydání, vydavatele/identifikátory a u online zdroje URL/datum přístupu. Nekopíruj nesouvisející vzorovou literaturu. Strana 1 zmiňuje knižní/internetové zdroje: plánuj obě kategorie, pokud je skutečně použiješ, nebo potvrď očekávání; citaci knihy nevymýšlej.

Čekají: celé jméno studenta, škola/fakulta/předmět, skupina a údaje názvu souboru, zkouška/termín, schválené téma/další rubrika, jazyk práce a délka/formát prezentace. Účet repozitáře neurčuje identitu studenta. S1 neuvádí přesný termín ani čas prezentace.

## Pořadí dokončení

1. Potvrdit údaje a téma/rubriku, vybrat skutečné zdroje.
2. Vytvořit upravitelnou práci se styly, automatickými poli a [11stránkovou osnovou](REPORT_OUTLINE.md).
3. Zachytit obrázky s dočasnými daty, doplnit důkazy a skutečné ruční/modelové kontroly.
4. Aktualizovat pole, zkontrolovat vykreslené strany, počet a název souboru, nacvičit a odevzdat požadovanou cestou. Publikování tohoto PR není odevzdáním semestrální práce.
