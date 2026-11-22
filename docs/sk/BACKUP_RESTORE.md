# Záloha a obnova (v0.9.0)

[English](../BACKUP_RESTORE.md) · [Čeština](../cs/BACKUP_RESTORE.md) · [Slovenčina](BACKUP_RESTORE.md) · [Русский](../ru/BACKUP_RESTORE.md)

## Vytvorenie zálohy

Otvor **Settings → Backup and restore → Create backup**, vyber miestny priečinok a doteraz nepoužitý názov `.sqlite3`. Počkaj na dokončenie; existujúce súbory sa neprepisujú. Počas kopírovania možno aplikáciu používať, bežné zatvorenie/Quit počká na dokončenie úlohy.

Snímka SQLite obsahuje všetky uložené študijné údaje, nastavenia a miestne AI konverzácie. Zahŕňa potvrdené WAL údaje, nie neuložené zmeny, bežiaci čas, formuláre a dosiaľ neuložený text odpovede. Najprv dokonči focus, ulož formuláre a vyrieš neuložené odpovede. Export je samostatná databáza DELETE, nie obyčajná kópia živého súboru.

## Obnova

1. Dokonči focus a dokonči/zahoď test. Počkaj na AI alebo použi Stop; ulož potrebné formuláre a vyrieš odpovede cez Retry save reply alebo Discard unsaved.
2. Zatvor ostatné okná SOSkúška nad rovnakou databázou, staršie verzie aplikácie a externé SQLite nástroje. Aktuálna verzia používa zdieľaný/výhradný zámok; staršie aplikácie a externé nástroje sa tohto mechanizmu nezúčastňujú.
3. V Settings zvoľ **Choose backup…** a bežný miestny samostatný SQLite súbor schémy **10**. Pracovné WAL súbory, cudzie, poškodené, neplatné, staršie aj novšie databázy sa odmietnu. WAL databázu najprv exportuj cez Create backup.
4. Súkromná kópia prejde kontrolou integrity, štruktúry, obmedzení, typov, dátumov/časových pásiem, konzistencie testov a väzieb. Skontroluj názov a počty. **Cancel** alebo navigácia výber zruší bez zmeny údajov. Neskoršia zmena zdrojového súboru nezmení overenú kópiu.
5. **Confirm restore and close** nahradí všetky uložené študijné údaje, nastavenia a konverzácie obsahom zálohy. Rozpísané formuláre sa stratia. Ochrany sa overia znovu; editácia sa zablokuje a databázové callbacky pozastavia.
6. Pred nahradením vznikne bezpečnostná kópia v `backups/` vedľa aktívnej databázy: `SOSkuska-before-restore-<dátum>-<jedinečné-id>.sqlite3`. Úspešná správa ukáže presnú cestu. Jedna transakcia zachová ID sekvencie a porovná výsledok s overenou kópiou; chyba pred commitom vráti pôvodné údaje. Ak nemožno vytvoriť bezpečnostnú kópiu, údaje sa nenahradia.
7. Po skutočnom pokuse o obnovu sa aplikácia zatvorí aj pri chybe. Spusť ju znovu s rovnakým `--data` alebo pôvodným spôsobom. Záloha môže obsahovať rozpracovaný test, v ktorom možno pokračovať. Už vytvorená bezpečnostná kópia zostane aj pri neskoršej chybe a možno ju obnoviť rovnakým postupom.

## Obmedzenia

Ide o ručné miestne zálohy, nie synchronizáciu, plánované zálohovanie, šifrovanie ani úplnú obnovu po páde/výpadku prúdu. Kópie obsahujú súkromné študijné údaje a AI nastavenia; ulož ich bezpečne. Bežné štúdium zostáva offline bez cloudu.

Aktuálna schéma je 10; obnova prijíma iba schému 10, bez downgradu či automatickej migrácie. Aktívne databázy s pevnými odkazmi sa odmietajú kvôli spoľahlivému zamykaniu. Aktívnu databázu ani sprievodné súbory nemožno použiť ako cieľ, vrátane variantov veľkosti písmen a Unicode.

Na macOS/Linux vyžaduje atomické zverejnenie bez prepísania podporu pevných odkazov (napríklad bežné miestne APFS/ext4). Ak externý disk zápis odmietne, použi podporovaný miestny priečinok. Windows používa premenovanie bez prepísania. Úlohy bežia v pomocných procesoch: rozpočet operácie 60 sekúnd, poistka procesu 90 sekúnd. Vyhni sa sieťovým cestám a nevynucuj ukončenie. Ak pomocný proces nečakane skončí, po spustení skontroluj údaje a bezpečnostné kópie; nemožno predpokladať chybu pred commitom.

## Uložené konverzácie AI Tutor

AI Tutor teraz ukladá konverzácie lokálne vrátane pôvodného servera/modelu a stavu odpovede. Históriu možno otvoriť bez siete, výslovne sa pripojiť na pokračovanie alebo vybranú konverzáciu po potvrdení zmazať. Vydané vo v0.12.0 so schémou 7, ktorá transakčne migruje pôvodné študijné údaje. [Uložené konverzácie AI Tutor](TUTOR_HISTORY.md).

## Obnova sústredenia po páde

v0.17.0 pridáva obnovu sústredenia po páde so schémou **10**. Pred otvorením pôvodných dát vytvor zálohu: migrácia je transakčná, ale v0.16.0 databázu schémy 10 neotvorí. [Obnova sústredenia po páde](FOCUS_RECOVERY.md).

## Plánované miestne zálohy

Funkcia je implementovaná v aktuálnej vetve a zatiaľ nie je vydaná. Vydaná verzia zostáva v0.17.0; schéma SQLite zostáva **10**. Ručná záloha a obnova fungujú samostatne. [Plánované miestne zálohy](SCHEDULED_BACKUPS.md).
