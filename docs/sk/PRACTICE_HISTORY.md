# História testov

[English](../PRACTICE_HISTORY.md) · [Čeština](../cs/PRACTICE_HISTORY.md) · [Slovenčina](../sk/PRACTICE_HISTORY.md) · [Русский](../ru/PRACTICE_HISTORY.md)

**v0.20.0 — redizajn testov, krok 3:** Bežiaci test združuje priebeh/čas v záhlaví a ukazuje počet uložených odpovedí lištou. Riadky A–D cez celú šírku zvýraznia uložený výber, nie správnosť; kliknutie na pozadie/text používa pôvodné ukladanie. Previous/Next/Clear a Finish zdieľajú pätu. Nastavenia sú v spoločnej karte, výsledky/história majú zjednotené plochy. Chyba zápisu vráti výber/vzhľad; skryté odpovede pri nastaveniach či inej stránke nezapisujú. Dlhý obsah sa zalamuje a posúva. Skóre, termíny, potvrdenia, pokračovanie, filtre a snímky zostávajú; aktuálna schéma je 10.

Otvor **Practice Tests → Completed tests**. História sprístupňuje všetky dokončené pokusy po 20 na stránku, od najnovšieho dokončenia; pri zhode rozhoduje ID pokusu. Previous / Next prepína stránky, View result otvorí uložené skóre, vybrané aj správne odpovede a vysvetlenia. Návrat do nastavenia/histórie zachová stránku a filtre.

Ak je test rozpracovaný, otvor tento prehľad tlačidlom **← Test setup / history** v bežiacom teste; Resume test ťa vráti k pokusu.

Vyber názov predmetu uložený s testom a prípadne vyplň Completed from / Completed through v presnom formáte `YYYY-MM-DD`. Použi Apply filters alebo Enter v poli dátumu. Prázdna hranica znamená bez obmedzenia. Oba dátumy zahŕňajú celý miestny kalendárny deň podľa uloženého času dokončenia; zmena časového pásma môže pokus presunúť na iný deň. Reset filters zruší predmet aj dátumy. Použitie alebo zrušenie filtrov začne na prvej stránke. Neplatné dátumy či obrátený rozsah zachovajú predchádzajúce výsledky aj použité filtre.

Názvy pochádzajú z dokončených snímok vrátane zmazaných predmetov. Po premenovaní majú novšie pokusy nový historický názov. Zhodné uložené názvy sa zoskupujú, aj pri zmazaní a novom vytvorení rovnakého názvu; filter nepoužíva aktuálne ID predmetu. Používateľský obsah sa neprekladá. Nedokončené a zahodené pokusy sa nezobrazujú.

Úpravy filtrov sú konceptom do Apply. Stránkovanie aj návrat na obrazovku zachovajú koncept a používajú skôr použité filtre. Stav platí len počas behu aplikácie, nie po reštarte. Chyba čítania zachová karty, filtre a stránku; akciu možno zopakovať. Počty, názvy a riadky sa čítajú v jednej snímke SQLite. Pri zmene počtu sa stránka upraví na platnú; nové dokončenie v inom okne môže medzi požiadavkami posunúť riadky.

Výsledky sú nemenné snímky pôvodných otázok, možností, správnych odpovedí, vysvetlení a názvu predmetu. Neskoršie úpravy a zmazanie ich nemenia. Prezeranie histórie nevyplní ani nedokončí rozpracovaný test; časový limit ďalej beží a automatické dokončenie môže ako doteraz prevziať obrazovku. Schéma zostáva 8, bez novej závislosti a sieťového pripojenia.

Vývojárske kontroly `tests/test_practice_history.py` a `soskuska/check_practice_history.py` používajú dočasné databázy. GUI kontroluje staršie výsledky, filtre, chyby/opakovanie, koncepty/navigáciu, oddelenie aktívneho testu, kompaktné posúvanie a nový proces. Nenahrádza ručné overenie Windows ani fyzického trackpadu.


## Vysvetlenia otázok · v0.25.0

Dokončené výsledky Practice vrátane histórie ponúkajú **Vysvetliť túto otázku**. Otvorte miestny náhľad a zvoľte **Pripraviť v Tutorovi**. Použije sa uložená snímka otázky, štyri možnosti, vaša odpoveď alebo Unanswered, uložený kľúč a vysvetlenie, aj po odstránení pôvodného obsahu. Náhľad ani príprava nič nepripájajú ani neposielajú. V Tutorovi skontrolujte server, model a jazyk, podľa potreby výslovne použite Connect a potom Send. Upraviteľný návrh využíva bežnú miestnu históriu, Stop a opakovanie uloženia.

Tutor musí byť nečinný, v čistom New chat s prázdnou otázkou a bez čakajúceho potvrdenia či neuloženej odpovede. Existujúca práca zostáva zachovaná; dokončite ju alebo výslovne potvrďte New chat a zopakujte akciu. Celý dotaz nad 4 000 znakov je odmietnutý s uvedením dĺžky, bez skracovania. Kľúč aj AI sa môžu mýliť; skóre ani zdrojové dáta sa nemenia. Automatic požaduje jazyk dodanej otázky; výslovná voľba jazyka má prednosť. Pokyny dotazu sú anglicky, obsah používateľa sa nemení. Schéma zostáva 10 a vydaná verzia je v0.28.0.

Implementácia: `question_explanation.py` zostavuje ohraničený dotaz zo snímky, `practice_page.py` riadi náhľad a kontrolu aktuálneho výsledku, `tutor_page.py` chráni vloženie návrhu. Send uloží otázku pred HTTP. Automatické testy používajú dočasné dáta a miestny FakeOllama; kvalita modelu a natívne overenie platformy/DPI zostávajú ručné.


## Študijné režimy AI · v0.26.0

V dokončenom výsledku otvorte **Vysvetliť túto otázku** a pred **Pripraviť v Tutorovi** vyberte **Študijný režim**. **Vysvetliť odpoveď** zachová doterajšie vysvetlenie; **Vysvetliť jednoducho** požaduje krátke kroky pre začiatočníka a príklad; **Dať nápovedu** požaduje jednu pojmovú nápovedu a z otázky pre AI vynechá vašu odpoveď, uložený kľúč aj vysvetlenie; **Precvičiť ma** kladie jednu novú doplňujúcu otázku a pred spätnou väzbou čaká na odpoveď. Ide o neformálne precvičovanie bez zápisu bodovaného testu alebo zmeny zdrojov.

Zmena režimu obnoví presný miestny náhľad a zneplatní jeho predchádzajúcu akciu prípravy. Pripojenie, odoslanie a vytvorenie konverzácie vyžadujú existujúce výslovné ovládanie. Odoslaná otázka sa ukladá do bežnej miestnej histórie; platí doterajší jazyk, limit 4 000 znakov, ochrana čistého chatu, Zastaviť a opakovanie uloženia. Nápoveda stále obsahuje štyri možnosti: model môže odpoveď odvodiť či prezradiť a už zobrazené výsledky zostávajú viditeľné. Kvalita a dodržanie režimu vyžadujú neskorší test skutočného modelu, ktorý používateľ výslovne odložil. Automatické testy používajú miestny FakeOllama. Vydaná verzia je v0.28.0, schéma 10.
