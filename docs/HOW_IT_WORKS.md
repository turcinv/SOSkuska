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

Dashboard pak ukáže skutečně uložený čas, počet sezení, sérii studijních dní a počet předmětů. Denní cíl je zatím pevně 60 minut. Nedávná aktivita obsahuje uložená sezení; nadcházející zkoušky tvoje uložené termíny. Procenta zvládnutého učiva či úspěšnost testů se zatím nepočítají.

Denní seznam úkolů se také ukládá. Review a subject označuješ ručně; Complete a focus session se po uložení nenulového času označí automaticky. Po opětovném spuštění ve stejný den se stav obnoví.

## Co se stane při smazání

**Delete** nejdříve zobrazí potvrzení na stránce. Smazání odstraní předmět a jeho termín zkoušky, ale zachová uložený studijní čas a historii se jménem platným při sezení. Aktivní předmět nelze smazat před dokončením časovače.

## Kde jsou data a jaká jsou omezení

Na Macu je výchozí soubor `~/Library/Application Support/SOSkuska/dashboard.sqlite3`. Pokud aplikace najde původní databázi v `ExamPrep/dashboard.sqlite3` a nová ještě neexistuje, pokračuje v původním souboru. Původní záznamy zachová a doplní nové tabulky/sloupce pomocí migrace. Starým sezením nepřiřazuje vymyšlené předměty.

Parametr `--data` umožňuje vlastní cestu. Údaje se automaticky nesynchronizují, nezálohují ani nešifrují. Během časovače se čas průběžně neukládá: při pádu může rozpracované sezení zmizet a po restartu se neobnoví. Sezení přes půlnoc se zatím připíše ke dni dokončení.

AI Tutor, testy a kartičky jsou další plánované funkce. Jejich položky v navigaci zatím zobrazují oznámení.

## Banka témat a otázek

V My Subjects zvol u předmětu **Questions**. Přidej téma přes New topic a otázku přes New question. Každá otázka má čtyři různé povinné odpovědi A–D, právě jednu správnou odpověď, obtížnost Easy/Medium/Hard a volitelné vysvětlení. Téma je volitelné. Formulář zachová rozepsaný obsah při chybě validace nebo zápisu.

Témata lze přejmenovat a smazat; vyber téma ve filtru a použij Rename selected topic nebo Delete selected topic. Otázky lze upravovat a mazat. Hledání v textu otázky se kombinuje s filtrem tématu a obtížnosti. Počty na kartách předmětů vycházejí z uloženého obsahu. Smazání tématu ponechá jeho otázky v No topic. Smazání předmětu po výslovném upozornění odstraní jeho témata a otázky, ale zachová čas i historii studia.

Jde o editor obsahu: správná odpověď je viditelná. Spouštění a hodnocení procvičovacích testů, import a obrázky zatím nejsou implementované.
