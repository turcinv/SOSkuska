# Jak to funguje — jednoduše

SOSkúška je desktopová aplikace. Python a CustomTkinter vytvářejí okno; SQLite ukládá údaje do souboru na tvém počítači. Prohlížeč, cloud ani spuštěnou AI k tomu nepotřebuješ. HTML ve složce `soskuska-local/` je historický návrh, nikoli běžící aplikace.

## První vlastní předmět

1. Otevři **My Subjects** a klikni na **New subject**.
2. Vyplň název, případně popis a termín zkoušky ve formátu `YYYY-MM-DD`.
3. Klikni na **Save subject**. Předmět se uloží a objeví také na Dashboardu.
4. **Edit** upraví stejný předmět. Prázdné, příliš dlouhé či duplicitní názvy a neplatná data aplikace odmítne přímo ve formuláři.

Nová instalace je prázdná. Názvy, termíny ani studijní statistiky nejsou automaticky vymyšlené. Vyhledávání na obou obrazovkách filtruje názvy tvých předmětů.

## Studium a ukládání

Na Dashboardu zvol předmět a klikni na **Start Studying**, nebo použij **Study** na kartě předmětu. Spustí se 15minutový časovač, který můžeš pozastavit a obnovit. **Finish** uloží skutečně uplynulé sekundy k vybranému předmětu; po 15 minutách se dokončí automaticky. I běžné zavření okna uloží rozpracovaný čas.

Dashboard pak ukáže skutečně uložený čas, počet sezení, sérii studijních dní a počet předmětů. Denní cíl je zatím pevně 60 minut. Nedávná aktivita obsahuje uložená sezení; nadcházející zkoušky tvoje uložené termíny. Dashboard nepočítá zvládnutí učiva; výsledky testů jsou v Practice Tests a souhrn ve Statistics.

Denní seznam úkolů se také ukládá. Review a subject označuješ ručně; Complete a focus session se po uložení nenulového času označí automaticky. Po opětovném spuštění ve stejný den se stav obnoví.

## Co se stane při smazání

**Delete** nejdříve zobrazí potvrzení na stránce. Smazání odstraní předmět a jeho termín zkoušky, ale zachová uložený studijní čas a historii se jménem platným při sezení. Aktivní předmět nelze smazat před dokončením časovače.

## Kde jsou data a jaká jsou omezení

Na Macu je výchozí soubor `~/Library/Application Support/SOSkuska/dashboard.sqlite3`. Pokud aplikace najde původní databázi v `ExamPrep/dashboard.sqlite3` a nová ještě neexistuje, pokračuje v původním souboru. Původní záznamy zachová a doplní nové tabulky/sloupce pomocí migrace. Starým sezením nepřiřazuje vymyšlené předměty.

Parametr `--data` umožňuje vlastní cestu. Údaje se automaticky nesynchronizují, nezálohují ani nešifrují. Během časovače se čas průběžně neukládá: při pádu může rozpracované sezení zmizet a po restartu se neobnoví. Sezení přes půlnoc se zatím připíše ke dni dokončení.

AI Tutor otevírá volitelný session chat přes Ollamu; spojení začne až po Connect nebo Send.

## Banka témat a otázek

V My Subjects zvol u předmětu **Questions**. Přidej téma přes New topic a otázku přes New question. Každá otázka má čtyři různé povinné odpovědi A–D, právě jednu správnou odpověď, obtížnost Easy/Medium/Hard a volitelné vysvětlení. Téma je volitelné. Formulář zachová rozepsaný obsah při chybě validace nebo zápisu.

Témata lze přejmenovat a smazat; vyber téma ve filtru a použij Rename selected topic nebo Delete selected topic. Otázky lze upravovat a mazat. Hledání v textu otázky se kombinuje s filtrem tématu a obtížnosti. Počty na kartách předmětů vycházejí z uloženého obsahu. Smazání tématu ponechá jeho otázky v No topic. Smazání předmětu po výslovném upozornění odstraní jeho témata a otázky, ale zachová čas i historii studia.

Jde o editor obsahu: správná odpověď je viditelná. Procvičování a hodnocení najdeš v Practice Tests. Import a obrázky zatím nejsou implementované.

## Opravy po kontrole hlavní větve

