# SOSkúška — slovenská dokumentácia

[English](../../README.md) · [Čeština](../cs/README.md) · [Slovenčina](README.md) · [Русский](../ru/README.md)

**Vydanie: [v0.11.1](https://github.com/turcinv/SOSkuska/releases/tag/v0.11.1)** — zdrojový kód funkčného prototypu. Prehľad funkcií a opráv je v [histórii zmien](CHANGELOG.md). Inštalátor zatiaľ nie je súčasťou vydania.

Lokálny desktopový študijný asistent v Pythone a CustomTkinteri. Implementované sú Dashboard a My Subjects: správa predmetov a termínov skúšok, denný zoznam úloh, vyhľadávanie a časovač prepojený s predmetom. Úlohy a odštudovaný čas sa ukladajú do SQLite na zariadení používateľa.

**Stav: funkčný prototyp so skutočnými lokálnymi údajmi.** Predmety možno vytvárať, upravovať a mazať; prehľad používa uložené časy a termíny. Nová databáza začína prázdna. AI Tutor ponúka voliteľný session chat cez Ollamu. Beh nevyžaduje Superdesign, platené API ani internet.

## Dokumenty

**Nemáš na Windows nič nainštalované?** Začni návodom [Windows od nuly — krok za krokom](WINDOWS_FIRST_RUN.md).

- [Práca s Gitom](GIT_GUIDE.md)
- [Prispievanie](CONTRIBUTING.md)
- [História zmien](CHANGELOG.md)
- [Jednoduché vysvetlenie](HOW_IT_WORKS.md)
- [Súčasná architektúra](CURRENT_ARCHITECTURE.md)
- [Plánovaná architektúra](PLANNED_ARCHITECTURE.md)
- [Vývoj a spustenie na macOS, Windows a Linuxe](DEVELOPMENT.md)
- [Pokyny pre vývojových asistentov — anglicky](../../AGENTS.md)

## Klonovanie a prvá inštalácia

Repozitár je súkromný; potrebuješ Git a účet s prístupom. V termináli prejdi do priečinka, kam chceš projekt uložiť:

```sh
git clone https://github.com/turcinv/SOSkuska.git
cd SOSkuska
```

Klon neobsahuje prostredie Pythonu ani databázu. Pokračuj podľa [inštalácie pre svoj systém](DEVELOPMENT.md). Inštaláciu Gitu, prihlásenie, aktualizácie a prácu s vetvami opisuje [Git krok za krokom](GIT_GUIDE.md).

## Rýchle spustenie na tomto Macu

Z koreňového priečinka projektu:

```sh
.venv-macos/bin/python soskuska/app.py
```

Alebo otvor `soskuska/run-macos.command`. Pripravené prostredie používa Python 3.12.13 / Tk 9.0. Staré `.venv-desktop` nepoužívaj: na tomto Macu zobrazovalo prázdne okno.

## Priečinky a platformy

```text
soskuska/          Natívna aplikácia a kontrolný skript
soskuska-local/    Starší samostatný HTML návrh; vizuálna referencia
docs/             Česká dokumentácia; sk/ slovenská, ru/ ruská
```

Primárne cieľové platformy sú Windows/Linux; macOS je aj súčasné vývojové prostredie. Natívne kontroly prešli na macOS; CI overuje jednotkové testy na troch systémoch a GUI na Linuxe. Ručné overenie Windows/Linux a fyzických gest zatiaľ chýba. Inštalátor zatiaľ nie je vytvorený. Samostatný repozitár: [turcinv/SOSkuska](https://github.com/turcinv/SOSkuska). Repozitár je súkromný; prístup vyžaduje oprávnenie.

[Česká verzia](../../README.md) · [Русская версия](../ru/README.md)

## Banka tém a otázok

V My Subjects zvoľ pri predmete **Questions**. Pridaj tému cez New topic a otázku cez New question. Každá otázka má štyri rôzne povinné odpovede A–D, práve jednu správnu odpoveď, náročnosť Easy/Medium/Hard a voliteľné vysvetlenie. Téma je voliteľná. Formulár zachová rozpísaný obsah pri chybe validácie alebo zápisu.

Témy možno premenovať a vymazať; vyber tému vo filtri a použi Rename selected topic alebo Delete selected topic. Otázky možno upravovať a mazať. Hľadanie v texte otázky sa kombinuje s filtrom témy a náročnosti. Počty na kartách predmetov vychádzajú z uloženého obsahu. Vymazanie témy ponechá jej otázky v No topic. Vymazanie predmetu po výslovnom upozornení odstráni jeho témy a otázky, ale zachová čas aj históriu štúdia.

Ide o editor obsahu: správna odpoveď je viditeľná. Precvičovanie a hodnotenie nájdeš v Practice Tests. Import otázok z CSV je dostupný; obrázky zatiaľ nie sú implementované.

## Practice Tests — precvičovanie (v0.4.0)

Najprv vytvor predmet a otázky cez My Subjects → Questions. V Practice Tests vyber predmet, tému (všetky / bez témy / konkrétna), náročnosť a 1–100 dostupných otázok. Voliteľný limit je 5, 10, 15, 30 alebo 60 minút; Untimed nemá limit. Otázky sa náhodne vyberú bez opakovania.

Odpoveď sa uloží po každom výbere; možno ju zmeniť alebo vymazať cez Clear answer. Previous/Next menia uloženú pozíciu. Pri návrate alebo reštarte možno pokračovať cez Resume test. Naraz môže byť rozpracovaný jeden test. Discard test vyžaduje potvrdenie a odstráni iba tento rozpracovaný pokus.

Finish test po potvrdení uloží výsledok; nevyplnené otázky sa počítajú ako nesprávne. Správne odpovede a vysvetlenia sa zobrazia až po odovzdaní. Časový limit beží aj mimo obrazovky a pri zatvorenej aplikácii; po uplynutí sa test automaticky dokončí pri behu alebo návrate do aplikácie. Výsledok a otázky sú snímkou zo začiatku pokusu: neskoršia úprava či vymazanie pôvodného obsahu ich nezmení. História zobrazuje posledných 20 dokončených testov; staršie záznamy zostávajú v databáze.

Precvičovanie je dostupné od v0.4.0. Precvičovanie nepridáva vymyslený čas do súčtov časovača. Import kartičiek z CSV je dostupný; AI Tutor má vlastný voliteľný chat; celkový prehľad je v Statistics.

## Priebežná integrácia (CI)

CI: Python 3.12, jednotkové testy na troch systémoch a dvanásť GUI kontrol na Ubuntu/Xvfb. [Výsledky](https://github.com/turcinv/SOSkuska/actions/workflows/ci.yml).

## Kartičky a opakovanie (v0.5.0)

V bočnej ponuke otvor **Flashcards**. New deck vytvorí balíček pre existujúci predmet; názov musí byť jedinečný medzi všetkými balíčkami. Predmet balíčka sa potom nemení, názov a popis áno. Open deck umožní pridať a upravovať kartičky. Predná strana má 1–2000 znakov, zadná 1–4000; Search hľadá v oboch stranách. Zoznam zobrazuje najviac 100 výsledkov, ďalšie nájdeš užším hľadaním.

[Podrobný návod a pravidlá](FLASHCARDS.md).

## Štatistiky (v0.6.0)

V ponuke **Statistics** zvoľ Last 7 days, Last 30 days alebo All time. Prehľad ukazuje uložený čas a relácie, úspešnosť dokončených testov váženú otázkami, počty vlastných hodnotení kartičiek, čas podľa predmetu a dennú aktivitu. Refresh alebo návrat na obrazovku načíta novú snímku. Nejde o meranie zvládnutia učiva.

[Podrobné pravidlá](STATISTICS.md).

## AI Tutor s Ollamou (v0.7.0)

V AI Tutor pripoj vlastný server Ollama cez Connect / refresh, vyber model a jazyk odpovede a zadaj otázku. Odpoveď prichádza priebežne; Stop ju zastaví. Ostatné obrazovky zostávajú použiteľné počas generovania aj bez Ollamy. Chat je iba pre aktuálne spustenie aplikácie, neukladá sa do databázy.

[Návod AI Tutor](AI_TUTOR.md).

## Nastavenia

Chat zostáva iba v pamäti a zatvorením sa odstráni. Voľby spojenia možno výslovne uložiť v [Settings](SETTINGS.md); bez Save sú dočasné.

[Nastavenia](SETTINGS.md).

Hlavná dokumentácia je po anglicky v koreni repozitára a v `docs/`. Česká verzia je v `docs/cs/`, slovenská v `docs/sk/` a ruská v `docs/ru/`. AGENTS.md zostáva anglicky; konverzácia môže byť česky, slovensky, anglicky alebo rusky.

## Záloha a obnova

Settings teraz ponúka ručnú miestnu zálohu a overenú obnovu s bezpečnostnou kópiou pred nahradením. Schéma zostáva 6. Obnova zatvorí aplikáciu; potom ju spusti znovu. Pozri [Záloha a obnova](BACKUP_RESTORE.md).

## Import otázok z CSV

Banka otázok teraz podporuje import UTF-8 CSV do existujúceho predmetu: šablóna s hlavičkou, stránkovaný náhľad, odmietnutie presných duplicít a jedno atomické uloženie. Maximum 2 MiB / 500 záznamov; zoznam ukazuje 50 otázok na stránku. Schéma zostáva 6. [Import otázok z CSV](QUESTION_CSV_IMPORT.md).

## Import kartičiek z CSV

Flashcards teraz podporuje import UTF-8 CSV do existujúceho balíčka: šablónu s hlavičkou, stránkovaný náhľad, odmietnutie presných duplicít a jedno atomické uloženie. Maximum 2 MiB / 500 záznamov. Nové kartičky sú ihneď splatné; pôvodné termíny a história hodnotení zostávajú zachované. Schéma zostáva 6. [Import kartičiek z CSV](FLASHCARD_CSV_IMPORT.md).

[Poznatky zo sedenia a odovzdanie projektu](SESSION_LESSONS.md)
