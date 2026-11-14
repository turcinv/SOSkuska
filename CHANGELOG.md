# Historie změn

## Opravy po kontrole hlavní větve — nevydáno

Zavření okna i příkaz Quit v nabídce macOS používají stejné uložení sezení. Pokud uložení selže, aplikace zůstane otevřená se zachovaným pozastaveným časem; po odstranění problému lze zkusit Finish nebo Quit znovu.

Opuštění obrazovky My Subjects zruší rozpracované potvrzení smazání předmětu. Před smazáním se v jedné transakci porovná aktuální název a počty témat/otázek s posledním zobrazeným upozorněním. Pokud se změnily, aplikace nejprve zobrazí aktualizované upozornění a vyžádá nové potvrzení.

Při změně dne se aktualizuje i datum v záhlaví. Chyba čtení při obnově checklistu nebo přehledu nezastaví plánování časovače; obnova se opakuje a nový den se potvrdí až po úspěchu. Posouvání uvnitř dlouhého textového pole zůstává v tomto poli, včetně jeho krajů; stránku posuneš nad jinou částí okna. Krátké pole bez vlastního posuvu dál umožňuje posouvání stránky.

## Banka témat a otázek — 2026-11-14

V My Subjects zvol u předmětu **Questions**. Přidej téma přes New topic a otázku přes New question. Každá otázka má čtyři různé povinné odpovědi A–D, právě jednu správnou odpověď, obtížnost Easy/Medium/Hard a volitelné vysvětlení. Téma je volitelné. Formulář zachová rozepsaný obsah při chybě validace nebo zápisu.

Témata lze přejmenovat a smazat; vyber téma ve filtru a použij Rename selected topic nebo Delete selected topic. Otázky lze upravovat a mazat. Hledání v textu otázky se kombinuje s filtrem tématu a obtížnosti. Počty na kartách předmětů vycházejí z uloženého obsahu. Smazání tématu ponechá jeho otázky v No topic. Smazání předmětu po výslovném upozornění odstraní jeho témata a otázky, ale zachová čas i historii studia.

Jde o editor obsahu: správná odpověď je viditelná. Spouštění a hodnocení procvičovacích testů, import a obrázky zatím nejsou implementované.

[Slovenčina](docs/sk/CHANGELOG.md) · [Русский](docs/ru/CHANGELOG.md)

## Unreleased

- Oprava souběžného spouštění při migraci a přepínání sloupců My Subjects.
- Regresní kontrola automatického ukládání časovače po chybě a obnovení checklistu přes půlnoc.

- Správa předmětů a termínů zkoušek, prázdný stav, validace Unicode a historie při smazání.
- Skutečné metriky Dashboardu a propojení časovače s předmětem; odstranění ukázkových statistik.
- Transakční migrace SQLite na verzi 2 se zachováním původních dat; 30 testů a rozšířená nativní kontrola.

- Návod ke klonování, autentizaci, větvím, commitům, aktualizacím a pull requestům.
- Pokyny k přispívání, šablony chyb/návrhů a pull requestu, nastavení editoru.

## 0.1.0 — 2026-11-10

Počáteční prototyp; označení verze, nikoli oznámení vydaného instalátoru nebo GitHub release.

- Dashboard SOSkúška v Pythonu/CustomTkinteru, resizable okno a sbalitelná navigace.
- Vyhledávání předmětů, denní checklist a 15minutový časovač; ukládání do SQLite.
- Posouvání včetně Tk 9 trackpadu a kompatibilita s databází původní aplikace ExamPrep.
- Automatické kontroly úložiště a nativní kontrolní skript; prověřeno na macOS, Windows/Linux zatím neověřené.
- Česká, slovenská a ruská dokumentace včetně návodu Windows od nuly; anglický AGENTS.md.
- Soukromý repozitář `turcinv/SOSkuska`. Vzorové metriky a ostatní obrazovky zůstávají ve stavu popsaném v dokumentaci.
