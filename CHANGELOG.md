# Historie změn

[Slovenčina](docs/sk/CHANGELOG.md) · [Русский](docs/ru/CHANGELOG.md)

## Nevydáno

CI: Python 3.12, jednotkové testy na třech systémech a čtyři GUI kontroly na Ubuntu/Xvfb. [Výsledky](https://github.com/turcinv/SOSkuska/actions/workflows/ci.yml).

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
