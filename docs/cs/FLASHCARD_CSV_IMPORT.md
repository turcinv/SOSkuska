# Import kartiček z CSV

[English](../FLASHCARD_CSV_IMPORT.md) · [Čeština](FLASHCARD_CSV_IMPORT.md) · [Slovenčina](../sk/FLASHCARD_CSV_IMPORT.md) · [Русский](../ru/FLASHCARD_CSV_IMPORT.md)

## Nevydáno — nastavení a společné datové panely

Plán denních záloh, ruční záloha/obnova a oba importy CSV používají společný vzhled karet, odsazení a zalomené zprávy. Skupiny akcí mají tři sloupce v širokém rozložení, jinak dva. Varování obnovy je nad tlačítkem nevratného potvrzení a Zrušit. Pole náhledu/chyb CSV mají viditelné okraje a vlastní posouvání. Pravidla náhledu, zrušení, atomického zápisu, oddělených procesů, zavření po obnově a bezpečnostní kopie se nemění.

Flashcards nyní podporuje import UTF-8 CSV do existujícího balíčku: šablonu s hlavičkou, stránkovaný náhled, odmítnutí přesných duplicit a jedno atomické uložení. Maximum 2 MiB / 500 záznamů. Nové kartičky jsou ihned splatné; původní termíny a historie hodnocení zůstávají zachované. Aktuální schéma je 10.

1. Otevři **Flashcards → Open deck → Import CSV**. Cílový balíček musí existovat; pro vytvoření nového nejprve založ předmět.
2. Přes **Save CSV template** vyber nepoužitý název. Vyplň sloupce `front,back` v editoru nebo tabulce a exportuj čárkami oddělené UTF-8 CSV; BOM je volitelný.
3. Zvol **Choose CSV…** a prohlédni kartičky přes Previous / Next. Oprav všechny chyby, než se zpřístupní **Import all**. Náhled nic neukládá.
4. Zvol **Import all**. Uloží se vše, nebo nic. Počkej na dokončení; potom lze nové kartičky opakovat přes **Study due**.

Přední strana je povinná (1–2 000 znaků), zadní také (1–4 000). Okrajové mezery se odstraní. Pořadí, velikost písmen a okrajové mezery hlaviček se mohou lišit; neznámé či opakované sloupce se odmítnou. Čárky a více řádků uzavři do standardních CSV uvozovek. Prázdné záznamy se ignorují. Středníky, stará kódování, obrázky, automatický převod otázek ani slučování/aktualizace nejsou podporované.

Duplicita znamená přesně stejnou oříznutou přední i zadní stranu s rozlišením velikosti písmen, v souboru nebo cílovém balíčku. Odmítne se celá dávka; nic se nepřeskakuje ani nepřepisuje. Jiný balíček může obsahovat stejnou kartičku. Identita/název balíčku a duplicity se znovu ověří pod zámkem zápisu. Přejmenovaný/smazaný balíček vyžaduje nové otevření a výběr souboru; balíček zachovaný po smazání předmětu zůstává použitelný.

Náhled je soukromá dávka: změna původního souboru vyžaduje nový **Choose CSV…**. Zavření importu nebo navigace zahodí náhled. Čtení lze zrušit; ukládání blokuje navigaci/Quit. Při chybě zápisu lze zachovanou dávku zkusit uložit znovu. Po úspěšném zápisu a chybě přehledu použij **Refresh totals**; nic znovu neimportuje. Pokud pomocný proces nepotvrdí výsledek, nejprve zkontroluj balíček: dávka se již mohla uložit.

Šablona obsahuje pouze hlavičky, zveřejní se atomicky a nepřepisuje soubory ani doprovodné cesty databáze. POSIX vyžaduje pevné odkazy; při nepodporovaném externím disku použij místní složku. Čtení a validaci provádějí oddělené procesy; náhled otevře existující databázi jen pro čtení bez migrace. Bez cloudu, změny schématu a smyšlených hodnocení.

[CSV template](../examples/flashcards-template.csv)
