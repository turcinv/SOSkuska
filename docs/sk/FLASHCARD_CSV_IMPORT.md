# Import kartičiek z CSV

[English](../FLASHCARD_CSV_IMPORT.md) · [Čeština](../cs/FLASHCARD_CSV_IMPORT.md) · [Slovenčina](FLASHCARD_CSV_IMPORT.md) · [Русский](../ru/FLASHCARD_CSV_IMPORT.md)

Flashcards teraz podporuje import UTF-8 CSV do existujúceho balíčka: šablónu s hlavičkou, stránkovaný náhľad, odmietnutie presných duplicít a jedno atomické uloženie. Maximum 2 MiB / 500 záznamov. Nové kartičky sú ihneď splatné; pôvodné termíny a história hodnotení zostávajú zachované. Schéma aktuálnej vetvy je 10.

1. Otvor **Flashcards → Open deck → Import CSV**. Cieľový balíček musí existovať; na vytvorenie nového najprv založ predmet.
2. Cez **Save CSV template** vyber nepoužitý názov. Vyplň stĺpce `front,back` v editore alebo tabuľke a exportuj čiarkami oddelené UTF-8 CSV; BOM je voliteľný.
3. Zvoľ **Choose CSV…** a prezri kartičky cez Previous / Next. Oprav všetky chyby pred sprístupnením **Import all**. Náhľad nič neukladá.
4. Zvoľ **Import all**. Uloží sa všetko, alebo nič. Počkaj na dokončenie; potom možno nové kartičky opakovať cez **Study due**.

Predná strana je povinná (1–2 000 znakov), zadná tiež (1–4 000). Okrajové medzery sa odstránia. Poradie, veľkosť písmen a okrajové medzery hlavičiek sa môžu líšiť; neznáme či opakované stĺpce sa odmietnu. Čiarky a viac riadkov uzavri do štandardných CSV úvodzoviek. Prázdne záznamy sa ignorujú. Bodkočiarky, staré kódovania, obrázky, automatický prevod otázok ani zlučovanie/aktualizácie nie sú podporované.

Duplicita znamená presne rovnakú orezanú prednú aj zadnú stranu s rozlíšením veľkosti písmen, v súbore alebo cieľovom balíčku. Odmietne sa celá dávka; nič sa nepreskakuje ani neprepisuje. Iný balíček môže obsahovať rovnakú kartičku. Identita/názov balíčka a duplicity sa znovu overia pod zámkom zápisu. Premenovaný/zmazaný balíček vyžaduje nové otvorenie a výber súboru; balíček zachovaný po zmazaní predmetu zostáva použiteľný.

Náhľad je súkromná dávka: zmena pôvodného súboru vyžaduje nový **Choose CSV…**. Zatvorenie importu alebo navigácia zahodí náhľad. Čítanie možno zrušiť; ukladanie blokuje navigáciu/Quit. Pri chybe zápisu možno zachovanú dávku skúsiť uložiť znovu. Po úspešnom zápise a chybe prehľadu použi **Refresh totals**; nič znovu neimportuje. Ak pomocný proces nepotvrdí výsledok, najprv skontroluj balíček: dávka sa už mohla uložiť.

Šablóna obsahuje iba hlavičky, zverejní sa atomicky a neprepisuje súbory ani sprievodné cesty databázy. POSIX vyžaduje pevné odkazy; pri nepodporovanom externom disku použi miestny priečinok. Čítanie a validáciu vykonávajú oddelené procesy; náhľad otvorí existujúcu databázu iba na čítanie bez migrácie. Bez cloudu, zmeny schémy a vymyslených hodnotení.

[CSV template](../examples/flashcards-template.csv)
