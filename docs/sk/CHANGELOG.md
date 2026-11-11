# História zmien

[Čeština](../../CHANGELOG.md) · [Русский](../ru/CHANGELOG.md)

## Unreleased

- Oprava súbežného spúšťania pri migrácii a prepínania stĺpcov My Subjects.
- Regresná kontrola automatického ukladania časovača po chybe a obnovenia zoznamu úloh cez polnoc.

- Správa predmetov a termínov skúšok, prázdny stav, validácia Unicode a história pri vymazaní.
- Skutočné metriky Dashboardu a prepojenie časovača s predmetom; odstránenie ukážkových štatistík.
- Transakčné migrácie SQLite na verziu 2 so zachovaním pôvodných údajov; 17 testov a rozšírená natívna kontrola.

- Návod na klonovanie, autentifikáciu, vetvy, commity, aktualizácie a pull requesty.
- Pokyny na prispievanie, šablóny chýb/návrhov a pull requestu, nastavenie editora.

## 0.1.0 — 2026-11-10

Počiatočný prototyp; označenie verzie, nie oznámenie vydaného inštalátora alebo GitHub release.

- Dashboard SOSkúška v Pythone/CustomTkinteri, meniteľná veľkosť okna a zbaliteľná navigácia.
- Vyhľadávanie predmetov, denný zoznam úloh a 15-minútový časovač; ukladanie do SQLite.
- Posúvanie vrátane trackpadu Tk 9 a kompatibilita s databázou pôvodnej aplikácie ExamPrep.
- Automatické kontroly úložiska a natívny kontrolný skript; overené na macOS, Windows/Linux zatiaľ neoverené.
- Česká, slovenská a ruská dokumentácia vrátane návodu Windows od nuly; anglický AGENTS.md.
- Súkromný repozitár `turcinv/SOSkuska`. Vzorové metriky a ostatné obrazovky zostávajú v stave opísanom v dokumentácii.
