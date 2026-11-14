# Ako to funguje — jednoducho

SOSkúška je desktopová aplikácia. Python a CustomTkinter vytvárajú okno; SQLite ukladá údaje do súboru na tvojom počítači. Prehliadač, cloud ani spustenú AI nepotrebuješ. HTML v priečinku `soskuska-local/` je historický návrh, nie bežiaca aplikácia.

## Prvý vlastný predmet

1. Otvor **My Subjects** a klikni na **New subject**.
2. Vyplň názov, prípadne popis a termín skúšky vo formáte `YYYY-MM-DD`.
3. Klikni na **Save subject**. Predmet sa uloží a objaví aj na Dashboarde.
4. **Edit** upraví rovnaký predmet. Prázdne, príliš dlhé či duplicitné názvy a neplatné dátumy aplikácia odmietne priamo vo formulári.

Nová inštalácia je prázdna. Názvy, termíny ani študijné štatistiky nie sú automaticky vymyslené. Vyhľadávanie na oboch obrazovkách filtruje názvy tvojich predmetov.

## Štúdium a ukladanie

Na Dashboarde zvoľ predmet a klikni na **Start Studying**, alebo použi **Study** na karte predmetu. Spustí sa 15-minútový časovač, ktorý môžeš pozastaviť a obnoviť. **Finish** uloží skutočne uplynulé sekundy k vybranému predmetu; po 15 minútach sa dokončí automaticky. Aj bežné zatvorenie okna uloží rozpracovaný čas.

Dashboard potom ukáže skutočne uložený čas, počet relácií, sériu študijných dní a počet predmetov. Denný cieľ je zatiaľ pevne 60 minút. Nedávna aktivita obsahuje uložené relácie; nadchádzajúce skúšky tvoje uložené termíny. Percentá zvládnutého učiva či úspešnosť testov sa zatiaľ nepočítajú.

Denný zoznam úloh sa tiež ukladá. Review a subject označuješ ručne; Complete a focus session sa po uložení nenulového času označí automaticky. Po opätovnom spustení v rovnaký deň sa stav obnoví.

## Čo sa stane pri vymazaní

**Delete** najprv zobrazí potvrdenie na stránke. Vymazanie odstráni predmet a jeho termín skúšky, ale zachová uložený študijný čas a históriu s názvom platným počas relácie. Aktívny predmet nemožno vymazať pred dokončením časovača.

## Kde sú údaje a aké sú obmedzenia

Na Macu je predvolený súbor `~/Library/Application Support/SOSkuska/dashboard.sqlite3`. Ak aplikácia nájde pôvodnú databázu v `ExamPrep/dashboard.sqlite3` a nová ešte neexistuje, pokračuje v pôvodnom súbore. Pôvodné záznamy zachová a doplní nové tabuľky/stĺpce pomocou migrácie. Starým reláciám nepriraďuje vymyslené predmety.

Parameter `--data` umožňuje vlastnú cestu. Údaje sa automaticky nesynchronizujú, nezálohujú ani nešifrujú. Počas časovača sa čas priebežne neukladá: pri páde môže rozpracovaná relácia zmiznúť a po reštarte sa neobnoví. Relácia cez polnoc sa zatiaľ pripíše ku dňu dokončenia.

AI Tutor, testy a kartičky sú ďalšie plánované funkcie. Ich položky v navigácii zatiaľ zobrazujú oznámenie.

## Banka tém a otázok

V My Subjects zvoľ pri predmete **Questions**. Pridaj tému cez New topic a otázku cez New question. Každá otázka má štyri rôzne povinné odpovede A–D, práve jednu správnu odpoveď, náročnosť Easy/Medium/Hard a voliteľné vysvetlenie. Téma je voliteľná. Formulár zachová rozpísaný obsah pri chybe validácie alebo zápisu.

Témy možno premenovať a vymazať; vyber tému vo filtri a použi Rename selected topic alebo Delete selected topic. Otázky možno upravovať a mazať. Hľadanie v texte otázky sa kombinuje s filtrom témy a náročnosti. Počty na kartách predmetov vychádzajú z uloženého obsahu. Vymazanie témy ponechá jej otázky v No topic. Vymazanie predmetu po výslovnom upozornení odstráni jeho témy a otázky, ale zachová čas aj históriu štúdia.

Ide o editor obsahu: správna odpoveď je viditeľná. Spúšťanie a hodnotenie cvičných testov, import a obrázky zatiaľ nie sú implementované.

## Opravy po kontrole hlavnej vetvy

Zatvorenie okna aj príkaz Quit v ponuke macOS používajú rovnaké uloženie relácie. Ak uloženie zlyhá, aplikácia zostane otvorená so zachovaným pozastaveným časom; po odstránení problému možno skúsiť Finish alebo Quit znovu.

Opustenie obrazovky My Subjects zruší rozpracované potvrdenie vymazania predmetu. Pred vymazaním sa v jednej transakcii porovná aktuálny názov a počty tém/otázok s posledným zobrazeným upozornením. Ak sa zmenili, aplikácia najprv zobrazí aktualizované upozornenie a vyžiada nové potvrdenie.

Pri zmene dňa sa aktualizuje aj dátum v záhlaví. Chyba čítania pri obnove zoznamu úloh alebo prehľadu nezastaví plánovanie časovača; obnova sa opakuje a nový deň sa potvrdí až po úspechu. Posúvanie v dlhom textovom poli zostáva v tomto poli vrátane jeho okrajov; stránku posunieš nad inou časťou okna. Krátke pole bez vlastného posunu naďalej umožňuje posúvanie stránky.

Ak sa relácia uložila, ale následné načítanie prehľadu zlyhá, aplikácia opakuje iba načítanie aj počas rovnakého dňa; záznam relácie znovu neukladá. Po úspechu obnoví metriky aj výber predmetu a odstráni oznámenie o opakovaní. Ak sa naopak relácia neuložila, pokyn Press Finish zostane viditeľný aj pri chybe či úspešnej obnove denného prehľadu. Gestá trackpadu nad posuvníkom a okrajom dlhého editora sa odovzdajú jeho textovému poľu.
