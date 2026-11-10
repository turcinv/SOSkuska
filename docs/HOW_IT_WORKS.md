# Jak to funguje — jednoduše

SOSkuska je desktopová aplikace. Python pomocí CustomTkinteru vytvoří okno a jeho ovládací prvky. Prohlížeč ani webový server k tomu nepotřebuješ. HTML ve složce `soskuska-local/` je jen samostatný návrh vzhledu.

## Od spuštění k uloženým datům

1. **Spuštění:** aplikace vytvoří okno a otevře místní SQLite databázi. Když ještě neexistuje, založí ji.
2. **Checklist:** zaškrtneš úkol a změna se ihned uloží pro dnešní datum. Po dalším spuštění ve stejný den zůstane zachovaná.
3. **Vyhledávání:** zadáš například `Physics`. Aplikace přefiltruje čtyři ukázkové předměty v paměti; nic neposílá na internet.
4. **Studium:** Start Studying i Resume session spouští nový 15minutový časovač. Ten můžeš pozastavit a znovu rozběhnout.
5. **Dokončení:** Finish uloží skutečně uplynulé sekundy. Po 15 minutách se sezení dokončí automaticky. Běžné zavření okna také uloží dosavadní čas.

Časovač se mezi spuštěními neobnovuje. Při násilném ukončení nebo pádu může rozpracovaný čas zmizet, protože se zatím průběžně neukládá.

## Skutečné funkce a ukázková data

| Skutečně funguje | Zatím pouze ukázka |
| --- | --- |
| Denní checklist a jeho uložení | Profil Alex Morgan |
| Měření a uložení studijního času | Streak, počet otázek a úspěšnost |
| Filtrování, posouvání a změna rozložení | Předměty a procenta pokroku |
| Pauza a dokončení časovače | Termíny zkoušek a nedávná aktivita |

Přehled začíná na ukázkových **24 h 35 min celkem** a **45 min dnes**. Skutečně uložený čas se k těmto základům přičítá. Nejde ještě o kompletní statistiku tvého studia.

Na Macu je databáze standardně v `~/Library/Application Support/SOSkuska/dashboard.sqlite3`. Nikam se automaticky nesynchronizuje. Aplikace ji sama nešifruje.

## Co přijde později

Přidáš vlastní předměty, otázky a kartičky. Procvičování začne zapisovat odpovědi a přehled bude počítat skutečný pokrok. AI Tutor se připojí k místní Ollamě, která provozuje jazykový model. Běžné studium má zůstat použitelné i bez AI.

To je budoucí plán, nikoli dnešní funkce. Další obrazovky v navigaci zatím jen zobrazují oznámení o jejich budoucí dostupnosti.


Kompatibilita s původním názvem: pokud nová databáze v `SOSkuska` neexistuje a původní `ExamPrep/dashboard.sqlite3` existuje, aplikace použije tento původní soubor. Nic automaticky nekopíruje, nepřesouvá ani nepřepisuje. Explicitní `--data` má vždy přednost.
