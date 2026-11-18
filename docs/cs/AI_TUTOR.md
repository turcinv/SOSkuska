# AI Tutor s Ollamou (v0.7.0)

[English](../AI_TUTOR.md) · [Čeština](AI_TUTOR.md) · [Slovenčina](../sk/AI_TUTOR.md) · [Русский](../ru/AI_TUTOR.md)

V AI Tutor připoj vlastní Ollama server přes Connect / refresh, vyber model a jazyk odpovědi a zadej otázku. Odpověď přichází průběžně; Stop ji zastaví. Ostatní obrazovky zůstávají použitelné během generování i bez Ollamy. Chat je pouze pro aktuální spuštění aplikace, neukládá se do databáze.

## První použití

1. Nainstaluj a spusť Ollamu podle [oficiálního návodu](https://docs.ollama.com/quickstart); pro Windows je dostupný [samostatný návod](https://docs.ollama.com/windows), pro Linux [instalace a spuštění](https://docs.ollama.com/linux). Vyber místní model odpovídající paměti počítače. SOSkúška modely sama nestahuje ani neinstaluje.
2. Ověř v Ollamě, že je alespoň jeden model dostupný. Pro běžné studium mimo AI Tutor Ollamu nepotřebuješ.
3. Spusť SOSkúška a otevři AI Tutor. Výchozí adresa je `http://127.0.0.1:11434`. Connect / refresh načte modely; při prázdném seznamu nejprve připrav model v Ollamě a obnov připojení.
4. Vyber model a jazyk: Automatic, English, Czech, Slovak nebo Russian. Automatic požádá model o jazyk poslední otázky, přesnost závisí na modelu. Zadej otázku a zvol Send.
5. Stop ponechá už přijatý text. Po chybě můžeš zkusit další otázku; neúplné odpovědi se neposílají jako kontext dalšího dotazu. New chat vyžaduje druhé potvrzení, pokud existuje chat. Návrat na obrazovku nebo Send/Connect toto potvrzení zruší.

## Soukromí a limity

Síťový požadavek začíná pouze po Connect nebo Send; spuštění aplikace ani navigace nic neodesílá. Na zvolený server jde otázka a omezený kontext tohoto chatu, nikoli obsah SQLite, předměty, výsledky nebo soubory. Výchozí server je místní; při změně adresy rozhoduje zvolený server/model o zpracování dat. Před připojením k jinému serveru je potřeba New chat. Automatický přechod na cloud neexistuje.

Chat zůstává jen v paměti. Volby spojení lze uložit přes [Settings](SETTINGS.md); zavření odstraní chat; pokud chceš text uchovat, zkopíruj jej před zavřením. Limit je 12 dotazů na chat, otázka 4 000 znaků, odpověď 16 000 znaků. Kontext zahrnuje nejvýše šest posledních úplných dvojic, celkem 24 000 znaků; starší obsah model nemusí znát. Text je prostý, bez vykreslování Markdown/LaTeX či připojených materiálů. Nejde o ověřené správné odpovědi ani automatické hodnocení učiva.

Adresa podporuje HTTP/HTTPS bez vložených přihlašovacích údajů, cesty, query a fragmentu. Certifikáty HTTPS se ověřují, přesměrování a systémové HTTP proxy se nepoužívají. Autentizované servery zatím nejsou podporované. Časový limit socketu je 30 sekund, celkový požadavek má pojistku 180 sekund; systémové DNS/připojování může oddálit zastavení. Chyba spojení neznamená jistotu, že Ollama není nainstalovaná.


API: [models](https://docs.ollama.com/api/tags) · [chat](https://docs.ollama.com/api/chat) · [streaming](https://docs.ollama.com/api/streaming).
