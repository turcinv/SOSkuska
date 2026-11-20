# Historie změn

[English](../../CHANGELOG.md) · [Čeština](CHANGELOG.md) · [Slovenčina](../sk/CHANGELOG.md) · [Русский](../ru/CHANGELOG.md)


## Nevydané

Flashcards nyní podporuje import UTF-8 CSV do existujícího balíčku: šablonu s hlavičkou, stránkovaný náhled, odmítnutí přesných duplicit a jedno atomické uložení. Maximum 2 MiB / 500 záznamů. Nové kartičky jsou ihned splatné; původní termíny a historie hodnocení zůstávají zachované. Schéma zůstává 6. [Import kartiček z CSV](FLASHCARD_CSV_IMPORT.md).

## 0.10.0 — 2026-11-19

Banka otázek nyní podporuje import UTF-8 CSV do existujícího předmětu: šablona s hlavičkou, stránkovaný náhled, odmítnutí přesných duplicit a jedno atomické uložení. Maximum 2 MiB / 500 záznamů; seznam ukazuje 50 otázek na stránku. Schéma zůstává 6. [Import otázek z CSV](QUESTION_CSV_IMPORT.md).

csv_import.py ověřuje omezené normalizované záznamy; csv_import_worker.py izoluje parsování, kontrolu pouze pro čtení, uložení a šablonu s výstupem do souboru. Store.open_existing používá mode=ro/rw bez vytváření či migrace. Store.import_questions znovu ověří dávku pod BEGIN IMMEDIATE a uloží témata/otázky jednou transakcí. Úspěšná dávka se zneplatní před čtením přehledů; opakovaná obnova nic neimportuje. Stránkování filtruje celý seznam a pak vykreslí 50 karet.

Závěrečná kontrola opravila riziko starého náhledu: výběr nového souboru okamžitě zruší starou dávku a ověření předmětu neblokuje Tk. Ověření: 188 jednotkových testů, jedenáct nativních kontrol během implementace a opakované ověření opravy, nezávislá kontrola Sol i opětovná kontrola a všechny čtyři CI úlohy funkčního PR prošly.

## 0.9.0 — 2026-11-19

Settings nyní nabízí ruční místní zálohu a ověřenou obnovu s bezpečnostní kopií před nahrazením. Schéma zůstává 6. Obnova zavře aplikaci; potom ji spusť znovu. Viz [Záloha a obnova](BACKUP_RESTORE.md).

backup.py a backup_validation.py ověřují soukromé samostatné snímky a aplikační hodnoty; řádky nahrazují v jedné transakci bez převzetí cizího DDL. database_lock.py drží sdílené zámky Store a výhradní zámek obnovy (flock / Windows LockFileEx). backup_worker.py běží v odděleném procesu; backup_panel.py přes Tk čte dočasný výstupní soubor, takže nehrozí plná roura ani finalizace Tk z pracovního vlákna. Při obnově se Store zavře a periodické callbacky pozastaví. Bezpečnostní kopie vznikne pod zápisovým zámkem; před commitem se ověří konečné řádky a ID sekvence.

Ověření: 156 jednotkových testů a deset nativních kontrol na macOS s dočasnými databázemi. CI funkčního PR prošlo na Ubuntu, Windows a macOS; všech deset GUI kontrol prošlo na Ubuntu/Xvfb. Nálezy nezávislé kontroly Sol byly opravené a znovu ověřené.

## 0.8.1 — 2026-11-18

Angličtina je nyní hlavním jazykem dokumentace v kořeni repozitáře a v `docs/`. Česká dokumentace je zachovaná v `docs/cs/`, vedle slovenské a ruské verze. Odkazy přepínají mezi odpovídajícími stránkami všech čtyř jazyků; AGENTS.md popisuje novou strukturu. Mění se pouze dokumentace, aplikace i schéma databáze zůstávají stejné.

