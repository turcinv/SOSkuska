# Historie testů

[English](../PRACTICE_HISTORY.md) · [Čeština](../cs/PRACTICE_HISTORY.md) · [Slovenčina](../sk/PRACTICE_HISTORY.md) · [Русский](../ru/PRACTICE_HISTORY.md)

**v0.20.0 — redesign testů, krok 3:** Běžící test sdružuje postup/čas v záhlaví a ukazuje počet uložených odpovědí lištou. Řádky A–D přes celou šířku zvýrazní uložený výběr, nikoli správnost; kliknutí na pozadí/text používá původní ukládání. Previous/Next/Clear a Finish sdílejí patičku. Nastavení je ve společné kartě, výsledky/historie mají sjednocené plochy. Chyba zápisu vrátí výběr/vzhled; skryté odpovědi při nastavení či jiné stránce nezapisují. Dlouhý obsah se zalamuje a posouvá. Skóre, termíny, potvrzení, pokračování, filtry a snímky zůstávají; aktuální schéma je 10.

Otevři **Practice Tests → Completed tests**. Historie zpřístupňuje všechny dokončené pokusy po 20 na stránku, od nejnovějšího dokončení; při shodě rozhoduje ID pokusu. Previous / Next přepíná stránky, View result otevře uložené skóre, vybrané i správné odpovědi a vysvětlení. Návrat do nastavení/historie zachová stránku a filtry.

Pokud je test rozpracovaný, otevři tento přehled tlačítkem **← Test setup / history** v běžícím testu; Resume test tě vrátí k pokusu.

Vyber název předmětu uložený s testem a případně vyplň Completed from / Completed through v přesném formátu `YYYY-MM-DD`. Použij Apply filters nebo Enter v poli data. Prázdná mez znamená bez omezení. Obě data zahrnují celý místní kalendářní den podle uloženého času dokončení; změna časového pásma může pokus přesunout na jiný den. Reset filters zruší předmět i data. Použití nebo zrušení filtrů začne na první stránce. Neplatná data či obrácený rozsah zachovají předchozí výsledky i použité filtry.

Názvy pocházejí z dokončených snímků včetně smazaných předmětů. Po přejmenování mají novější pokusy nový historický název. Shodné uložené názvy se seskupují, také při smazání a novém vytvoření stejného názvu; filtr nepoužívá aktuální ID předmětu. Uživatelský obsah se nepřekládá. Nedokončené a zahozené pokusy se nezobrazují.

Úpravy filtrů jsou konceptem do Apply. Stránkování i návrat na obrazovku zachovají koncept a používají dříve použité filtry. Stav platí jen po dobu běhu aplikace, nikoli po restartu. Chyba čtení zachová karty, filtry a stránku; akci lze zopakovat. Počty, názvy a řádky se čtou v jednom snímku SQLite. Při změně počtu se stránka upraví na platnou; nové dokončení v jiném okně může mezi požadavky posunout řádky.

Výsledky jsou neměnné snímky původních otázek, možností, správných odpovědí, vysvětlení a názvu předmětu. Pozdější úpravy a smazání je nemění. Prohlížení historie nevyplní ani nedokončí rozpracovaný test; časový limit dál běží a automatické dokončení může jako dříve převzít obrazovku. Schéma zůstává 8, bez nové závislosti a síťového připojení.

Vývojářské kontroly `tests/test_practice_history.py` a `soskuska/check_practice_history.py` používají dočasné databáze. GUI kontroluje starší výsledky, filtry, chyby/opakování, koncepty/navigaci, oddělení aktivního testu, kompaktní posouvání a nový proces. Nenahrazuje ruční ověření Windows ani fyzického trackpadu.


## Vysvětlení otázek · v0.25.0

Dokončené výsledky Practice včetně historie nabízejí **Vysvětlit tuto otázku**. Otevřete místní náhled a zvolte **Připravit v Tutorovi**. Použije se uložený snímek otázky, čtyři možnosti, vaše odpověď nebo Unanswered, uložený klíč a vysvětlení, i po smazání původního obsahu. Náhled ani příprava nic nepřipojují a neodesílají. V Tutorovi zkontrolujte server, model a jazyk, podle potřeby výslovně použijte Connect a poté Send. Upravitelný koncept využívá běžnou místní historii, Stop a opakování uložení.

Tutor musí být nečinný, v čistém New chat s prázdným dotazem a bez čekajícího potvrzení či neuložené odpovědi. Stávající práce zůstává zachována; dokončete ji nebo výslovně potvrďte New chat a opakujte akci. Celý dotaz přes 4 000 znaků je odmítnut s uvedením délky, bez zkracování. Klíč i AI se mohou mýlit; skóre ani zdrojová data se nemění. Automatic požaduje jazyk dodané otázky; výslovná volba jazyka má přednost. Pokyny dotazu jsou anglicky, obsah uživatele se nemění. Schéma zůstává 10 a vydaná verze je v0.31.1.

Implementace: `question_explanation.py` sestavuje omezený dotaz ze snímku, `practice_page.py` řídí náhled a kontrolu aktuálního výsledku, `tutor_page.py` chrání vložení konceptu. Send uloží dotaz před HTTP. Automatické testy používají dočasná data a místní FakeOllama; kvalita modelu a nativní ověření platformy/DPI zůstávají ruční.


## Studijní režimy AI · v0.26.0

V dokončeném výsledku otevřete **Vysvětlit tuto otázku** a před **Připravit v Tutorovi** vyberte **Studijní režim**. **Vysvětlit odpověď** zachová dosavadní vysvětlení; **Vysvětlit jednoduše** požaduje krátké kroky pro začátečníka a příklad; **Dát nápovědu** požaduje jednu pojmovou nápovědu a z dotazu vynechá vaši odpověď, uložený klíč i vysvětlení; **Procvičit mě** klade jednu novou doplňující otázku a před zpětnou vazbou čeká na odpověď. Jde o neformální procvičování bez zápisu bodovaného testu nebo změny zdrojů.

Změna režimu obnoví přesný místní náhled a zneplatní jeho předchozí akci přípravy. Připojení, odeslání a vytvoření konverzace vyžadují stávající výslovné ovládání. Odeslaný dotaz se ukládá do běžné místní historie; platí dosavadní jazyk, limit 4 000 znaků, ochrana čistého chatu, Zastavit a opakování uložení. Nápověda stále obsahuje čtyři možnosti: model může odpověď odvodit či prozradit a již zobrazené výsledky zůstávají viditelné. Kvalita a dodržení režimu vyžadují pozdější test skutečného modelu, který uživatel výslovně odložil. Automatické testy používají místní FakeOllama. Vydaná verze je v0.31.1, schéma 10.
