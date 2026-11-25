# Import otázek z CSV (v0.10.0)

[English](../QUESTION_CSV_IMPORT.md) · [Čeština](QUESTION_CSV_IMPORT.md) · [Slovenčina](../sk/QUESTION_CSV_IMPORT.md) · [Русский](../ru/QUESTION_CSV_IMPORT.md)

## Nevydáno — nastavení a společné datové panely

Plán denních záloh, ruční záloha/obnova a oba importy CSV používají společný vzhled karet, odsazení a zalomené zprávy. Skupiny akcí mají tři sloupce v širokém rozložení, jinak dva. Varování obnovy je nad tlačítkem nevratného potvrzení a Zrušit. Pole náhledu/chyb CSV mají viditelné okraje a vlastní posouvání. Pravidla náhledu, zrušení, atomického zápisu, oddělených procesů, zavření po obnově a bezpečnostní kopie se nemění.

Redesign úprav ve v0.22.0 sdružuje filtry a hledání do jedné plochy a ponechává Import CSV v záhlaví banky. Vstup do importu, oddělení náhledu od konceptů a pravidla ukládání a opakování níže se nemění.

Otevři **My Subjects → Questions → Import CSV** u existujícího předmětu. Soubor přidá otázky jen do něj; nevytváří předmět ani neupravuje existující otázky. Kartičky tato první verze neimportuje.

## Příprava souboru

Použij **Save CSV template** nebo [šablonu pouze s hlavičkou](../examples/questions-template.csv). Doplň vlastní řádky; šablona nemá vzorové otázky a nikdy se automaticky neimportuje. Ulož UTF-8 (volitelně BOM), CSV oddělené čárkami. Uvozovky umožňují čárky a více řádků v buňce. Středníky, neznámé/duplicitní hlavičky a neplatné UTF-8 se odmítnou. Maximum je **2 MiB a 500 neprázdných záznamů**; větší soubor rozděl. Prázdné záznamy se ignorují.

Povinné sloupce: `prompt`, `option_a`, `option_b`, `option_c`, `option_d`, `correct_option`, `difficulty`. Volitelné: `topic`, `explanation`. Pořadí sloupců je libovolné; velikost písmen a krajní mezery v hlavičce se ignorují. Správná odpověď je **A, B, C nebo D**, nikoli číslo. Obtížnost je Easy, Medium nebo Hard; u písmene odpovědi i obtížnosti nezáleží na velikosti písmen.

Platí běžné limity otázek: text 1–2 000 znaků, čtyři různé odpovědi po 1–500, vysvětlení nejvýše 2 000, téma nejvýše 120. Neplatné řídicí znaky se odmítnou. Prázdné téma znamená No topic. Existující téma se použije podle normalizovaného názvu (mezery, Unicode NFKC a casefold); chybějící vznikne až při uložení celé dávky.

## Náhled a uložení

1. **Choose CSV…** načte soubor. Náhled používá databázové spojení pouze pro čtení bez vytváření souboru či migrace; otázky ani témata neukládá.
2. Přečti chyby a přes Previous/Next zkontroluj všechny platné otázky, možnosti, správnou odpověď, obtížnost, vysvětlení a téma. Platné řádky lze prohlížet i při chybách, ale **jakákoli chyba zablokuje Import all**. Čísla označují CSV záznamy včetně hlavičky, ne nutně fyzické řádky víceřádkových buněk; chyba syntaxe CSV může uvést fyzický řádek.
3. Přesné duplicity se odmítnou v souboru i vůči předmětu. Shoda zahrnuje všechna normalizovaná pole otázky a název tématu. Jiné vysvětlení, obtížnost nebo téma znamená jinou otázku. Existující otázky se nepřepisují ani potichu nepřeskakují.
4. **Import all** potvrzuje uložení náhledu. Použije se soukromá kopie náhledu i po změně původního souboru; úpravy načteš novým výběrem. Identita/název předmětu, duplicity a témata se znovu kontrolují pod zápisovým zámkem. Přejmenování/smazání předmětu či nová duplicita odmítne celou dávku místo změny cíle.
5. Témata a otázky se uloží jednou transakcí. Validační chyba nebo selhání zápisu neuloží nic z dávky; náhled zůstane pro opakování či opravu. Při změně z jiného okna vyřeš uvedené chyby a vyber CSV znovu.
6. Úspěch nejprve zruší možnost znovu odeslat dávku a pak obnoví přehledy. Při chybě čtení použij **Refresh totals**, ne nový import. Pokud proces skončí bez potvrzení výsledku, import mohl proběhnout: nejprve obnov a zkontroluj předmět.

Close import nebo navigace zruší čtení/náhled; samostatné formuláře otázek/témat zůstanou při práci v bance rozepsané. Při skutečném ukládání modální okno zablokuje editaci, navigaci a běžné zavření/Quit. Parsování i zápis běží v pomocném procesu bez sítě a AI, s pojistkou 60 sekund. Používej běžné místní soubory, nikoli síťové cesty.

Banka zobrazuje **50 otázek na stránku**. Hledání/filtry platí pro celý předmět. Úprava či obnova pokud možno zachová stránku; změna filtrů/předmětu vrátí první. Aktivní filtr může skrýt importované otázky.

Šablona se zveřejní atomicky bez přepsání souborů či doprovodných databázových cest. POSIX vyžaduje podporu pevných odkazů; pokud externí disk selže, použij podporovanou místní složku. Aktuální schéma je **9**, snímky testů a historie se nemění. Nejde o synchronizaci, aktualizaci/slučování otázek, vyhodnocení tabulkových vzorců ani import kartiček na této obrazovce.

[Import kartiček z CSV](FLASHCARD_CSV_IMPORT.md)