Zavření okna i příkaz Quit v nabídce macOS používají stejné uložení sezení. Pokud uložení selže, aplikace zůstane otevřená se zachovaným pozastaveným časem; po odstranění problému lze zkusit Finish nebo Quit znovu.

Opuštění obrazovky My Subjects zruší rozpracované potvrzení smazání předmětu. Před smazáním se v jedné transakci porovná aktuální název a počty témat/otázek s posledním zobrazeným upozorněním. Pokud se změnily, aplikace nejprve zobrazí aktualizované upozornění a vyžádá nové potvrzení.

Při změně dne se aktualizuje i datum v záhlaví. Chyba čtení při obnově checklistu nebo přehledu nezastaví plánování časovače; obnova se opakuje a nový den se potvrdí až po úspěchu. Posouvání uvnitř dlouhého textového pole zůstává v tomto poli, včetně jeho krajů; stránku posuneš nad jinou částí okna. Krátké pole bez vlastního posuvu dál umožňuje posouvání stránky.

Pokud se sezení uložilo, ale následné načtení přehledu selže, aplikace opakuje pouze načtení i během stejného dne; záznam sezení znovu neukládá. Po úspěchu obnoví metriky i výběr předmětu a odstraní oznámení o opakování. Pokud se naopak sezení neuložilo, pokyn Press Finish zůstane viditelný i při chybě či úspěšné obnově denního přehledu. Gesta trackpadu nad posuvníkem a okrajem dlouhého editoru se předají jeho textovému poli.

## Practice Tests — procvičování (v0.4.0)

Nejprve vytvoř předmět a otázky přes My Subjects → Questions. V Practice Tests vyber předmět, téma (všechna / bez tématu / konkrétní), obtížnost a 1–100 dostupných otázek. Volitelný limit je 5, 10, 15, 30 nebo 60 minut; Untimed nemá limit. Otázky se náhodně vyberou bez opakování.

Odpověď se uloží po každém výběru; lze ji změnit nebo vymazat přes Clear answer. Previous/Next mění uloženou pozici. Při návratu nebo restartu lze pokračovat přes Resume test. Najednou může být rozpracovaný jeden test. Discard test vyžaduje potvrzení a odstraní pouze tento rozpracovaný pokus.

Finish test po potvrzení uloží výsledek; nevyplněné otázky se počítají jako nesprávné. Správné odpovědi a vysvětlení se zobrazí až po odevzdání. Časový limit běží i mimo obrazovku a při zavřené aplikaci; po vypršení se test automaticky dokončí při běhu nebo návratu do aplikace. Výsledek a otázky jsou snímkem ze začátku pokusu: pozdější úprava či smazání původního obsahu je nezmění. Historie zobrazuje posledních 20 dokončených testů; starší záznamy zůstávají v databázi.

Procvičování je dostupné od v0.4.0. Procvičování nepřidává smyšlený čas do součtů časovače. Import zůstává plánovaný; AI Tutor má vlastní volitelný chat; celkový přehled je ve Statistics.

## Kartičky a opakování (v0.5.0)

V postranní nabídce otevři **Flashcards**. New deck vytvoří balíček pro existující předmět; název musí být jedinečný mezi všemi balíčky. Předmět balíčku se potom nemění, název a popis ano. Open deck umožní přidat a upravovat kartičky. Přední strana má 1–2000 znaků, zadní 1–4000; Search hledá v obou stranách. Seznam zobrazuje nejvýše 100 výsledků, další najdeš užším hledáním.

[Podrobný návod a pravidla](FLASHCARDS.md).

## Statistiky (v0.6.0)

V nabídce **Statistics** zvol Last 7 days, Last 30 days nebo All time. Přehled ukazuje uložený čas a sezení, otázkami váženou úspěšnost dokončených testů, počty vlastních hodnocení kartiček, čas podle předmětu a denní aktivitu. Refresh nebo návrat na obrazovku načte nový snímek. Nejde o měření zvládnutí učiva.

[Podrobná pravidla](STATISTICS.md).

## AI Tutor s Ollamou (v0.7.0)

V AI Tutor připoj vlastní Ollama server přes Connect / refresh, vyber model a jazyk odpovědi a zadej otázku. Odpověď přichází průběžně; Stop ji zastaví. Ostatní obrazovky zůstávají použitelné během generování i bez Ollamy. Chat je pouze pro aktuální spuštění aplikace, neukládá se do databáze.

[Návod AI Tutor](AI_TUTOR.md).
