# Uložené konverzácie AI Tutor

[English](../TUTOR_HISTORY.md) · [Čeština](../cs/TUTOR_HISTORY.md) · [Slovenčina](TUTOR_HISTORY.md) · [Русский](../ru/TUTOR_HISTORY.md)

## v0.23.0 — vzhľad štatistík a AI Tutora

AI Tutor oddeľuje ovládanie servera/modelu/jazyka a uloženej histórie do kariet, vedľa seba v širokom okne a pod sebou v kompaktnom. Výber modelu má celý riadok. Vlastník konverzácie, prepis, otázka a Odoslať/Zastaviť zdieľajú ohraničenú plochu na čítanie a písanie. Správa o obnove sa opakuje pri tlačidlách opakovania, zahodenia a prerušenia, aby bolo potvrdenie čitateľné po posune stránky. Navigácia a zmena veľkosti zachovajú koncepty, prvky, výber histórie a bežiace úlohy. Pripojenie je výslovné; otvorenie histórie zostáva offline.

AI Tutor teraz ukladá konverzácie lokálne vrátane pôvodného servera/modelu a stavu odpovede. Históriu možno otvoriť bez siete, výslovne sa pripojiť na pokračovanie alebo vybranú konverzáciu po potvrdení zmazať. Vydané vo v0.12.0 so schémou 7, ktorá transakčne migruje pôvodné študijné údaje.

## Použitie histórie

Pripoj sa, vyber model/jazyk, napíš otázku a zvoľ Send. Otázka sa uloží pred sieťovou požiadavkou. Názov vzniká z prvej otázky. Odpoveď sa ukladá po dokončení, zastavení alebo chybe. New chat odpojí aktuálnu konverzáciu; potvrdenie vymaže rozpísanú otázku, ale zachová históriu.

Výber ukazuje 20 konverzácií na stránku podľa poslednej zmeny. Použi Previous chats / Next chats a Refresh, vyber názov a Open. Otvorenie nič neposiela ani sa nepripája. Obnoví pôvodný server/model a text; pokračovanie vyžaduje Connect / refresh. Konverzácia zostáva spojená s pôvodným serverom a modelom. Pre iný použi New chat; chýbajúci model sa nenahradí automaticky. Jazyk odpovede možno meniť pri každej otázke.

Delete vyžaduje druhé potvrdenie a odstráni vybranú konverzáciu aj jej otázky/odpovede. Kontrola revízie odmietne zastaranú zmenu či zmazanie z iného okna. Prechod na inú konverzáciu sa s rozpísanou otázkou odmietne; najprv ju výslovne vymaž. Opätovné otvorenie rovnakej konverzácie otázku zachová.

## Prerušenie a chyby

Stop uchová prijatý text ako stopped. Failed, stopped, pending a interrupted nevstupujú do kontextu modelu. Bežné zatvorenie/Quit uloží viditeľnú časť ako interrupted a zruší sieť bez čakania na vlákno. Chyba uloženia ponechá text, zakáže odosielanie/prepínanie a ponúkne Retry save reply. Quit ponechá okno otvorené a ukáže AI Tutor, kým odpoveď neuložíš alebo výslovne nezahodíš. Discard unsaved vyžaduje potvrdenie, zachová ďalšiu rozpísanú otázku a nemaže históriu.

Pád procesu/systému môže ponechať uloženú pending otázku; časti streamu sa priebežne neukladajú, preto sa rozpracovaná odpoveď môže stratiť. Otvor ju a dvakrát potvrď Mark interrupted pred ďalšou otázkou. Ide o výslovnú akciu, pretože iné okno môže stále generovať. Obnova/zmazanie zneplatní jeho neskorý zápis; pred zahodením či novým načítaním skopíruj neuložený text.

## Údaje, súkromie a limity

`tutor_conversations` obsahuje názov, endpoint, model, revíziu a časy UTC; `tutor_turns` poradie, otázku/odpoveď/jazyk/stav a časy. Revízia sa kontroluje v rovnakej transakcii ako zápis; opakované uloženie rovnakej dokončenej odpovede nič neduplikuje. Sieťové vlákna nevolajú Tk ani SQLite. Spustenie, história, navigácia a Settings Save nič neposielajú; Send posiela obmedzený dokončený kontext vybraného chatu.

Konverzácie sú obyčajný text vo vybranej databáze a patria do záloh. Nie sú šifrované ani synchronizované. Limit: 12 otázok na konverzáciu, otázka 4 000 znakov, odpoveď 16 000; kontext najviac šesť dokončených dvojíc / 24 000 znakov. Čiastočné či chybné odpovede nie sú dokončeným kontextom. AI odpovede naďalej overuj.

Obnova prijíma iba samostatné zálohy schémy 9. Starší originál uchovaj. Vlastnú zálohu schémy 6 prevedieš tak, že vytvoríš samostatnú kópiu, otvoríš ju v novej aplikácii cez --data na migráciu pri štarte a vyexportuješ novú zálohu cez Create backup. Kvôli prevodu nenahrádzaj pracovnú databázu. Migrácia neobnoví chaty zo starých verzií bez ukladania.
