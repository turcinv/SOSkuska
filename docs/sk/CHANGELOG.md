# História zmien

[Čeština](../../CHANGELOG.md) · [Русский](../ru/CHANGELOG.md)

## 0.3.0 — 2026-11-14

Prvé GitHub vydanie zdrojového kódu. Zahŕňa správu predmetov, banku otázok a opravy z PR #1, #2 a #3. Verzia 0.2.0 nebola samostatne vydaná. Ide o funkčný desktopový prototyp; inštalátor zatiaľ nie je súčasťou vydania.

### Nové funkcie

- Natívny Dashboard v CustomTkinteri, zbaliteľná navigácia, hľadanie, denný zoznam úloh a lokálne ukladanie bez cloudového účtu.
- My Subjects: vytváranie, úpravy a mazanie predmetov, popis, voliteľný termín skúšky a validácia Unicode.
- Question bank: témy a otázky pre každý predmet, štyri rôzne odpovede, jedna správna odpoveď, náročnosť a voliteľné vysvetlenie. Úpravy, mazanie a kombinované filtre témy, náročnosti a textu.
- Skutočné počty predmetov, tém, otázok a relácií; uložený čas, študijné série, nadchádzajúce skúšky a nedávna aktivita. Nová databáza začína prázdna.
- Časovač prepojený s predmetom, pauza, dokončenie a uchovanie názvu predmetu v študijnej histórii.
- Transakčné migrácie SQLite až na schému 3; zachovanie pôvodných úloh a relácií a kompatibilita s dátovým priečinkom ExamPrep.
- Dokumentácia v češtine, slovenčine a ruštine: inštalácia vrátane Windows od nuly, klonovanie, Git, prispievanie a súčasná/plánovaná architektúra. Anglický AGENTS.md.

### Opravy

- Zatvorenie okna aj Quit v ponuke macOS ukladajú reláciu; chyba zápisu zachová pozastavený čas a pokyn Press Finish na opakovanie.
- Zastarané potvrdenie vymazania predmetu sa pri navigácii ruší; zmena názvu či počtov obsahu vyžaduje nové potvrdenie pod SQLite zámkom. História štúdia sa zachová.
- Zlyhanie čítania nezastaví plánovanie časovača. Denná obnova sa opakuje a dátum v záhlaví sa aktualizuje po úspechu.
- Prehľad sa po uloženej relácii opakovane načítava aj v rovnaký deň; obnoví metriky a výber predmetu bez duplicitného zápisu relácie. Pokyn na uloženie neuloženej relácie zostane viditeľný.
- Jedno gesto neposúva dlhé textové pole aj stránku súčasne. Tk 9 gestá nad posuvníkom a okrajom editora sa odovzdajú textovému poľu; krátke pole umožňuje posun stránky.
- Opravené súbežné migrácie, prepínanie stĺpcov My Subjects a prístup k obsahu v kompaktnom okne.

### Overenie a rozsah

32 testov a všetky tri natívne kontroly prešli na macOS s Pythonom 3.12.13 / Tk 9.0 / CustomTkinter 5.2.2. Regresné kontroly používajú dočasné databázy, skutočné SQLite zámky, natívnu ponuku Quit a syntetické gestá posúvania.

Windows/Linux a fyzický trackpad nie sú prakticky overené. Banka otázok je editor s viditeľnou správnou odpoveďou; cvičné testy s vyhodnotením, kartičky, AI Tutor, import a inštalátory zostávajú plánované. Beh funguje offline bez platených služieb.

## 0.1.0 — 2026-11-10

Počiatočný prototyp; označenie verzie, nie oznámenie vydaného inštalátora alebo GitHub release.

- Dashboard SOSkúška v Pythone/CustomTkinteri, meniteľná veľkosť okna a zbaliteľná navigácia.
- Vyhľadávanie predmetov, denný zoznam úloh a 15-minútový časovač; ukladanie do SQLite.
- Posúvanie vrátane trackpadu Tk 9 a kompatibilita s databázou pôvodnej aplikácie ExamPrep.
- Automatické kontroly úložiska a natívny kontrolný skript; overené na macOS, Windows/Linux zatiaľ neoverené.
- Česká, slovenská a ruská dokumentácia vrátane návodu Windows od nuly; anglický AGENTS.md.
- Súkromný repozitár `turcinv/SOSkuska`. Vzorové metriky a ostatné obrazovky zostávajú v stave opísanom v dokumentácii.
