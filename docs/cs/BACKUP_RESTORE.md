# Záloha a obnova (v0.9.0)

[English](../BACKUP_RESTORE.md) · [Čeština](BACKUP_RESTORE.md) · [Slovenčina](../sk/BACKUP_RESTORE.md) · [Русский](../ru/BACKUP_RESTORE.md)

## Nevydáno — nastavení a společné datové panely

Plán denních záloh, ruční záloha/obnova a oba importy CSV používají společný vzhled karet, odsazení a zalomené zprávy. Skupiny akcí mají tři sloupce v širokém rozložení, jinak dva. Varování obnovy je nad tlačítkem nevratného potvrzení a Zrušit. Pole náhledu/chyb CSV mají viditelné okraje a vlastní posouvání. Pravidla náhledu, zrušení, atomického zápisu, oddělených procesů, zavření po obnově a bezpečnostní kopie se nemění.

## Vytvoření zálohy

Otevři **Settings → Backup and restore → Create backup**, vyber místní složku a dosud nepoužitý název `.sqlite3`. Počkej na dokončení; existující soubory se nepřepisují. Během kopírování lze aplikaci používat, běžné zavření/Quit počká na dokončení úlohy.

Snímek SQLite obsahuje všechna uložená studijní data, nastavení a místní AI konverzace. Zahrnuje potvrzená WAL data, nikoli neuložené změny, běžící čas, formuláře a dosud neuložený text odpovědi. Nejprve dokonči focus, ulož formuláře a vyřeš neuložené odpovědi. Export je samostatná databáze DELETE, nikoli prostá kopie živého souboru.

## Obnova

1. Dokonči focus a dokonči/zahoď test. Počkej na AI nebo použij Stop; ulož potřebné formuláře a vyřeš odpovědi přes Retry save reply nebo Discard unsaved.
2. Zavři ostatní okna SOSkúška nad stejnou databází, starší verze aplikace a externí SQLite nástroje. Aktuální verze používá sdílený/výhradní zámek; starší aplikace a externí nástroje se tohoto mechanismu neúčastní.
3. V Settings zvol **Choose backup…** a běžný místní samostatný SQLite soubor schématu **10**. Pracovní WAL soubory, cizí, poškozené, neplatné, starší i novější databáze se odmítnou. WAL databázi nejprve exportuj přes Create backup.
4. Soukromá kopie projde kontrolou integrity, struktury, omezení, typů, dat/časových zón, konzistence testů a vazeb. Zkontroluj název a počty. **Cancel** nebo navigace výběr zruší bez změny dat. Pozdější změna zdrojového souboru nezmění ověřenou kopii.
5. **Confirm restore and close** nahradí všechna uložená studijní data, nastavení a konverzace obsahem zálohy. Rozepsané formuláře se ztratí. Ochrany se ověří znovu; editace se zablokuje a databázové callbacky pozastaví.
6. Před nahrazením vznikne bezpečnostní kopie v `backups/` vedle aktivní databáze: `SOSkuska-before-restore-<datum>-<unikátní-id>.sqlite3`. Úspěšná zpráva ukáže přesnou cestu. Jedna transakce zachová ID sekvence a porovná výsledek s ověřenou kopií; chyba před commitem vrátí původní data. Pokud nelze vytvořit bezpečnostní kopii, data se nenahradí.
7. Po skutečném pokusu o obnovu se aplikace zavře i při chybě. Spusť ji znovu stejným `--data` nebo původním způsobem. Záloha může obsahovat rozpracovaný test, ve kterém lze pokračovat. Již vytvořená bezpečnostní kopie zůstane i při pozdější chybě a lze ji obnovit stejným postupem.

## Omezení

Jde o ruční místní zálohy, ne synchronizaci, plánované zálohování, šifrování ani úplnou obnovu po pádu/výpadku proudu. Kopie obsahují soukromá studijní data a AI nastavení; ulož je bezpečně. Běžné studium zůstává offline bez cloudu.

Aktuální schéma je 10; obnova přijímá pouze schéma 10, bez downgradu či automatické migrace. Aktivní databáze s pevnými odkazy se odmítají kvůli spolehlivému zamykání. Aktivní databázi ani její doprovodné soubory nelze použít jako cíl, včetně variant velikosti písmen a Unicode.

Na macOS/Linux vyžaduje atomické zveřejnění bez přepsání podporu pevných odkazů (například běžné místní APFS/ext4). Pokud externí disk zápis odmítne, použij podporovanou místní složku. Windows používá přejmenování bez přepsání. Úlohy běží v pomocných procesech: rozpočet operace 60 sekund, pojistka procesu 90 sekund. Vyhni se síťovým cestám a nevynucuj ukončení. Pokud pomocný proces nečekaně skončí, po spuštění zkontroluj data a bezpečnostní kopie; nelze předpokládat chybu před commitem.

## Uložené konverzace AI Tutor

AI Tutor nyní ukládá konverzace lokálně včetně původního serveru/modelu a stavu odpovědi. Historii lze otevřít bez sítě, výslovně se připojit pro pokračování nebo vybranou konverzaci po potvrzení smazat. Vydáno ve v0.12.0 se schématem 7, které transakčně migruje původní studijní data. [Uložené konverzace AI Tutor](TUTOR_HISTORY.md).

## Obnova soustředění po pádu

v0.17.0 přidává obnovu soustředění po pádu se schématem **10**. Před otevřením původních dat vytvoř zálohu: migrace je transakční, ale v0.16.0 databázi schématu 10 neotevře. [Obnova soustředění po pádu](FOCUS_RECOVERY.md).

## Plánované místní zálohy

Plánované místní zálohy jsou dostupné ve **v0.18.0**. Schéma SQLite zůstává **10**. Ruční záloha a obnova fungují samostatně. [Plánované místní zálohy](SCHEDULED_BACKUPS.md).
