# AI Tutor s Ollamou (v0.7.0)

[English](../AI_TUTOR.md) · [Čeština](../cs/AI_TUTOR.md) · [Slovenčina](AI_TUTOR.md) · [Русский](../ru/AI_TUTOR.md)

## v0.23.0 — vzhľad štatistík a AI Tutora

AI Tutor oddeľuje ovládanie servera/modelu/jazyka a uloženej histórie do kariet, vedľa seba v širokom okne a pod sebou v kompaktnom. Výber modelu má celý riadok. Vlastník konverzácie, prepis, otázka a Odoslať/Zastaviť zdieľajú ohraničenú plochu na čítanie a písanie. Správa o obnove sa opakuje pri tlačidlách opakovania, zahodenia a prerušenia, aby bolo potvrdenie čitateľné po posune stránky. Navigácia a zmena veľkosti zachovajú koncepty, prvky, výber histórie a bežiace úlohy. Pripojenie je výslovné; otvorenie histórie zostáva offline.

V AI Tutor pripoj vlastný server Ollama cez Connect / refresh, vyber model a jazyk odpovede a zadaj otázku. Odpoveď prichádza priebežne; Stop ju zastaví. Ostatné obrazovky zostávajú použiteľné počas generovania aj bez Ollamy. Chat sa ukladá do miestnej databázy a možno ho otvoriť po reštarte; pozri sprievodcu históriou.

## Prvé použitie

