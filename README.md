# SOSkúška

Název aplikace je **SOSkúška**. Repozitář a kořenová složka jsou **SOSkuska**, zdrojový adresář `soskuska/`; technické názvy používají podobu bez diakritiky.

Lokální desktopový studijní asistent v Pythonu a CustomTkinteru. Aktuálně je implementovaný Dashboard s denním checklistem, vyhledáváním předmětů a časovačem. Úkoly a odstudovaný čas ukládá do SQLite na zařízení uživatele.

**Stav: funkční prototyp Dashboardu.** Předměty, zkoušky, profil a část statistik jsou ukázkové. AI Tutor, testy a kartičky zatím neexistují. Běh nevyžaduje Superdesign, placené API ani internet.

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
| [Pokyny pro asistenty](AGENTS.md) | AGENTS.md pro další vývoj aplikace |

## Složky

```text
soskuska/          Nativní aplikace a kontrolní skript
soskuska-local/    Starší samostatný HTML návrh; vizuální reference
docs/             Dokumentace
```

Primární cílové platformy jsou Windows/Linux; macOS je také aktuální vývojové prostředí. Nativní kontrola prošla na macOS, Windows/Linux ještě ověřené nejsou. Instalátor zatím není vytvořený. Samostatný repozitář: [turcinv/SOSkuska](https://github.com/turcinv/SOSkuska). Repozitář je soukromý; přístup vyžaduje oprávnění.
