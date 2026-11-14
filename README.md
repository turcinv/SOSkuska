# SOSkúška

Název aplikace je **SOSkúška**. Repozitář a kořenová složka jsou **SOSkuska**, zdrojový adresář `soskuska/`; technické názvy používají podobu bez diakritiky.

Lokální desktopový studijní asistent v Pythonu a CustomTkinteru. Implementované jsou Dashboard a My Subjects: správa předmětů a termínů zkoušek, denní checklist, vyhledávání a časovač propojený s předmětem. Úkoly a odstudovaný čas ukládá do SQLite na zařízení uživatele.

**Stav: funkční prototyp se skutečnými lokálními daty.** Předměty lze vytvářet, upravovat a mazat; přehled používá uložené časy a termíny. Nová databáze začíná prázdná. AI Tutor, testy a kartičky zatím nejsou implementované. Běh nevyžaduje Superdesign, placené API ani internet.

## Klonování a první instalace

Repozitář je soukromý; potřebuješ Git a účet s přístupem. V terminálu přejdi do složky, kam chceš projekt uložit:

```sh
git clone https://github.com/turcinv/SOSkuska.git
cd SOSkuska
```

Klon neobsahuje Python prostředí ani databázi. Pokračuj podle [instalace pro svůj systém](docs/DEVELOPMENT.md). Instalaci Gitu, přihlášení, aktualizace a práci s větvemi popisuje [Git krok za krokem](docs/GIT_GUIDE.md).

## Rychlé spuštění na tomto Macu

Z kořenové složky projektu:

```sh
.venv-macos/bin/python soskuska/app.py
```

Nebo otevři `soskuska/run-macos.command`. Připravené prostředí používá Python 3.12.13 / Tk 9.0. Staré `.venv-desktop` nepoužívej: na tomto Macu zobrazovalo prázdné okno.

## Dokumentace

**Začínáš na čistých Windows?** Použij podrobný návod: [Česky](docs/WINDOWS_FIRST_RUN.md) · [Slovensky](docs/sk/WINDOWS_FIRST_RUN.md) · [Русский](docs/ru/WINDOWS_FIRST_RUN.md). Vede od instalace Pythonu až po první spuštění; Git ani editor nejsou potřeba.

Jazykové verze: **Čeština** (tento rozcestník) · [Slovenčina](docs/sk/README.md) · [Русский](docs/ru/README.md). Pokyny v `AGENTS.md` jsou anglicky; konverzace může probíhat česky, slovensky, anglicky nebo rusky.

| Dokument | Obsah |
| --- | --- |
| [Jednoduché vysvětlení](docs/HOW_IT_WORKS.md) | Co se děje při spuštění, klikání a ukládání |
| [Současná architektura](docs/CURRENT_ARCHITECTURE.md) | Skutečné moduly, datové toky, databáze a omezení |
| [Plánovaná architektura](docs/PLANNED_ARCHITECTURE.md) | Budoucí členění, Ollama a etapy rozvoje |
| [Vývoj a spuštění](docs/DEVELOPMENT.md) | Instalace, příkazy, kontroly a řešení problémů |
| [Práce s Gitem](docs/GIT_GUIDE.md) | Klonování, přihlášení, větve, commity a aktualizace |
| [Přispívání](CONTRIBUTING.md) | Kontroly, pull requesty a hlášení chyb |
| [Historie změn](CHANGELOG.md) | Přehled změn prototypu |
| [Pokyny pro asistenty](AGENTS.md) | AGENTS.md pro další vývoj aplikace |

## Složky

```text
soskuska/          Nativní aplikace a kontrolní skript
soskuska-local/    Starší samostatný HTML návrh; vizuální reference
docs/             Dokumentace
```

Primární cílové platformy jsou Windows/Linux; macOS je také aktuální vývojové prostředí. Nativní kontrola prošla na macOS, Windows/Linux ještě ověřené nejsou. Instalátor zatím není vytvořený. Samostatný repozitář: [turcinv/SOSkuska](https://github.com/turcinv/SOSkuska). Repozitář je soukromý; přístup vyžaduje oprávnění.

## Banka témat a otázek

V My Subjects zvol u předmětu **Questions**. Přidej téma přes New topic a otázku přes New question. Každá otázka má čtyři různé povinné odpovědi A–D, právě jednu správnou odpověď, obtížnost Easy/Medium/Hard a volitelné vysvětlení. Téma je volitelné. Formulář zachová rozepsaný obsah při chybě validace nebo zápisu.

Témata lze přejmenovat a smazat; vyber téma ve filtru a použij Rename selected topic nebo Delete selected topic. Otázky lze upravovat a mazat. Hledání v textu otázky se kombinuje s filtrem tématu a obtížnosti. Počty na kartách předmětů vycházejí z uloženého obsahu. Smazání tématu ponechá jeho otázky v No topic. Smazání předmětu po výslovném upozornění odstraní jeho témata a otázky, ale zachová čas i historii studia.

Jde o editor obsahu: správná odpověď je viditelná. Spouštění a hodnocení procvičovacích testů, import a obrázky zatím nejsou implementované.
