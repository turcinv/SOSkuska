# AI Tutor s Ollamou (v0.7.0)

[English](../AI_TUTOR.md) · [Čeština](AI_TUTOR.md) · [Slovenčina](../sk/AI_TUTOR.md) · [Русский](../ru/AI_TUTOR.md)

## v0.23.0 — vzhled statistik a AI Tutora

AI Tutor odděluje ovládání serveru/modelu/jazyka a uložené historie do karet, vedle sebe v širokém okně a pod sebou v kompaktním. Výběr modelu má celý řádek. Vlastník konverzace, přepis, otázka a Odeslat/Zastavit sdílejí ohraničenou plochu pro čtení a psaní. Zpráva o obnově se opakuje u tlačítek opakování, zahození a přerušení, aby bylo potvrzení čitelné po posunu stránky. Navigace a změna velikosti zachovají koncepty, prvky, výběr historie a běžící úlohy. Připojení je výslovné; otevření historie zůstává offline.

V AI Tutor připoj vlastní Ollama server přes Connect / refresh, vyber model a jazyk odpovědi a zadej otázku. Odpověď přichází průběžně; Stop ji zastaví. Ostatní obrazovky zůstávají použitelné během generování i bez Ollamy. Chat se ukládá do místní databáze a lze jej otevřít po restartu; viz průvodce historií.

## První použití

1. Nainstaluj a spusť Ollamu podle [oficiálního návodu](https://docs.ollama.com/quickstart); pro Windows je dostupný [samostatný návod](https://docs.ollama.com/windows), pro Linux [instalace a spuštění](https://docs.ollama.com/linux). Vyber místní model odpovídající paměti počítače. SOSkúška modely sama nestahuje ani neinstaluje.
2. Ověř v Ollamě, že je alespoň jeden model dostupný. Pro běžné studium mimo AI Tutor Ollamu nepotřebuješ.
3. Spusť SOSkúška a otevři AI Tutor. Výchozí adresa je `http://127.0.0.1:11434`. Connect / refresh načte modely; při prázdném seznamu nejprve připrav model v Ollamě a obnov připojení.
4. Vyber model a jazyk: Automatic, English, Czech, Slovak nebo Russian. Automatic požádá model o jazyk poslední otázky, přesnost závisí na modelu. Zadej otázku a zvol Send.
5. Stop ponechá už přijatý text. Po chybě můžeš zkusit další otázku; neúplné odpovědi se neposílají jako kontext dalšího dotazu. New chat vyžaduje druhé potvrzení, pokud existuje chat. Návrat na obrazovku nebo Send/Connect toto potvrzení zruší.

## Soukromí a limity

Síťový požadavek začíná pouze po Connect nebo Send; spuštění aplikace ani navigace nic neodesílá. Na zvolený server jde otázka a omezený kontext tohoto chatu, bez automatických příloh. Výslovně připravený koncept z dokončené otázky obsahuje vybraný snímek (možnosti, vaši odpověď, klíč a vysvětlení) a odešle se po Send. Ostatní záznamy SQLite, předměty, výsledky a soubory se nepřikládají. Výchozí server je místní; při změně adresy rozhoduje zvolený server/model o zpracování dat. Před připojením k jinému serveru je potřeba New chat. Automatický přechod na cloud neexistuje.

Konverzace se ukládají do místní databáze. Volby spojení lze uložit zvlášť přes [Settings](SETTINGS.md). Limit je 12 dotazů na chat, otázka 4 000 znaků, odpověď 16 000 znaků. Kontext zahrnuje nejvýše šest posledních úplných dvojic, celkem 24 000 znaků; starší obsah model nemusí znát. Text je prostý, bez vykreslování Markdown/LaTeX či připojených materiálů. Nejde o ověřené správné odpovědi ani automatické hodnocení učiva.

Adresa podporuje HTTP/HTTPS bez vložených přihlašovacích údajů, cesty, query a fragmentu. Certifikáty HTTPS se ověřují, přesměrování a systémové HTTP proxy se nepoužívají. Autentizované servery zatím nejsou podporované. Časový limit socketu je 30 sekund, celkový požadavek má pojistku 180 sekund; systémové DNS/připojování může oddálit zastavení. Chyba spojení neznamená jistotu, že Ollama není nainstalovaná.


API: [models](https://docs.ollama.com/api/tags) · [chat](https://docs.ollama.com/api/chat) · [streaming](https://docs.ollama.com/api/streaming).

## Uložené konverzace AI Tutor

AI Tutor nyní ukládá konverzace lokálně včetně původního serveru/modelu a stavu odpovědi. Historii lze otevřít bez sítě, výslovně se připojit pro pokračování nebo vybranou konverzaci po potvrzení smazat. Vydáno ve v0.12.0 se schématem 7, které transakčně migruje původní studijní data. [Uložené konverzace AI Tutor](TUTOR_HISTORY.md).


## Vysvětlení otázek · v0.25.0

Dokončené výsledky Practice včetně historie nabízejí **Vysvětlit tuto otázku**. Otevřete místní náhled a zvolte **Připravit v Tutorovi**. Použije se uložený snímek otázky, čtyři možnosti, vaše odpověď nebo Unanswered, uložený klíč a vysvětlení, i po smazání původního obsahu. Náhled ani příprava nic nepřipojují a neodesílají. V Tutorovi zkontrolujte server, model a jazyk, podle potřeby výslovně použijte Connect a poté Send. Upravitelný koncept využívá běžnou místní historii, Stop a opakování uložení.

Tutor musí být nečinný, v čistém New chat s prázdným dotazem a bez čekajícího potvrzení či neuložené odpovědi. Stávající práce zůstává zachována; dokončete ji nebo výslovně potvrďte New chat a opakujte akci. Celý dotaz přes 4 000 znaků je odmítnut s uvedením délky, bez zkracování. Klíč i AI se mohou mýlit; skóre ani zdrojová data se nemění. Automatic požaduje jazyk dodané otázky; výslovná volba jazyka má přednost. Pokyny dotazu jsou anglicky, obsah uživatele se nemění. Schéma zůstává 10 a vydaná verze je v0.25.0.

Implementace: `question_explanation.py` sestavuje omezený dotaz ze snímku, `practice_page.py` řídí náhled a kontrolu aktuálního výsledku, `tutor_page.py` chrání vložení konceptu. Send uloží dotaz před HTTP. Automatické testy používají dočasná data a místní FakeOllama; kvalita modelu a nativní ověření platformy/DPI zůstávají ruční.