## 0.8.0 — 2026-11-18

Nastavení se ukládá do stejné databáze jako studijní data. Nastavení se ukládá transakčně ve schématu 6 s ochranou před přepsáním změn jiného okna. Migrace z verze 5 zachová všechny předchozí tabulky i data; starší aplikace novější schéma odmítne otevřít.

V **Settings** nastav délku příštího focus sezení (1–180 minut, výchozí 15), denní cíl (1–1 440 minut, výchozí 60), URL Ollamy, preferovaný model a jazyk AI odpovědi. **Save settings** uloží a použije všechny hodnoty; rozepsané změny přežijí přepnutí obrazovky, ale ne zavření aplikace. Probíhající i pozastavené sezení si zachová původní délku. Cíl se změní hned, historický čas se nepřepočítává.

**Use Tutor choices** jen zkopíruje do formuláře aktuální volby AI Tutor; potom použij Save settings. Přímé změny v AI Tutor jsou dočasné. Uložení, spuštění ani návrat na obrazovku nevytváří síťové spojení. Připoj se výslovně přes Connect / refresh. Nedostupný preferovaný model se nenahradí jiným bez výběru uživatele. Jazyk platí pro AI odpovědi, nikoli rozhraní aplikace.

Při aktivním AI požadavku nejprve počkej nebo použij Stop, než změníš AI preference. Studijní hodnoty lze uložit dál. Pokud chat patří jinému serveru, nejprve jej vymaž přes New chat a potvrzení. Zapamatování právě připojeného serveru jeho chat zachová. Chat se při zavření stále ztratí.

Chyba zápisu ani konflikt s jiným oknem neodstraní rozepsané hodnoty. Před Reload si je zkopíruj; u změněného formuláře je nutné potvrdit nahrazení druhým kliknutím. Změny jiného okna se nepoužijí živě: v tomto okně je použije Save nebo restart. Save použije všechny načtené hodnoty, včetně AI nastavení z druhého okna, proto mohou platit výše uvedené ochrany. Neplatná uložená nastavení zobrazí bezpečné výchozí hodnoty; opraví se až výslovným Save.

Nastavení je místní pro vybranou databázi (`--data`), bez synchronizace a šifrování. Chybí volba vzhledu, překlady UI, zálohy a ukládání AI konverzací.

Při změně serveru se preferovaný model vybere znovu; obnovení stejného serveru zachová ruční výběr. Ověření: 126 jednotkových testů a devět nativních kontrol s dočasnými daty; CI pro funkční PR prošlo na třech systémech a GUI na Ubuntu. Nezávislá kontrola Sol a opětovná kontrola oprav nenašly zbývající problémy.

## 0.7.0 — 2026-11-18

V AI Tutor připoj vlastní Ollama server přes Connect / refresh, vyber model a jazyk odpovědi a zadej otázku. Odpověď přichází průběžně; Stop ji zastaví. Ostatní obrazovky zůstávají použitelné během generování i bez Ollamy. Chat je pouze pro aktuální spuštění aplikace, neukládá se do databáze.

tutor_page.py drží session chat a widgety. tutor.py sestavuje omezený kontext a spouští daemon pracovní vlákno; výsledky předává přes queue, zpracovanou Tk after každých 50 ms. ollama_client.py používá standardní http.client/ssl, GET /api/tags a streamované POST /api/chat. Pracovní vlákna nevolají Tk ani SQLite. Ukončení přeruší síťový úkol bez čekání v UI; neúspěšné uložení focus sezení dál brání zavření. Schéma zůstává 5, nové externí závislosti nejsou potřeba.

23 nových testů a check_tutor.py používají výhradně fake Ollama server na loopbacku a dočasná data. Ověřují protokol, Unicode, chybné odpovědi, přerušení streamu/TLS handshake, limity, kontext, navigaci a zavření při generování. Celkem 107 jednotkových testů a osm GUI kontrol. Tyto testy neověřují kvalitu skutečného modelu ani jeho hardwarové nároky.

