# Plánované miestne zálohy

[English](../SCHEDULED_BACKUPS.md) · [Čeština](../cs/SCHEDULED_BACKUPS.md) · [Slovenčina](SCHEDULED_BACKUPS.md) · [Русский](../ru/SCHEDULED_BACKUPS.md)

Plánované miestne zálohy sú dostupné vo **v0.18.0**. Schéma SQLite zostáva **10**. Ručná záloha a obnova fungujú samostatne.

V Settings prejdi na Daily local backups. Vyber existujúci miestny priečinok, zapni Enable daily backups a klikni na Save backup schedule (popisky sa prekladajú podľa jazyka rozhrania). Plán má vlastné uloženie a načítanie; uloženie študijného/AI formulára plán neukladá. Automatika začne až po výslovnom zapnutí a uložení. Vypnutie uloženého plánu zastaví ďalšie automatické zálohy.

Aplikácia kontroluje plán po spustení a približne raz za minútu počas behu. Samostatný pomocný proces vytvorí najviac jednu zálohu za aktuálny miestny deň. Zatvorená aplikácia úlohy nespúšťa; po viacerých dňoch vznikne jedna aktuálna kópia. Zmena priečinka ani vypnutie/zapnutie nepridá ďalšiu kópiu po zaznamenanom úspechu toho istého dňa. Po vrátení hodín sa čaká na deň po poslednom úspechu. Retry backup overuje, či je záloha potrebná; ďalšiu ručnú kópiu vytvorí Create backup.

Kopírujú sa potvrdené dáta SQLite, vrátane uložených kontrolných bodov sústredenia, do existujúceho samostatného formátu záloh. Neuložené koncepty ani čas od posledného kontrolného bodu nie sú zahrnuté. Súbory sa neprepisujú ani nemažú. Jedinečné názvy začínajú `SOSkuska-auto-`; staré kópie a voľné miesto spravuj sám. Kópie nie sú šifrované a neodosielajú sa do cloudu.

Pre databázu beží jediný pomocný proces dennej zálohy. Iné okno počká a skontroluje stav znovu; zastaraný plán neprepíše novšie nastavenia. Záznam úspechu na pozadí nezneplatní rozpísaný formulár. Načítanie vyžaduje potvrdenie nahradenia upraveného konceptu; chyby uloženia/načítania ho zachovajú. Chyba zostáva viditeľná po navigácii. Zatvorenie počas úlohy zachová aktuálnu stránku aj koncepty a ukáže oznámenie dole v okne. Počkaj na dokončenie; bežné štúdium môže pokračovať.

Po chybe sa akcia opakuje asi o pätnásť minút; Retry backup vyvolá skoršiu kontrolu. Over priečinok, oprávnenia a voľné miesto. Procesy majú časové limity. Pád medzi zverejnením úplnej kópie a zápisom potvrdenia môže pri opakovaní vytvoriť ďalšiu platnú kópiu; aplikácia ju ponechá. Nejde o záruku pri výpadku prúdu.

Miestny plán a záznam úspechu sú vedľa databázy v `<database>.backup-plan.json`, so zámkom `<database>.backup-plan.lock`. Zápis atomicky nahrádza súkromný dočasný súbor; poškodené nastavenia vypnú automatiku do výslovnej opravy. Zámky počas behu nemaž. Plán nie je v exporte SQLite: obnova na inom počítači automatiku nezapne. Obnova už nastavenej databázy zachová plán tohto počítača. Samotné presunutie/kópia databázy na novú cestu vyžaduje nové zapnutie. Migrácia schémy nie je potrebná.

Vývoj: `automatic_backup.py` rieši validáciu, identitu plánu, záznam úspechu a zámok. `scheduled_backups.py` riadi rozhranie na hlavnom vlákne a pomocný proces so súborovým výstupom; `backup_worker.py automatic` pracuje bez Tk. `tests/test_automatic_backup.py` a `check_scheduled_backups.py` overujú ukladanie, súbeh, chyby, GUI a nový proces v [kontajneri](CONTAINER_TESTS.md). Windows CI kontroluje pribalený pomocný program s priečinkom Unicode; nenahrádza ručnú kontrolu čistého počítača a hardvéru.
