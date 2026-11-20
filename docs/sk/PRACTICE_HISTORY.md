# História testov

[English](../PRACTICE_HISTORY.md) · [Čeština](../cs/PRACTICE_HISTORY.md) · [Slovenčina](../sk/PRACTICE_HISTORY.md) · [Русский](../ru/PRACTICE_HISTORY.md)

Otvor **Practice Tests → Completed tests**. História sprístupňuje všetky dokončené pokusy po 20 na stránku, od najnovšieho dokončenia; pri zhode rozhoduje ID pokusu. Previous / Next prepína stránky, View result otvorí uložené skóre, vybrané aj správne odpovede a vysvetlenia. Návrat do nastavenia/histórie zachová stránku a filtre.

Ak je test rozpracovaný, otvor tento prehľad tlačidlom **← Test setup / history** v bežiacom teste; Resume test ťa vráti k pokusu.

Vyber názov predmetu uložený s testom a prípadne vyplň Completed from / Completed through v presnom formáte `YYYY-MM-DD`. Použi Apply filters alebo Enter v poli dátumu. Prázdna hranica znamená bez obmedzenia. Oba dátumy zahŕňajú celý miestny kalendárny deň podľa uloženého času dokončenia; zmena časového pásma môže pokus presunúť na iný deň. Reset filters zruší predmet aj dátumy. Použitie alebo zrušenie filtrov začne na prvej stránke. Neplatné dátumy či obrátený rozsah zachovajú predchádzajúce výsledky aj použité filtre.

Názvy pochádzajú z dokončených snímok vrátane zmazaných predmetov. Po premenovaní majú novšie pokusy nový historický názov. Zhodné uložené názvy sa zoskupujú, aj pri zmazaní a novom vytvorení rovnakého názvu; filter nepoužíva aktuálne ID predmetu. Používateľský obsah sa neprekladá. Nedokončené a zahodené pokusy sa nezobrazujú.

Úpravy filtrov sú konceptom do Apply. Stránkovanie aj návrat na obrazovku zachovajú koncept a používajú skôr použité filtre. Stav platí len počas behu aplikácie, nie po reštarte. Chyba čítania zachová karty, filtre a stránku; akciu možno zopakovať. Počty, názvy a riadky sa čítajú v jednej snímke SQLite. Pri zmene počtu sa stránka upraví na platnú; nové dokončenie v inom okne môže medzi požiadavkami posunúť riadky.

Výsledky sú nemenné snímky pôvodných otázok, možností, správnych odpovedí, vysvetlení a názvu predmetu. Neskoršie úpravy a zmazanie ich nemenia. Prezeranie histórie nevyplní ani nedokončí rozpracovaný test; časový limit ďalej beží a automatické dokončenie môže ako doteraz prevziať obrazovku. Schéma zostáva 8, bez novej závislosti a sieťového pripojenia.

Vývojárske kontroly `tests/test_practice_history.py` a `soskuska/check_practice_history.py` používajú dočasné databázy. GUI kontroluje staršie výsledky, filtre, chyby/opakovanie, koncepty/navigáciu, oddelenie aktívneho testu, kompaktné posúvanie a nový proces. Nenahrádza ručné overenie Windows ani fyzického trackpadu.