## 0.6.2 — 2026-11-17

Discard test získá zápisový zámek a potom ověří termín. Pokud mezitím vypršel, pokus i odpovědi se zachovají jako dokončený výsledek místo smazání; selhání zápisu ponechá původní data pro opakování. Pokud jiná instance rozpracovaný test odstraní, Finish zastaví opakování a obnoví nastavení. Chyby SQLite se dál dají opakovat; po chybě načtení nastavení použij Refresh subjects nebo návrat na obrazovku.

Editor otázek ukládá kopii původního obsahu. Při uložení ji porovná s aktuální otázkou pod zápisovým zámkem. Novější text, možnosti, správná odpověď, obtížnost, téma nebo vysvětlení se nepřepíšou starým formulářem. Při konfliktu zůstane rozepsaný obsah; před opětovným otevřením Edit si jej zkopíruj a změny spoj s aktuální verzí. Schéma databáze zůstává 5.

Formulář New deck obnoví nabídku předmětů při návratu, přes Refresh i před uložením, bez ztráty názvu a popisu. Přejmenovaný předmět zůstane vybraný podle ID. Pokud byl vybraný předmět smazán, Choose a subject vyžaduje výslovně zvolit jiný; formulář jej sám nenahradí jiným existujícím předmětem.

Nových osm jednotkových testů pokrývá termíny včetně čekání na zámek, rollback, konflikty otázek a odlišení odstraněného testu. check_state_fixes.py navíc ověřuje skutečné formuláře, zachování rozepsaného obsahu, konflikt a nové načtení, zachování výsledku po termínu a obnovu po odstranění z jiné instance. Celkem 84 jednotkových testů a sedm nativních kontrol s dočasnými daty.

## 0.6.0 — 2026-11-17

V nabídce **Statistics** zvol Last 7 days, Last 30 days nebo All time. Přehled ukazuje uložený čas a sezení, otázkami váženou úspěšnost dokončených testů, počty vlastních hodnocení kartiček, čas podle předmětu a denní aktivitu. Refresh nebo návrat na obrazovku načte nový snímek. Nejde o měření zvládnutí učiva.

StatisticsPage volá Store.statistics(); study_statistics.py čte sessions, dokončené practice_attempts s practice_items a review_events v jedné konzistentní čtecí transakci. Nemění schéma 5 ani data. UI se obnovuje při návratu nebo přes Refresh, při chybě ponechá předchozí report. Vazby Configure mají životnost svých widgetů. Ctrl+K / Cmd+K a Escape nemění hledání skrytých obrazovek.

Nových 16 testů ověřuje období, místní dny, váhu otázek, úplnou historii, zachování po smazání, pouze čtení, souběžný snímek a opakování po chybě. Nativní kontrola ověřuje prázdný stav, filtry, chybu a opakování, navigaci, kompaktní rozložení, posouvání a otevření v novém procesu. Celkem 76 jednotkových testů a šest nativních kontrol; používají dočasná data.

## 0.5.1 — 2026-11-16

Opraveno označení verze v aplikaci a odkazy na aktuální vydání. Historie změn, stav kartiček a návody jsou sjednocené v češtině, slovenštině a ruštině s vydanou v0.5.0. Studijní funkce a databázové schéma se nemění; zdrojové vydání bez instalátoru.

## 0.5.0 — 2026-11-16

Nová obrazovka **Flashcards**: správa balíčků a kartiček, hledání v obou stranách, odhalení odpovědi a hodnocení Again / Hard / Good / Easy. Vlastní deterministické plánování ukládá další termín; nejde o SM-2 ani FSRS. Úprava kartičky obnoví splatnost a zachová historii. Smazání předmětu ponechá balíčky i kartičky; smazání kartičky či balíčku zachová historické snímky. Formuláře zachovávají rozepsaný obsah a neúspěšný zápis lze opakovat.

