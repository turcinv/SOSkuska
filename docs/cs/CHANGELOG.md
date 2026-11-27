# Historie změn

[English](../../CHANGELOG.md) · [Čeština](CHANGELOG.md) · [Slovenčina](../sk/CHANGELOG.md) · [Русский](../ru/CHANGELOG.md)

## Nevydáno

- CI: kontrola rozložení Dashboardu hlídá start čerstvého procesu podle času CPU a reálného času místo měření celé sondy, která selhávala na zatížených hostovaných strojích.
- Příprava serveru MCP jen pro čtení (žádná nová závislost, žádná změna GUI): umístění uživatelské databáze se přesunulo z `app.py` do `storage.user_database_path()` a nový `soskuska/study_queries.py` poskytuje omezené studijní dotazy jen pro čtení, ve výchozím stavu bez klíčů odpovědí a rubových stran kartiček. Schéma zůstává 10.

## 0.30.1 — 2026-11-26

- Opravy kvality AI podle vyhodnocení se skutečným modelem: správnou odpověď otázky umisťuje aplikace (žádná nesouhlasná písmena), poznámky jsou chráněny před vloženými pokyny, návrhy jasně nenalezené v poznámkách začínají nezaškrtnuté s varováním a studijní režimy odpovídají v jazyce otázky. Přidává `tools/evaluate_ai.py`. Schéma zůstává 10.

## 0.30.0 — 2026-11-26

- Návrhy AI z poznámek: vložte poznámky do balíčku nebo banky otázek, uloženým modelem Ollama vygenerujte kartičky nebo otázky s výběrem z odpovědí, návrhy zkontrolujte, zrušte zaškrtnutí chybných a výběr uložte atomicky. [Návod](AI_NOTE_GENERATION.md). Schéma zůstává 10.

## 0.29.0 — 2026-11-26

- Redesign značky s kočkou: nové logo a ikony s kočkou čtoucí knihu, paleta Charcoal/Lavender/Violet/Cream, tlačítka ve tvaru pilulky, levandulový výběr v postranním panelu, uvítací záhlaví, souhrnné dlaždice s ikonami, banner „Pokračujte ve studiu“ s ilustrovanou scénou a karta „Přidat předmět“. Schéma zůstává 10.

## 0.28.0 — 2026-11-26

- Místní logo otevřené knihy se značkou zaškrtnutí v postranním panelu a ikonách okna; vlastní ikona Windows EXE.

## 0.27.0 — 2026-11-26

- Nový studijní prostor: Dashboard, navigation, Dark/Light.

## 0.26.1 — 2026-11-26

- Opravy po revizi Astra: A62-05–A62-09.

## 0.26.0 — 2026-11-26

- Studijní režimy AI: Explain simply / Give me a hint / Quiz me.

## 0.25.0 — 2026-11-26

- Vysvětlení otázek: Explain this question → Prepare in Tutor → Connect / Send.

## 0.24.0 — 2026-11-25

- Nastavení seskupuje studijní předvolby a rozhraní vedle sebe v širokém okně a pod sebou v kompaktním; AI má vlastní kartu přes celou šířku. Zpráva pro Uložit/Načíst se zobrazuje u ovládání i v záhlaví. Změna velikosti zachová stejné prvky, koncepty a uložené snímky; ukládání zůstává výslovné a aktivní časovače zachovají původní délku.
- Plán denních záloh, ruční záloha/obnova a oba importy CSV používají společný vzhled karet, odsazení a zalomené zprávy. Skupiny akcí mají tři sloupce v širokém rozložení, jinak dva. Varování obnovy je nad tlačítkem nevratného potvrzení a Zrušit. Pole náhledu/chyb CSV mají viditelné okraje a vlastní posouvání. Pravidla náhledu, zrušení, atomického zápisu, oddělených procesů, zavření po obnově a bezpečnostní kopie se nemění.

## 0.23.0 — 2026-11-25

