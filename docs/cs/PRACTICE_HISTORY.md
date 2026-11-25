# Historie testů

[English](../PRACTICE_HISTORY.md) · [Čeština](../cs/PRACTICE_HISTORY.md) · [Slovenčina](../sk/PRACTICE_HISTORY.md) · [Русский](../ru/PRACTICE_HISTORY.md)

**Dosud nevydané — redesign testů, krok 3:** Běžící test sdružuje postup/čas v záhlaví a ukazuje počet uložených odpovědí lištou. Řádky A–D přes celou šířku zvýrazní uložený výběr, nikoli správnost; kliknutí na pozadí/text používá původní ukládání. Previous/Next/Clear a Finish sdílejí patičku. Nastavení je ve společné kartě, výsledky/historie mají sjednocené plochy. Chyba zápisu vrátí výběr/vzhled; skryté odpovědi při nastavení či jiné stránce nezapisují. Dlouhý obsah se zalamuje a posouvá. Skóre, termíny, potvrzení, pokračování, filtry a snímky zůstávají; aktuální schéma je 10.

Otevři **Practice Tests → Completed tests**. Historie zpřístupňuje všechny dokončené pokusy po 20 na stránku, od nejnovějšího dokončení; při shodě rozhoduje ID pokusu. Previous / Next přepíná stránky, View result otevře uložené skóre, vybrané i správné odpovědi a vysvětlení. Návrat do nastavení/historie zachová stránku a filtry.

Pokud je test rozpracovaný, otevři tento přehled tlačítkem **← Test setup / history** v běžícím testu; Resume test tě vrátí k pokusu.

Vyber název předmětu uložený s testem a případně vyplň Completed from / Completed through v přesném formátu `YYYY-MM-DD`. Použij Apply filters nebo Enter v poli data. Prázdná mez znamená bez omezení. Obě data zahrnují celý místní kalendářní den podle uloženého času dokončení; změna časového pásma může pokus přesunout na jiný den. Reset filters zruší předmět i data. Použití nebo zrušení filtrů začne na první stránce. Neplatná data či obrácený rozsah zachovají předchozí výsledky i použité filtry.

Názvy pocházejí z dokončených snímků včetně smazaných předmětů. Po přejmenování mají novější pokusy nový historický název. Shodné uložené názvy se seskupují, také při smazání a novém vytvoření stejného názvu; filtr nepoužívá aktuální ID předmětu. Uživatelský obsah se nepřekládá. Nedokončené a zahozené pokusy se nezobrazují.

Úpravy filtrů jsou konceptem do Apply. Stránkování i návrat na obrazovku zachovají koncept a používají dříve použité filtry. Stav platí jen po dobu běhu aplikace, nikoli po restartu. Chyba čtení zachová karty, filtry a stránku; akci lze zopakovat. Počty, názvy a řádky se čtou v jednom snímku SQLite. Při změně počtu se stránka upraví na platnou; nové dokončení v jiném okně může mezi požadavky posunout řádky.

Výsledky jsou neměnné snímky původních otázek, možností, správných odpovědí, vysvětlení a názvu předmětu. Pozdější úpravy a smazání je nemění. Prohlížení historie nevyplní ani nedokončí rozpracovaný test; časový limit dál běží a automatické dokončení může jako dříve převzít obrazovku. Schéma zůstává 8, bez nové závislosti a síťového připojení.

Vývojářské kontroly `tests/test_practice_history.py` a `soskuska/check_practice_history.py` používají dočasné databáze. GUI kontroluje starší výsledky, filtry, chyby/opakování, koncepty/navigaci, oddělení aktivního testu, kompaktní posouvání a nový proces. Nenahrazuje ruční ověření Windows ani fyzického trackpadu.
