# Zlepšenia AI: vysvetlenie otázky

[English](../AI_IMPROVEMENTS.md) · [Čeština](../cs/AI_IMPROVEMENTS.md) · [Slovenčina](AI_IMPROVEMENTS.md) · [Русский](../ru/AI_IMPROVEMENTS.md)

Rozhodnutie o pláne · 26. novembra 2026. Základ: v0.24.0, schéma 10. Ide o budúcu prácu; funkcia nie je implementovaná a toto plánovacie PR neschvaľuje implementáciu, zlúčenie ani vydanie.

## Cieľ

Prepojiť dokončené výsledky Practice s AI Tutorom cez **Vysvetliť túto otázku**. Študent si prezrie jednu uloženú otázku, výslovne pripraví koncept a použije doterajšie Pripojiť a Odoslať. Bežné štúdium zostáva offline, Ollama je voliteľná.

## Implementačné kroky

### 1. Vymedziť prvú funkciu

Podporovať jednu otázku z dokončeného výsledku vrátane otvorenia z histórie. Nepridávať akciu do bežiaceho testu, prípravy ani banky otázok. AI vysvetľuje, nemení správnu odpoveď, skóre, obsah ani štatistiky. Uložený kľúč nie je zárukou vecnej správnosti. Študijné režimy, generovanie z poznámok, prílohy a formátovanie patria do ďalších PR.

### 2. Zostaviť nemenný obmedzený prompt

Použiť snímku pokusu podľa `(attempt_id, position)`, nie `question_id` alebo dnešnú banku otázok. Znova overiť existenciu a dokončenie. Kopírovať otázku, možnosti A–D, vybranú odpoveď alebo Nezodpovedané, správnu odpoveď a uložené vysvetlenie. Pridať stručnú žiadosť o odôvodnenie a vysvetlenie rozdielu, prípadne správneho postupu pri nezodpovedanej otázke. Chyba čítania či chýbajúci záznam ponúkne opakovanie bez straty obrazovky. Úprava/vymazanie zdroja nesmie obsah zmeniť.

### 3. Zachovať limit vstupu

Tutor povoľuje 4000 znakov; platná otázka s možnosťami a vysvetlením môže byť dlhšia. Počítať celý zostavený prompt vrátane popisov a inštrukcií. Pri prekročení nič nepripraviť ani neposlať, ukázať dĺžku a limit a ponechať výsledok použiteľný. Uviesť, že skratka pre celý kontext túto položku zatiaľ nezvládne. Nič potichu neskracovať a nezvyšovať doterajšie limity. Prílohy pre dlhý kontext odložiť; otestovať presnú hranicu aj prekročenie.

### 4. Pridať miestny náhľad výsledku

Pri každej dokončenej otázke ponúknuť akciu dostupnú aj pri dlhom texte a malom okne. Ukázať presný prompt a zdieľaný obsah, Pripraviť v Tutorovi a Zrušiť. Náhľad nevykonáva HTTP, neukladá konverzáciu, nemení výsledok a nepripája sa. Callback zachová pôvodnú identitu pokusu/pozície a odmietne zastarané či skryté akcie; pred odovzdaním spôsobilosť znova overiť.

### 5. Odovzdať bez straty konverzácie

Pripraviť iba v nečinnom Tutorovi bez neuloženej odpovede a čakajúcej obnovy/potvrdenia, v čistom Novom chate s prázdnym promptom. Existujúci chat, koncept a úlohu zachovať; vysvetliť, ako prácu dokončiť alebo výslovne použiť doterajší potvrdený Nový chat a potom akciu zopakovať. Automaticky nič nemazať, neotvárať inú históriu, nemeniť server/model, nezastavovať úlohu ani neplánovať odložené odoslanie. Úspešný koncept zobraziť v Tutorovi a umožniť úpravu. Opakovaná akcia nesmie duplikovať text ani nahradiť zmenený koncept.

### 6. Použiť doterajšie Pripojiť/Odoslať

Server, model a jazyk odpovede zostávajú viditeľné. Pripojenie je výslovné; generovanie spustí iba Odoslať. Prompt uložiť bežnou transakciou čakajúcej otázky pred HTTP, takže história obsahuje dodanú snímku ako text otázky. Nová tabuľka kontextu ani migrácia sa neplánuje. Zachovať Stop, čiastočné odpovede, opakovanie zápisu, obnovu, hranice kontextu a vlastníctvo servera/modelu. Nerozširovať automatické prílohy ani sieťového klienta. Ak kód vyžaduje schému, najprv upraviť plán.

