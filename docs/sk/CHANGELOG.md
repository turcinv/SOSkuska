# História zmien

[Čeština](../../CHANGELOG.md) · [Русский](../ru/CHANGELOG.md)

## 0.5.0 — 2026-11-16

Nová obrazovka **Flashcards**: správa balíčkov a kartičiek, hľadanie na oboch stranách, odhalenie odpovede a hodnotenie Again / Hard / Good / Easy. Vlastné deterministické plánovanie ukladá ďalší termín; nejde o SM-2 ani FSRS. Úprava kartičky obnoví splatnosť a zachová históriu. Zmazanie predmetu ponechá balíčky aj kartičky; zmazanie kartičky či balíčka zachová historické snímky. Formuláre zachovávajú rozpísaný obsah a neúspešný zápis možno zopakovať.

Overenie: 60 jednotkových testov na Ubuntu, Windows a macOS v CI; päť GUI kontrol na Ubuntu/Xvfb aj lokálne na macOS. Dokumentácia je samostatne česky, slovensky a rusky. Ide o zdrojové vydanie bez inštalátora. [Návod a pravidlá](FLASHCARDS.md).

`flashcard_page.py` obsahuje obrazovku, `repetition.py` čistú validáciu a pravidlá. Schéma 5 pridáva decks, flashcards a review_events. Termín a interval sú priamo pri kartičke. Zápis hodnotenia, snímky oboch strán a ďalšieho termínu je jedna transakcia; kontrola revízie aj splatnosti prebieha pod zápisovým zámkom. Opakované hodnotenie rovnakej revízie nevytvorí ďalší záznam. Odkazy z histórie majú ON DELETE SET NULL, kópie obsahu zostávajú. Balíčky majú k predmetu ON DELETE SET NULL, kartičky k balíčku ON DELETE CASCADE. Migrácia z verzie 4 a starších zachová existujúce údaje a výsledky testov.

## 0.4.1 — 2026-11-15

CI: Python 3.12, jednotkové testy na troch systémoch a štyri GUI kontroly na Ubuntu/Xvfb. [Výsledky](https://github.com/turcinv/SOSkuska/actions/workflows/ci.yml).

CI overuje 45 jednotkových testov, syntax a kompatibilitu závislostí na Ubuntu, Windows a macOS s Pythonom 3.12. Štyri GUI kontroly bežia na Ubuntu/Xvfb (Tk 8.6). Prvý hostovaný beh všetkých úloh prešiel. Workflow používa pripnuté verzie akcií, token iba na čítanie, časové limity a rušenie nahradených behov. Pridaná dokumentácia v češtine, slovenčine a ruštine. Študijné funkcie aj schéma databázy zostávajú rovnaké ako vo v0.4.0; nejde o nové vydanie inštalátora.

## 0.4.0 — 2026-11-15

Practice Tests — precvičovanie

Najprv vytvor predmet a otázky cez My Subjects → Questions. V Practice Tests vyber predmet, tému (všetky / bez témy / konkrétna), náročnosť a 1–100 dostupných otázok. Voliteľný limit je 5, 10, 15, 30 alebo 60 minút; Untimed nemá limit. Otázky sa náhodne vyberú bez opakovania.

Odpoveď sa uloží po každom výbere; možno ju zmeniť alebo vymazať cez Clear answer. Previous/Next menia uloženú pozíciu. Pri návrate alebo reštarte možno pokračovať cez Resume test. Naraz môže byť rozpracovaný jeden test. Discard test vyžaduje potvrdenie a odstráni iba tento rozpracovaný pokus.

Finish test po potvrdení uloží výsledok; nevyplnené otázky sa počítajú ako nesprávne. Správne odpovede a vysvetlenia sa zobrazia až po odovzdaní. Časový limit beží aj mimo obrazovky a pri zatvorenej aplikácii; po uplynutí sa test automaticky dokončí pri behu alebo návrate do aplikácie. Výsledok a otázky sú snímkou zo začiatku pokusu: neskoršia úprava či vymazanie pôvodného obsahu ich nezmení. História zobrazuje posledných 20 dokončených testov; staršie záznamy zostávajú v databáze.

Precvičovanie je dostupné od v0.4.0. Precvičovanie nepridáva vymyslený čas do súčtov časovača. AI, kartičky, import a celková štatistická obrazovka zostávajú plánované.

Migrácia na schému 4 zachová predmety, otázky a študijnú históriu. Overené 45 testami a štyrmi natívnymi kontrolami na macOS; nezávislá kontrola Sol (medium) overila opravu posunu inej obrazovky pri dokončení na pozadí. Windows/Linux a fyzické gestá zostávajú neoverené. Vydanie obsahuje zdrojový kód bez inštalátora.

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
