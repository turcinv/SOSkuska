# AI Tutor s Ollamou (v0.7.0)

[English](../AI_TUTOR.md) · [Čeština](../cs/AI_TUTOR.md) · [Slovenčina](AI_TUTOR.md) · [Русский](../ru/AI_TUTOR.md)

V AI Tutor pripoj vlastný server Ollama cez Connect / refresh, vyber model a jazyk odpovede a zadaj otázku. Odpoveď prichádza priebežne; Stop ju zastaví. Ostatné obrazovky zostávajú použiteľné počas generovania aj bez Ollamy. Chat je iba pre aktuálne spustenie aplikácie, neukladá sa do databázy.

## Prvé použitie

1. Nainštaluj a spusti Ollamu podľa [oficiálneho návodu](https://docs.ollama.com/quickstart); pre Windows je dostupný [samostatný návod](https://docs.ollama.com/windows), pre Linux [inštalácia a spustenie](https://docs.ollama.com/linux). Vyber miestny model zodpovedajúci pamäti počítača. SOSkúška modely sama nesťahuje ani neinštaluje.
2. Over v Ollame, že je dostupný aspoň jeden model. Na bežné štúdium mimo AI Tutor Ollamu nepotrebuješ.
3. Spusti SOSkúška a otvor AI Tutor. Predvolená adresa je `http://127.0.0.1:11434`. Connect / refresh načíta modely; pri prázdnom zozname najprv priprav model v Ollame a obnov spojenie.
4. Vyber model a jazyk: Automatic, English, Czech, Slovak alebo Russian. Automatic požiada model o jazyk poslednej otázky, presnosť závisí od modelu. Zadaj otázku a zvoľ Send.
5. Stop ponechá prijatý text. Po chybe môžeš skúsiť ďalšiu otázku; neúplné odpovede sa neposielajú ako kontext ďalšieho dotazu. New chat vyžaduje druhé potvrdenie, ak existuje chat. Návrat na obrazovku alebo Send/Connect toto potvrdenie zruší.

## Súkromie a limity

Sieťová požiadavka začína iba po Connect alebo Send; spustenie aplikácie ani navigácia nič neposiela. Na zvolený server ide otázka a obmedzený kontext tohto chatu, nie obsah SQLite, predmety, výsledky či súbory. Predvolený server je miestny; pri zmene adresy rozhoduje zvolený server/model o spracovaní údajov. Pred pripojením k inému serveru je potrebné New chat. Automatický prechod na cloud neexistuje.

Chat zostáva iba v pamäti. Voľby spojenia možno uložiť cez [Settings](SETTINGS.md); zatvorenie odstráni chat; ak chceš text uchovať, skopíruj ho pred zatvorením. Limit je 12 dotazov na chat, otázka 4 000 znakov, odpoveď 16 000 znakov. Kontext zahŕňa najviac šesť posledných úplných dvojíc, spolu 24 000 znakov; starší obsah model nemusí poznať. Text je obyčajný, bez vykresľovania Markdown/LaTeX či pripojených materiálov. Nejde o overené správne odpovede ani automatické hodnotenie učiva.

Adresa podporuje HTTP/HTTPS bez vložených prihlasovacích údajov, cesty, query a fragmentu. Certifikáty HTTPS sa overujú, presmerovania a systémové HTTP proxy sa nepoužívajú. Autentizované servery zatiaľ nie sú podporované. Časový limit socketu je 30 sekúnd, celková požiadavka má poistku 180 sekúnd; systémové DNS/pripájanie môže oddialiť zastavenie. Chyba spojenia neznamená istotu, že Ollama nie je nainštalovaná.


API: [models](https://docs.ollama.com/api/tags) · [chat](https://docs.ollama.com/api/chat) · [streaming](https://docs.ollama.com/api/streaming).