1. Nainštaluj a spusti Ollamu podľa [oficiálneho návodu](https://docs.ollama.com/quickstart); pre Windows je dostupný [samostatný návod](https://docs.ollama.com/windows), pre Linux [inštalácia a spustenie](https://docs.ollama.com/linux). Vyber miestny model zodpovedajúci pamäti počítača. SOSkúška modely sama nesťahuje ani neinštaluje.
2. Over v Ollame, že je dostupný aspoň jeden model. Na bežné štúdium mimo AI Tutor Ollamu nepotrebuješ.
3. Spusti SOSkúška a otvor AI Tutor. Predvolená adresa je `http://127.0.0.1:11434`. Connect / refresh načíta modely; pri prázdnom zozname najprv priprav model v Ollame a obnov spojenie.
4. Vyber model a jazyk: Automatic, English, Czech, Slovak alebo Russian. Automatic požiada model o jazyk poslednej otázky, presnosť závisí od modelu. Zadaj otázku a zvoľ Send.
5. Stop ponechá prijatý text. Po chybe môžeš skúsiť ďalšiu otázku; neúplné odpovede sa neposielajú ako kontext ďalšieho dotazu. New chat vyžaduje druhé potvrdenie, ak existuje chat. Návrat na obrazovku alebo Send/Connect toto potvrdenie zruší.

## Súkromie a limity

Sieťová požiadavka začína iba po Connect alebo Send; spustenie aplikácie ani navigácia nič neposiela. Na zvolený server ide otázka a obmedzený kontext tohto chatu, bez automatických príloh. Výslovne pripravený návrh z dokončenej otázky obsahuje vybranú snímku a odošle sa po Send. Režim nápovedy zahŕňa iba otázku a možnosti; ostatné režimy aj vašu odpoveď, uložený kľúč a vysvetlenie. Ostatné záznamy SQLite, predmety, výsledky a súbory sa neprikladajú. Predvolený server je miestny; pri zmene adresy rozhoduje zvolený server/model o spracovaní údajov. Pred pripojením k inému serveru je potrebné New chat. Automatický prechod na cloud neexistuje.

Konverzácie sa ukladajú do miestnej databázy. Voľby spojenia možno uložiť osobitne cez [Settings](SETTINGS.md). Limit je 12 dotazov na chat, otázka 4 000 znakov, odpoveď 16 000 znakov. Kontext zahŕňa najviac šesť posledných úplných dvojíc, spolu 24 000 znakov; starší obsah model nemusí poznať. Text je obyčajný, bez vykresľovania Markdown/LaTeX či pripojených materiálov. Nejde o overené správne odpovede ani automatické hodnotenie učiva.

Adresa podporuje HTTP/HTTPS bez vložených prihlasovacích údajov, cesty, query a fragmentu. Certifikáty HTTPS sa overujú, presmerovania a systémové HTTP proxy sa nepoužívajú. Autentizované servery zatiaľ nie sú podporované. Časový limit socketu je 30 sekúnd, celková požiadavka má poistku 180 sekúnd; systémové DNS/pripájanie môže oddialiť zastavenie. Chyba spojenia neznamená istotu, že Ollama nie je nainštalovaná.


API: [models](https://docs.ollama.com/api/tags) · [chat](https://docs.ollama.com/api/chat) · [streaming](https://docs.ollama.com/api/streaming).

## Uložené konverzácie AI Tutor

AI Tutor teraz ukladá konverzácie lokálne vrátane pôvodného servera/modelu a stavu odpovede. Históriu možno otvoriť bez siete, výslovne sa pripojiť na pokračovanie alebo vybranú konverzáciu po potvrdení zmazať. Vydané vo v0.12.0 so schémou 7, ktorá transakčne migruje pôvodné študijné údaje. [Uložené konverzácie AI Tutor](TUTOR_HISTORY.md).


## Vysvetlenia otázok · v0.25.0

Dokončené výsledky Practice vrátane histórie ponúkajú **Vysvetliť túto otázku**. Otvorte miestny náhľad a zvoľte **Pripraviť v Tutorovi**. Použije sa uložená snímka otázky, štyri možnosti, vaša odpoveď alebo Unanswered, uložený kľúč a vysvetlenie, aj po odstránení pôvodného obsahu. Náhľad ani príprava nič nepripájajú ani neposielajú. V Tutorovi skontrolujte server, model a jazyk, podľa potreby výslovne použite Connect a potom Send. Upraviteľný návrh využíva bežnú miestnu históriu, Stop a opakovanie uloženia.

Tutor musí byť nečinný, v čistom New chat s prázdnou otázkou a bez čakajúceho potvrdenia či neuloženej odpovede. Existujúca práca zostáva zachovaná; dokončite ju alebo výslovne potvrďte New chat a zopakujte akciu. Celý dotaz nad 4 000 znakov je odmietnutý s uvedením dĺžky, bez skracovania. Kľúč aj AI sa môžu mýliť; skóre ani zdrojové dáta sa nemenia. Automatic požaduje jazyk dodanej otázky; výslovná voľba jazyka má prednosť. Pokyny dotazu sú anglicky, obsah používateľa sa nemení. Schéma zostáva 10 a vydaná verzia je v0.31.0.

Implementácia: `question_explanation.py` zostavuje ohraničený dotaz zo snímky, `practice_page.py` riadi náhľad a kontrolu aktuálneho výsledku, `tutor_page.py` chráni vloženie návrhu. Send uloží otázku pred HTTP. Automatické testy používajú dočasné dáta a miestny FakeOllama; kvalita modelu a natívne overenie platformy/DPI zostávajú ručné.


## Študijné režimy AI · v0.26.0

V dokončenom výsledku otvorte **Vysvetliť túto otázku** a pred **Pripraviť v Tutorovi** vyberte **Študijný režim**. **Vysvetliť odpoveď** zachová doterajšie vysvetlenie; **Vysvetliť jednoducho** požaduje krátke kroky pre začiatočníka a príklad; **Dať nápovedu** požaduje jednu pojmovú nápovedu a z otázky pre AI vynechá vašu odpoveď, uložený kľúč aj vysvetlenie; **Precvičiť ma** kladie jednu novú doplňujúcu otázku a pred spätnou väzbou čaká na odpoveď. Ide o neformálne precvičovanie bez zápisu bodovaného testu alebo zmeny zdrojov.

Zmena režimu obnoví presný miestny náhľad a zneplatní jeho predchádzajúcu akciu prípravy. Pripojenie, odoslanie a vytvorenie konverzácie vyžadujú existujúce výslovné ovládanie. Odoslaná otázka sa ukladá do bežnej miestnej histórie; platí doterajší jazyk, limit 4 000 znakov, ochrana čistého chatu, Zastaviť a opakovanie uloženia. Nápoveda stále obsahuje štyri možnosti: model môže odpoveď odvodiť či prezradiť a už zobrazené výsledky zostávajú viditeľné. Kvalita a dodržanie režimu vyžadujú neskorší test skutočného modelu, ktorý používateľ výslovne odložil. Automatické testy používajú miestny FakeOllama. Vydaná verzia je v0.31.0, schéma 10.