- Statistiky seskupují výběr období a Obnovit do záhlaví. Tři souhrnné karty jsou vedle sebe v širokém okně, jinak pod sebou. Aktivita předmětů a dnů zůstává níže s čitelně zalomenými popisky. Změna velikosti zachová existující přehled bez dotazu na databázi; chyba obnovení ponechá předchozí snímek. Definice, vážená úspěšnost a počty vlastních hodnocení se nemění.
- AI Tutor odděluje ovládání serveru/modelu/jazyka a uložené historie do karet, vedle sebe v širokém okně a pod sebou v kompaktním. Výběr modelu má celý řádek. Vlastník konverzace, přepis, otázka a Odeslat/Zastavit sdílejí ohraničenou plochu pro čtení a psaní. Zpráva o obnově se opakuje u tlačítek opakování, zahození a přerušení, aby bylo potvrzení čitelné po posunu stránky. Navigace a změna velikosti zachovají koncepty, prvky, výběr historie a běžící úlohy. Připojení je výslovné; otevření historie zůstává offline.

## 0.22.0 — 2026-11-25

- Předměty a banka otázek nyní seskupují názvy, počty a akce v záhlaví a označené hledání a filtry na společných plochách. Akce předmětu mají dva řádky; kartičky mají dva sloupce od 950 logických pixelů stránky, jinak jeden. Změna velikosti přeskládá existující kartičky bez dotazu na databázi. Pole odpovědí mají dva sloupce od 850 logických pixelů panelu, jinak jsou pod sebou; náhled správné odpovědi je zvýrazněný pouze v seznamu pro úpravy. Stránkování zůstává po 50 otázkách. Koncepty, původní snímky úprav, filtry, identita témat, kontroly zastaralého stavu a náhled CSV zachovávají dosavadní chování. Vydaná verze zůstává v0.21.0, schéma 10.

## 0.21.0 — 2026-11-25

- Nové čtecí plochy otázky a odpovědi, společné místo pro odhalení a hodnocení, akce balíčku a prázdné stavy. Chyby zápisu jsou u ovládání; chyba načtení další kartičky neopakuje uložené hodnocení. Zachováno plánování, historie a import; ověřeny čtyři jazyky při počátečním měřítku 100/150 %.


## 0.20.0 — 2026-11-25

- Redesign nastavení testu, záhlaví, uložených odpovědí, navigace, výsledků a historie. Zachované skóre/termíny/snímky, ochrana skrytých událostí a ověření chyb zápisu/dlouhého obsahu ve čtyřech jazycích při počátečním měřítku 100/150 %.

## 0.19.0 — 2026-11-25

- Redesign Dashboardu, krok 2: společné studijní ovládání, akce pro první předmět, předměty/hledání níže, kompaktní souhrn, responzivní boční obsah a výběr sidebaru. Logické rozměry plochy/názvů; obnova/opakování zápisu ve čtyřech jazycích při počátečním měřítku 100/150 %.
- Společný modrý/mátový vzhled s párovými Light/Dark plochami, samostatným najetím vedlejších tlačítek a jednotným pozadím postupu. Rozložení, výchozí hodnoty a schéma 10 zůstávají; uložené dočasné snímky před/po a skici budoucího rozložení.

## 0.18.1 — 2026-11-22

- Oprava zastaralého ukládání předmětů a potvrzení smazání otázek/témat; zachování konceptů stejného předmětu a nedostupných témat.
- Zohlednění úspěšné zálohy jiného okna při starém oznámení chyby. Čtyři nálezy Astra sleduje REVIEW_FINDINGS.md; schéma zůstává 10.

## 0.18.0 — 2026-11-22

- Volitelné denní místní zálohy se složkou pro daný počítač, koordinací oken a viditelnými výsledky/opakováním.
- Zachování souborů i konceptů bez změny schématu; kontejnerové, procesní a Windows kontroly a návody ve čtyřech jazycích.

## 0.17.0 — 2026-11-22

- Obnova soustředění po pádu: kontrolní body, pozastavená obnova/zahození, výhradní vlastnictví, opakování uložení a zálohy schématu 10.
- Testy migrace a přerušení/obnovy; sladěné návody ve čtyřech jazycích.

## 0.16.0 — 2026-11-22

v0.16.0 přidává uložené Light/Dark/System, použité po Save bez obnovy obrazovek a ztráty aktivní práce. System sleduje Windows/macOS, na Linuxu používá Light. Aktuální schéma je 9. Uživatel 22. listopadu 2026 potvrdil dokončení testování základu a schválil sloučení PR #32. [Nastavení vzhledu](APPEARANCE.md).

