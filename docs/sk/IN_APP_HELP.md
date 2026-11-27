# Pomocník v aplikácii

[English](../IN_APP_HELP.md) · [Čeština](../cs/IN_APP_HELP.md) · [Slovenčina](IN_APP_HELP.md) · [Русский](../ru/IN_APP_HELP.md)

SOSkúška má vstavanú stránku Pomocník s krátkymi návodmi ku všetkým častiam aplikácie. Funguje offline, nič neodosiela a nikdy nemení vaše údaje.

## Otvorenie pomocníka

- Zvoľte tlačidlo **?** vedľa **Nastavenia** dole na bočnom paneli. V zbalenom paneli je pod ikonou Nastavenia.
- Na ľubovoľnej stránke stlačte **F1**. Na Macu funguje aj **Cmd+?**.

Pomocník sa otvorí na téme stránky, ktorú ste práve používali: napríklad z Kartičiek ukáže *Kartičky a opakovanie*, z banky otázok *Banka otázok*. Keď pomocníka otvoríte znova, kým ho čítate, zostanete na rovnakom mieste.

## Používanie

- Vyberte tému zo zoznamu. V širokom okne je zoznam vedľa článku, v menšom okne nad ním.
- Písaním do **Hľadať v pomocníkovi…** zoznam zúžite. Hľadanie nerozlišuje veľké písmená ani diakritiku (`zalohy` nájde *Zálohy*) a v téme sa musí objaviť každé zadané slovo. **Ctrl+K** (na Macu Cmd+K) prejde do poľa hľadania a **Esc** ho vymaže.
- Názvy tlačidiel a polí sú v úvodzovkách presne tak, ako sa volajú vo zvolenom jazyku rozhrania.
- **Otvoriť: …** na konci témy prejde na opisovanú stránku; **Pozri aj** odkazuje na súvisiace témy.

**← Späť: …** hore vás vráti na stránku, odkiaľ ste prišli, presne tak, ako ste ju opustili, na rovnakom mieste posúvača. Neuložené rozpracované texty zostanú zachované a pri návrate touto cestou aj náhľad importu CSV a vybraná záloha; prechod z Pomocníka na inú stránku ich ako zvyčajne zruší.

## Témy

Začíname · Prehľad a sústredenie · Predmety a dátumy skúšok · Banka otázok · Cvičné testy · Kartičky a opakovanie · Štatistiky · AI Tutor · Návrhy AI z poznámok · Import z CSV · Nastavenia a jazyk · Zálohy a obnova · Vaše údaje a súkromie · Klávesové skratky · Riešenie problémov.

Pomocník sa po reštarte riadi jazykom rozhrania zvoleným v Nastaveniach (angličtina, čeština, slovenčina alebo ruština). Podrobnou referenciou zostávajú návody v priečinku `docs/`.

## Pre vývojárov

Témy sú v `soskuska/i18n/help-<en|cs|sk|ru>.json`. `help_content.py` ich overuje, pripravuje text na hľadanie a priraďuje stránkam témy; `help_page.py` ich vykresľuje a vytvára sa až pri prvom použití, aby nespomaľoval štart. Každá téma má `id`, `title`, `summary`, voliteľnú `page` na otvorenie, `blocks` (`heading`, `text`, `steps` alebo `bullets`) a `related` s id súvisiacich tém. Doslovné popisky rozhrania označte ako `**Popisok**`.

`tests/test_help.py` vyžaduje rovnakú štruktúru všetkých štyroch súborov, aby každý `**Popisok**` bol skutočným popiskom v katalógu rozhrania daného jazyka, a overuje hľadanie; `check_help.py` testuje stránku v štyroch jazykoch a pri 150 %. Pri zmene funkcie alebo popisku upravte všetky štyri súbory spoločne.
