# Plánované místní zálohy

[English](../SCHEDULED_BACKUPS.md) · [Čeština](SCHEDULED_BACKUPS.md) · [Slovenčina](../sk/SCHEDULED_BACKUPS.md) · [Русский](../ru/SCHEDULED_BACKUPS.md)

Funkce je implementovaná v aktuální větvi a zatím není vydaná. Vydaná verze zůstává v0.17.0; schéma SQLite zůstává **10**. Ruční záloha a obnova fungují samostatně.

V Settings přejdi na Daily local backups. Vyber existující místní složku, zapni Enable daily backups a klikni na Save backup schedule (popisky se překládají podle jazyka rozhraní). Plán má vlastní uložení a načtení; uložení studijního/AI formuláře plán neukládá. Automatika začne až po výslovném zapnutí a uložení. Vypnutí uloženého plánu zastaví další automatické zálohy.

Aplikace kontroluje plán po spuštění a přibližně jednou za minutu během běhu. Samostatný pomocný proces vytvoří nejvýše jednu zálohu za aktuální místní den. Zavřená aplikace úlohy nespouští; po více dnech vznikne jedna aktuální kopie. Změna složky ani vypnutí/zapnutí nepřidá další kopii po zaznamenaném úspěchu téhož dne. Po vrácení hodin se čeká na den po posledním úspěchu. Retry backup ověřuje, zda je záloha potřeba; další ruční kopii vytvoří Create backup.

Kopírují se potvrzená data SQLite, včetně uložených kontrolních bodů soustředění, do stávajícího samostatného formátu záloh. Neuložené koncepty ani čas od posledního kontrolního bodu nejsou zahrnuté. Soubory se nepřepisují ani nemažou. Jedinečné názvy začínají `SOSkuska-auto-`; staré kopie a volné místo spravuj sám. Kopie nejsou šifrované a neodesílají se do cloudu.

Pro databázi běží jediný pomocný proces denní zálohy. Jiné okno počká a zkontroluje stav znovu; zastaralý plán nepřepíše novější nastavení. Záznam úspěchu na pozadí nezneplatní rozepsaný formulář. Načtení vyžaduje potvrzení nahrazení upraveného konceptu; chyby uložení/načtení jej zachovají. Chyba zůstává viditelná po navigaci. Zavření během úlohy zachová aktuální stránku i koncepty a ukáže oznámení dole v okně. Počkej na dokončení; běžné studium může pokračovat.

Po chybě se akce opakuje asi za patnáct minut; Retry backup vyvolá dřívější kontrolu. Ověř složku, oprávnění a volné místo. Procesy mají časové limity. Pád mezi zveřejněním úplné kopie a zapsáním potvrzení může při opakování vytvořit další platnou kopii; aplikace ji ponechá. Nejde o záruku při výpadku proudu.

Místní plán a záznam úspěchu jsou vedle databáze v `<database>.backup-plan.json`, se zámkem `<database>.backup-plan.lock`. Zápis atomicky nahrazuje soukromý dočasný soubor; poškozené nastavení vypne automatiku do výslovné opravy. Zámky za běhu nemaž. Plán není uvnitř exportu SQLite: obnova na jiném počítači automatiku nezapne. Obnova již nastavené databáze zachová plán tohoto počítače. Samotné přesunutí/kopie databáze na novou cestu vyžaduje nové zapnutí. Migrace schématu není potřeba.

Vývoj: `automatic_backup.py` řeší validaci, identitu plánu, záznam úspěchu a zámek. `scheduled_backups.py` řídí rozhraní na hlavním vlákně a pomocný proces se souborovým výstupem; `backup_worker.py automatic` pracuje bez Tk. `tests/test_automatic_backup.py` a `check_scheduled_backups.py` ověřují ukládání, souběh, chyby, GUI a nový proces v [kontejneru](CONTAINER_TESTS.md). Windows CI kontroluje přibalený pomocný program se složkou Unicode; nenahrazuje ruční kontrolu čistého počítače a hardwaru.