### 7. Preložiť a overiť ovládanie

Doplniť angličtinu, češtinu, slovenčinu a ruštinu; používateľský text nemeniť. Jazyk odpovede je nezávislý od rozhrania. Pri Automaticky požiadať model o jazyk dodanej otázky a vyhodnotiť zmiešané jazyky; výslovná voľba zostáva používateľským riadením, rozpoznanie modelu nie je zaručené. Overiť klávesnicu, čitateľnosť, chyby a dosah akcií pri 1024×700/1440×900, Light/Dark/System a počiatočnej mierke 100/150 %. Skrytá aktualizácia nesmie zmeniť posun ani koncept inej stránky.

### 8. Otestovať správanie a chyby

Čisté testy: zostavenie snímky, správna/chybná/žiadna odpoveď, hranice, neplatná identita a stav. GUI: história po úprave/vymazaní zdroja, Zrušiť, žiadna sieť pred Pripojiť/Odoslať, odmietnutie zaneprázdneného či rozpísaného Tutora, idempotentné odovzdanie, zlyhanie prvého zápisu, stream/Stop a opakovanie uloženia bez duplicít. FakeOllama cez loopback overí požiadavku a persistenciu, nie kvalitu odpovede. Použiť dočasné dáta a kontajnerové GUI.

### 9. Dodať jedno sústredené PR

Z aktuálnej main založiť napr. `feature/ai-question-explanation`. Najprv čistý zostavovač, potom náhľad, chránené odovzdanie, integrácie a dokumentáciu; závislé commity držať v jednom PR. Vykonať vhodné jednotkové/kontajnerové kontroly a CI, nezávislú revíziu Sol na medium a opravy aj opätovnú revíziu na rovnakej vetve. Aktualizovať Tutor, históriu testov, architektúru a všetky štyri jazykové verzie. Verziu nemeniť do schválenia vydania.

### 10. Vyhodnotiť a rozhodnúť o pokračovaní

Pred ukážkou vyskúšať skutočný model na dočasných správnych, chybných, nezodpovedaných, nejednoznačných a viacjazyčných otázkach. Zapísať verziu Ollamy/modelu, hardvér, jazyk, odozvu/Stop a užitočnosť vysvetlenia. Oddeliť to od automatických testov. Finálna akceptácia a prezentácia stále zostávajú. Zlúčenie a vydanie potrebujú vlastné rozhodnutie; budúce funkčné vydanie obvykle použije ďalšiu voľnú vedľajšiu verziu 0.x, ktorú tento plán nerezervuje.

## Pravdepodobné miesta zmien

Pri implementácii overiť najmä `soskuska/practice_page.py` (`render_result`), nový čistý modul napr. `soskuska/question_explanation.py`, odovzdanie v `soskuska/app.py`, prípravu konceptu v `soskuska/tutor_page.py`, doterajšie čítacie API `soskuska/storage.py`, prípadnú obmedzenú jazykovú inštrukciu v `soskuska/tutor.py`, štyri katalógy `soskuska/i18n/`, testy a `tools/run_checks.py`. Nepridávať nesúvisiaci refaktoring, nastavenia ani migrácie.

## Podmienky dokončenia

Hotovo znamená: miestny náhľad jednej dokončenej snímky, zachovaná existujúca práca, výslovné Odoslať vytvorí bežný uložený ťah, chyby/Stop sa dajú obnoviť, skóre a história sa nemenia, revízia/testy prejdú a dokumentácia uvádza obmedzenia. Odmietnutie príliš dlhej otázky je výslovné obmedzenie prvej verzie, nie tiché skrátenie.

## Ďalšie zlepšenia AI

Po samostatnom určení priorít: (A) jednoduchšie vysvetlenie, nápoveda a skúšanie; (B) natívne zoznamy, nadpisy a bloky kódu; (C) generovanie otázok/kartičiek z vložených poznámok s validáciou, upraviteľným náhľadom a výslovným atomickým uložením. Generovanie potrebuje vlastný plán chybných výstupov, duplicít, opakovania a kontroly obsahu. RAG, automatický kontext celej databázy a cloudový záložný server sem nepatria.