## 0.15.0 — 2026-11-21

v0.15.0 přidává nepodepsaný přenosný ZIP pro Windows x64, sestavený a ověřený pátou úlohou CI. Přibalený pomocný program zachová oddělené CSV/zálohovací procesy; cílový počítač nepotřebuje Python. Automatické hostované kontroly a ruční seznam pro čistý počítač jsou oddělené; ruční přejímka zatím není dokončená. Vydaná verze je v0.15.0, schéma 8. [Přenosná verze Windows a přejímka](WINDOWS_PORTABLE.md).

## 0.14.0 — 2026-11-20

Historie testů nyní nabízí všechny dokončené pokusy po 20 na stránku, filtr uloženého názvu předmětu a místních dat včetně obou hranic a otevření uloženého rozboru odpovědí. Koncepty filtrů a použitá stránka přežijí navigaci; chyba čtení zachová předchozí výsledky. Schéma zůstává 8. [Historie testů](PRACTICE_HISTORY.md).

Přidány offline testy v kontejneru s Xvfb, společný GUI spouštěč s časovými limity pro CI, kontext sestavení pouze se zdroji a popsané limity CPU/paměti. Běžné kontroly už nepotřebují okna na ploše hostitele. [Testy v kontejneru](CONTAINER_TESTS.md).

## 0.13.0 — 2026-11-20

Výběr jazyka rozhraní je dostupný ve v0.13.0: angličtina, čeština, slovenština a ruština. Ukládá se zvlášť od jazyka AI a použije se po restartu. Aktuální schéma je 8. [Jazyk rozhraní](UI_LANGUAGES.md).

## 0.12.0 — 2026-11-20

AI Tutor nyní ukládá konverzace lokálně včetně původního serveru/modelu a stavu odpovědi. Historii lze otevřít bez sítě, výslovně se připojit pro pokračování nebo vybranou konverzaci po potvrzení smazat. Vydáno ve v0.12.0 se schématem 7, které transakčně migruje původní studijní data. [Uložené konverzace AI Tutor](TUTOR_HISTORY.md).

## 0.11.1 — 2026-11-20

Kořenový AGENTS.md je přibližně o 86 % menší (z 27,4 KB na 3,9 KB), s výslovnými odkazy `@` a tabulkou pro načítání pokynů. Všech 20 původních sekcí zůstává zachováno v pěti anglických souborech pro agenty. Odkazy vyžadují přečtení souborů; nespoléhají na automatické vložení.

Datované poznatky uchovávají preference projektu, postup kontroly/vydání a pravidla pro importy, procesy Tk a rozepsané formuláře. Anglická, česká, slovenská a ruská verze jsou odkazované z README. Předání v0.11.0 zůstává historickým výchozím stavem. Studijní chování aplikace a schéma 6 se nemění.

Ověření: kontrola dokumentace nenašla blokující problém; ověřily se všechny původní sekce, místní odkazy, bloky kódu, cíle `@` a jazyková navigace. Všechny čtyři CI úlohy dokumentačního PR prošly. Označení vydání prošlo kontrolou verzí, syntaxe a dokumentace.

## 0.11.0 — 2026-11-20

Flashcards nyní podporuje import UTF-8 CSV do existujícího balíčku: šablonu s hlavičkou, stránkovaný náhled, odmítnutí přesných duplicit a jedno atomické uložení. Maximum 2 MiB / 500 záznamů. Nové kartičky jsou ihned splatné; původní termíny a historie hodnocení zůstávají zachované. Schéma zůstává 6. [Import kartiček z CSV](FLASHCARD_CSV_IMPORT.md).

Ověření: 202 jednotkových testů a všech dvanáct nativních GUI kontrol prošlo lokálně na macOS. Nálezy nezávislé kontroly Sol byly opravené a znovu zkontrolované. Všechny čtyři CI úlohy funkčního PR prošly: jednotkové testy na Linuxu, Windows a macOS a všech dvanáct GUI kontrol na Ubuntu/Xvfb.

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
