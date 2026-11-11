# SOSkúška — slovenská dokumentácia

Lokálny desktopový študijný asistent v Pythone a CustomTkinteri. Implementované sú Dashboard a My Subjects: správa predmetov a termínov skúšok, denný zoznam úloh, vyhľadávanie a časovač prepojený s predmetom. Úlohy a odštudovaný čas sa ukladajú do SQLite na zariadení používateľa.

**Stav: funkčný prototyp so skutočnými lokálnymi údajmi.** Predmety možno vytvárať, upravovať a mazať; prehľad používa uložené časy a termíny. Nová databáza začína prázdna. AI Tutor, otázky, testy a kartičky zatiaľ nie sú implementované. Beh nevyžaduje Superdesign, platené API ani internet.

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
