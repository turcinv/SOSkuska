# Import otázok z CSV (v0.10.0)

[English](../QUESTION_CSV_IMPORT.md) · [Čeština](../cs/QUESTION_CSV_IMPORT.md) · [Slovenčina](QUESTION_CSV_IMPORT.md) · [Русский](../ru/QUESTION_CSV_IMPORT.md)

Nevydaný redizajn úprav združuje filtre a hľadanie do jednej plochy a ponecháva Import CSV v záhlaví banky. Vstup do importu, oddelenie náhľadu od konceptov a pravidlá ukladania a opakovania nižšie sa nemenia.

Otvor **My Subjects → Questions → Import CSV** pri existujúcom predmete. Súbor pridá otázky iba doňho; nevytvára predmet ani neupravuje existujúce otázky. Kartičky táto prvá verzia neimportuje.

## Príprava súboru

Použi **Save CSV template** alebo [šablónu iba s hlavičkou](../examples/questions-template.csv). Doplň vlastné riadky; šablóna nemá vzorové otázky a nikdy sa automaticky neimportuje. Ulož UTF-8 (voliteľne BOM), CSV oddelené čiarkami. Úvodzovky umožňujú čiarky a viac riadkov v bunke. Bodkočiarky, neznáme/duplicitné hlavičky a neplatné UTF-8 sa odmietnu. Maximum je **2 MiB a 500 neprázdnych záznamov**; väčší súbor rozdeľ. Prázdne záznamy sa ignorujú.

Povinné stĺpce: `prompt`, `option_a`, `option_b`, `option_c`, `option_d`, `correct_option`, `difficulty`. Voliteľné: `topic`, `explanation`. Poradie je ľubovoľné; veľkosť písmen a krajné medzery v hlavičke sa ignorujú. Správna odpoveď je **A, B, C alebo D**, nie číslo. Náročnosť je Easy, Medium alebo Hard; pri písmene odpovede aj náročnosti nezáleží na veľkosti písmen.

Platia bežné limity: text 1–2 000 znakov, štyri rôzne odpovede po 1–500, vysvetlenie najviac 2 000, téma najviac 120. Neplatné riadiace znaky sa odmietnu. Prázdna téma znamená No topic. Existujúca téma sa použije podľa normalizovaného názvu (medzery, Unicode NFKC a casefold); chýbajúca vznikne až pri uložení celej dávky.

## Náhľad a uloženie

1. **Choose CSV…** načíta súbor. Náhľad používa databázové spojenie iba na čítanie bez vytvárania súboru či migrácie; otázky ani témy neukladá.
2. Prečítaj chyby a cez Previous/Next skontroluj všetky platné otázky, možnosti, správnu odpoveď, náročnosť, vysvetlenie a tému. Platné riadky možno prezerať aj pri chybách, ale **akákoľvek chyba zablokuje Import all**. Čísla označujú CSV záznamy vrátane hlavičky, nie nutne fyzické riadky viacriadkových buniek; chyba syntaxe CSV môže uviesť fyzický riadok.
3. Presné duplicity sa odmietnu v súbore aj voči predmetu. Zhoda zahŕňa všetky normalizované polia otázky a názov témy. Iné vysvetlenie, náročnosť alebo téma znamená inú otázku. Existujúce otázky sa neprepisujú ani potichu nepreskakujú.
4. **Import all** potvrdzuje uloženie náhľadu. Použije sa súkromná kópia náhľadu aj po zmene pôvodného súboru; úpravy načítaš novým výberom. Identita/názov predmetu, duplicity a témy sa znovu kontrolujú pod zápisovým zámkom. Premenovanie/zmazanie predmetu či nová duplicita odmietne celú dávku namiesto zmeny cieľa.
5. Témy a otázky sa uložia jednou transakciou. Validačná chyba alebo zlyhanie zápisu neuloží nič z dávky; náhľad zostane na opakovanie či opravu. Pri zmene z iného okna vyrieš uvedené chyby a vyber CSV znovu.
6. Úspech najprv zruší možnosť znovu odoslať dávku a potom obnoví prehľady. Pri chybe čítania použi **Refresh totals**, nie nový import. Ak proces skončí bez potvrdenia výsledku, import mohol prebehnúť: najprv obnov a skontroluj predmet.

Close import alebo navigácia zruší čítanie/náhľad; samostatné formuláre otázok/tém zostanú pri práci v banke rozpísané. Pri skutočnom ukladaní modálne okno zablokuje editáciu, navigáciu a bežné zatvorenie/Quit. Parsovanie aj zápis bežia v pomocnom procese bez siete a AI, s poistkou 60 sekúnd. Používaj bežné miestne súbory, nie sieťové cesty.

Banka zobrazuje **50 otázok na stránku**. Hľadanie/filtre platia pre celý predmet. Úprava či obnova podľa možností zachová stránku; zmena filtrov/predmetu vráti prvú. Aktívny filter môže skryť importované otázky.

Šablóna sa zverejní atomicky bez prepísania súborov či sprievodných databázových ciest. POSIX vyžaduje podporu pevných odkazov; ak externý disk zlyhá, použi podporovaný miestny priečinok. Aktuálna schéma je **9**, snímky testov a história sa nemenia. Nejde o synchronizáciu, aktualizáciu/zlučovanie otázok, vyhodnocovanie tabuľkových vzorcov ani import kartičiek na tejto obrazovke.

[Import kartičiek z CSV](FLASHCARD_CSV_IMPORT.md)
