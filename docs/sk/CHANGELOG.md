# História zmien

## Opravy po kontrole hlavnej vetvy — nevydané

Zatvorenie okna aj príkaz Quit v ponuke macOS používajú rovnaké uloženie relácie. Ak uloženie zlyhá, aplikácia zostane otvorená so zachovaným pozastaveným časom; po odstránení problému možno skúsiť Finish alebo Quit znovu.

Opustenie obrazovky My Subjects zruší rozpracované potvrdenie vymazania predmetu. Pred vymazaním sa v jednej transakcii porovná aktuálny názov a počty tém/otázok s posledným zobrazeným upozornením. Ak sa zmenili, aplikácia najprv zobrazí aktualizované upozornenie a vyžiada nové potvrdenie.

Pri zmene dňa sa aktualizuje aj dátum v záhlaví. Chyba čítania pri obnove zoznamu úloh alebo prehľadu nezastaví plánovanie časovača; obnova sa opakuje a nový deň sa potvrdí až po úspechu. Posúvanie v dlhom textovom poli zostáva v tomto poli vrátane jeho okrajov; stránku posunieš nad inou časťou okna. Krátke pole bez vlastného posunu naďalej umožňuje posúvanie stránky.

## Banka tém a otázok — 2026-11-14

V My Subjects zvoľ pri predmete **Questions**. Pridaj tému cez New topic a otázku cez New question. Každá otázka má štyri rôzne povinné odpovede A–D, práve jednu správnu odpoveď, náročnosť Easy/Medium/Hard a voliteľné vysvetlenie. Téma je voliteľná. Formulár zachová rozpísaný obsah pri chybe validácie alebo zápisu.

Témy možno premenovať a vymazať; vyber tému vo filtri a použi Rename selected topic alebo Delete selected topic. Otázky možno upravovať a mazať. Hľadanie v texte otázky sa kombinuje s filtrom témy a náročnosti. Počty na kartách predmetov vychádzajú z uloženého obsahu. Vymazanie témy ponechá jej otázky v No topic. Vymazanie predmetu po výslovnom upozornení odstráni jeho témy a otázky, ale zachová čas aj históriu štúdia.

Ide o editor obsahu: správna odpoveď je viditeľná. Spúšťanie a hodnotenie cvičných testov, import a obrázky zatiaľ nie sú implementované.

[Čeština](../../CHANGELOG.md) · [Русский](../ru/CHANGELOG.md)

## Unreleased

- Oprava súbežného spúšťania pri migrácii a prepínania stĺpcov My Subjects.
- Regresná kontrola automatického ukladania časovača po chybe a obnovenia zoznamu úloh cez polnoc.

- Správa predmetov a termínov skúšok, prázdny stav, validácia Unicode a história pri vymazaní.
- Skutočné metriky Dashboardu a prepojenie časovača s predmetom; odstránenie ukážkových štatistík.
- Transakčné migrácie SQLite na verziu 2 so zachovaním pôvodných údajov; 30 testov a rozšírená natívna kontrola.

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
