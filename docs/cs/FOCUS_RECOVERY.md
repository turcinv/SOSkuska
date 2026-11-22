# Obnova soustředění po pádu

[English](../FOCUS_RECOVERY.md) · [Čeština](FOCUS_RECOVERY.md) · [Slovenčina](../sk/FOCUS_RECOVERY.md) · [Русский](../ru/FOCUS_RECOVERY.md)

Tato větev přidává obnovu soustředění k vydané základní verzi v0.16.0. Funkce zatím není vydaná a používá schéma **10**. Před otevřením původních dat vytvoř zálohu: migrace je transakční, ale v0.16.0 databázi schématu 10 neotevře.

Start Studying nejprve vytvoří rozpracovaný záznam. Aplikace ukládá celé uplynulé sekundy přibližně každých pět sekund a ihned při Pause. Zachová původní název předmětu, cíl a ověřený čas; hodnotu monotónních hodin mezi procesy nepřenáší.

Po pádu nebo vynuceném ukončení Dashboard nabídne Recover paused, Discard checkpoint a Refresh (popisky se překládají podle jazyka rozhraní). Obnova začíná pozastavená, zachová původní cíl i po změně Settings a nepočítá dobu zavření jako studium. Resume pokračuje; Finish uloží čas. Rozpracovaný čas není ve Statistics. Zahození vyžaduje druhé potvrzení a nepřidává historii. Navigace, Escape, Refresh a Recover potvrzení ruší. Chyba čtení vypne zastaralé akce do úspěšného Refresh.

Trvalý soubor `.focus.lock` dovolí vlastnictví jedinému oknu. Jiné okno může kontrolní bod zobrazit, ale za běhu vlastníka jej neobnoví ani nezahodí. Po zavření vlastníka použij Refresh. Zámky nemaž ručně; ukončení procesu uvolní zámek operačního systému.

Zápis čeká na SQLite přibližně nejvýše 200 ms. Neúspěšný kontrolní bod nebo Finish pozastaví čas, vypne Resume a ponechá čas v paměti. Opakuj uložení přes Finish. Pokyn je u časovače a v postranním panelu se na ostatních stránkách ukáže Focus needs saving; otevře Dashboard. Neúspěšné zavření ponechá Dashboard otevřený. Běžné zavření čas uloží; při chybě ukládání aplikaci neukončuj násilně.

Dokončení vloží studijní relaci a označí kontrolní bod v jedné transakci; opakování nevytvoří druhou relaci. Nula sekund nepřidá statistiku. Čas patří místnímu dni dokončení, i po obnově; přes půlnoc se nedělí. Přejmenování/smazání předmětu zachová původní historický název; smazání odstraní jen živý odkaz.

Záloha obsahuje uložené rozpracované, dokončené i zahozené záznamy, nikoli čas od posledního zápisu a neuložené koncepty. Před obnovou vyřeš rozpracované soustředění cílové databáze. Záloha schématu 10 s rozpracovaným záznamem nabídne obnovení po spuštění. Obnova přijímá jen samostatné zálohy schématu 10; staré zálohy nemigruje. Starší databázi nejprve otevři jako samostatnou kopii v této verzi a vytvoř novou zálohu.

Násilné ukončení může ztratit přibližně posledních pět sekund a zlomek sekundy; zpožděná smyčka nebo chyba zápisu mohou ztrátu zvětšit. Nejde o záruku při výpadku proudu, synchronizaci ani průběžnou zálohu.

Použij [vývojové prostředí](DEVELOPMENT.md), oddělená data `--data .local-data/dev.sqlite3` a [kontejnerové kontroly](CONTAINER_TESTS.md). `tests/test_focus.py` ověřuje migraci, návrat při chybě, vlastnictví, smrt procesu, atomické dokončení a zálohy. `check_focus_recovery.py` ukončí testovací GUI a v nových procesech ověří obnovu, chyby, potvrzení a zavření. Windows CI otevírá přenosný program s kontrolním bodem. Linux/Xvfb nenahrazuje nativní macOS ani ruční přejímku hardwaru Windows.
