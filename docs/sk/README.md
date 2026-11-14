# SOSkúška — slovenská dokumentácia

Lokálny desktopový študijný asistent v Pythone a CustomTkinteri. Implementované sú Dashboard a My Subjects: správa predmetov a termínov skúšok, denný zoznam úloh, vyhľadávanie a časovač prepojený s predmetom. Úlohy a odštudovaný čas sa ukladajú do SQLite na zariadení používateľa.

**Stav: funkčný prototyp so skutočnými lokálnymi údajmi.** Predmety možno vytvárať, upravovať a mazať; prehľad používa uložené časy a termíny. Nová databáza začína prázdna. AI Tutor, testy a kartičky zatiaľ nie sú implementované. Beh nevyžaduje Superdesign, platené API ani internet.

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

Primárne cieľové platformy sú Windows/Linux; macOS je aj súčasné vývojové prostredie. Natívna kontrola prešla na macOS, Windows/Linux ešte nie sú overené. Inštalátor zatiaľ nie je vytvorený. Samostatný repozitár: [turcinv/SOSkuska](https://github.com/turcinv/SOSkuska). Repozitár je súkromný; prístup vyžaduje oprávnenie.

[Česká verzia](../../README.md) · [Русская версия](../ru/README.md)

## Banka tém a otázok

V My Subjects zvoľ pri predmete **Questions**. Pridaj tému cez New topic a otázku cez New question. Každá otázka má štyri rôzne povinné odpovede A–D, práve jednu správnu odpoveď, náročnosť Easy/Medium/Hard a voliteľné vysvetlenie. Téma je voliteľná. Formulár zachová rozpísaný obsah pri chybe validácie alebo zápisu.

Témy možno premenovať a vymazať; vyber tému vo filtri a použi Rename selected topic alebo Delete selected topic. Otázky možno upravovať a mazať. Hľadanie v texte otázky sa kombinuje s filtrom témy a náročnosti. Počty na kartách predmetov vychádzajú z uloženého obsahu. Vymazanie témy ponechá jej otázky v No topic. Vymazanie predmetu po výslovnom upozornení odstráni jeho témy a otázky, ale zachová čas aj históriu štúdia.

Ide o editor obsahu: správna odpoveď je viditeľná. Spúšťanie a hodnotenie cvičných testov, import a obrázky zatiaľ nie sú implementované.