Ověření: 60 jednotkových testů na Ubuntu, Windows a macOS v CI; pět GUI kontrol na Ubuntu/Xvfb i lokálně na macOS. Dokumentace je samostatně česky, slovensky a rusky. Jde o zdrojové vydání bez instalátoru. [Návod a pravidla](FLASHCARDS.md).

`flashcard_page.py` obsahuje obrazovku, `repetition.py` čistou validaci a pravidla. Schéma 5 přidává decks, flashcards a review_events. Termín a interval jsou přímo u kartičky. Zápis hodnocení, snímku obou stran a dalšího termínu je jedna transakce; kontrola revize i splatnosti probíhá pod zápisovým zámkem. Opakované hodnocení stejné revize nevytvoří další záznam. Odkazy z historie mají ON DELETE SET NULL, kopie obsahu zůstávají. Balíčky mají k předmětu ON DELETE SET NULL, kartičky k balíčku ON DELETE CASCADE. Migrace z verze 4 a starších zachová existující data a výsledky testů.

## 0.4.1 — 2026-11-15

CI: Python 3.12, jednotkové testy na třech systémech a čtyři GUI kontroly na Ubuntu/Xvfb. [Výsledky](https://github.com/turcinv/SOSkuska/actions/workflows/ci.yml).

CI ověřuje 45 jednotkových testů, syntaxi a kompatibilitu závislostí na Ubuntu, Windows a macOS s Pythonem 3.12. Čtyři GUI kontroly běží na Ubuntu/Xvfb (Tk 8.6). První hostovaný běh všech úloh prošel. Workflow používá připnuté verze akcí, token pouze pro čtení, časové limity a rušení nahrazených běhů. Přidána dokumentace v češtině, slovenštině a ruštině. Studijní funkce i schéma databáze zůstávají stejné jako ve v0.4.0; nejde o nové vydání instalátoru.

## 0.4.0 — 2026-11-15

Practice Tests — procvičování

Nejprve vytvoř předmět a otázky přes My Subjects → Questions. V Practice Tests vyber předmět, téma (všechna / bez tématu / konkrétní), obtížnost a 1–100 dostupných otázek. Volitelný limit je 5, 10, 15, 30 nebo 60 minut; Untimed nemá limit. Otázky se náhodně vyberou bez opakování.

Odpověď se uloží po každém výběru; lze ji změnit nebo vymazat přes Clear answer. Previous/Next mění uloženou pozici. Při návratu nebo restartu lze pokračovat přes Resume test. Najednou může být rozpracovaný jeden test. Discard test vyžaduje potvrzení a odstraní pouze tento rozpracovaný pokus.

Finish test po potvrzení uloží výsledek; nevyplněné otázky se počítají jako nesprávné. Správné odpovědi a vysvětlení se zobrazí až po odevzdání. Časový limit běží i mimo obrazovku a při zavřené aplikaci; po vypršení se test automaticky dokončí při běhu nebo návratu do aplikace. Výsledek a otázky jsou snímkem ze začátku pokusu: pozdější úprava či smazání původního obsahu je nezmění. Historie zobrazuje posledních 20 dokončených testů; starší záznamy zůstávají v databázi.

Procvičování je dostupné od v0.4.0. Procvičování nepřidává smyšlený čas do součtů časovače. AI, kartičky, import a celková statistická obrazovka zůstávají plánované.

Migrace na schéma 4 zachová předměty, otázky a studijní historii. Ověřeno 45 testy a čtyřmi nativními kontrolami na macOS; nezávislá kontrola Sol (medium) ověřila opravu posunu jiné obrazovky při dokončení na pozadí. Windows/Linux a fyzická gesta zůstávají neověřené. Vydání obsahuje zdrojový kód bez instalátoru.

## 0.3.0 — 2026-11-14

První GitHub vydání zdrojového kódu. Zahrnuje správu předmětů, banku otázek a opravy z PR #1, #2 a #3. Verze 0.2.0 nebyla samostatně vydaná. Jde o funkční desktopový prototyp; instalátor zatím není součástí vydání.

### Nové funkce

- Nativní Dashboard v CustomTkinteru, sbalitelná navigace, hledání, denní checklist a lokální ukládání bez cloudového účtu.
- My Subjects: vytváření, úpravy a mazání předmětů, popis, volitelný termín zkoušky a validace Unicode.
- Question bank: témata a otázky pro každý předmět, čtyři různé odpovědi, jedna správná odpověď, obtížnost a volitelné vysvětlení. Úpravy, mazání a kombinované filtry tématu, obtížnosti a textu.
- Skutečné počty předmětů, témat, otázek a sezení; uložený čas, studijní série, nadcházející zkoušky a nedávná aktivita. Nová databáze začíná prázdná.
- Časovač propojený s předmětem, pauza, dokončení a uchování názvu předmětu ve studijní historii.
- Transakční migrace SQLite až na schéma 3; zachování původních úkolů a sezení a kompatibilita s datovou složkou ExamPrep.
- Dokumentace v češtině, slovenštině a ruštině: instalace včetně Windows od nuly, klonování, Git, přispívání a současná/plánovaná architektura. Anglický AGENTS.md.

### Opravy

- Zavření okna i Quit v nabídce macOS ukládají sezení; chyba zápisu zachová pozastavený čas a pokyn Press Finish pro opakování.
- Zastaralé potvrzení smazání předmětu se při navigaci ruší; změna názvu či počtů obsahu vyžaduje nové potvrzení pod SQLite zámkem. Historie studia se zachová.
- Selhání čtení nezastaví plánování časovače. Denní obnova se opakuje a datum v záhlaví se aktualizuje po úspěchu.
- Přehled se po uloženém sezení opakovaně načítá i ve stejný den; obnoví metriky a výběr předmětu bez duplicitního zápisu sezení. Pokyn k uložení neuloženého sezení zůstane viditelný.
- Jedno gesto neposouvá dlouhé textové pole i stránku současně. Tk 9 gesta nad posuvníkem a okrajem editoru se předají textovému poli; krátké pole umožňuje posuv stránky.
- Opravené souběžné migrace, přepínání sloupců My Subjects a přístup k obsahu v kompaktním okně.

### Ověření a rozsah

32 testů a všechny tři nativní kontroly prošly na macOS s Pythonem 3.12.13 / Tk 9.0 / CustomTkinter 5.2.2. Regresní kontroly používají dočasné databáze, skutečné SQLite zámky, nativní nabídku Quit a syntetická gesta posouvání.

Windows/Linux a fyzický trackpad nejsou prakticky ověřené. Banka otázek je editor s viditelnou správnou odpovědí; procvičovací testy s vyhodnocením, kartičky, AI Tutor, import a instalátory zůstávají plánované. Běh funguje offline bez placených služeb.

## 0.1.0 — 2026-11-10

Počáteční prototyp; označení verze, nikoli oznámení vydaného instalátoru nebo GitHub release.

- Dashboard SOSkúška v Pythonu/CustomTkinteru, resizable okno a sbalitelná navigace.
- Vyhledávání předmětů, denní checklist a 15minutový časovač; ukládání do SQLite.
- Posouvání včetně Tk 9 trackpadu a kompatibilita s databází původní aplikace ExamPrep.
- Automatické kontroly úložiště a nativní kontrolní skript; prověřeno na macOS, Windows/Linux zatím neověřené.
- Česká, slovenská a ruská dokumentace včetně návodu Windows od nuly; anglický AGENTS.md.
- Soukromý repozitář `turcinv/SOSkuska`. Vzorové metriky a ostatní obrazovky zůstávají ve stavu popsaném v dokumentaci.
