# SOSkúška — desktopová aplikace

Vstupní soubor je `app.py`. Rozhraní používá Python a CustomTkinter, úkoly a studijní čas ukládá SQLite.

Z kořene projektu na tomto Macu:

```sh
.venv-macos/bin/python soskuska/app.py --data .local-data/dev.sqlite3
```

Bez `--data` se použije běžná uživatelská databáze. Nativní kontrola s vlastní dočasnou databází:

```sh
.venv-macos/bin/python soskuska/check_dashboard.py
.venv-macos/bin/python soskuska/check_question_bank.py
```

Úplná dokumentace:

První instalace na Windows: [Česky](../docs/WINDOWS_FIRST_RUN.md) · [Slovensky](../docs/sk/WINDOWS_FIRST_RUN.md) · [Русский](../docs/ru/WINDOWS_FIRST_RUN.md).

[Slovenčina](../docs/sk/README.md) · [Русский](../docs/ru/README.md) · Čeština (odkazy níže). Pokyny v AGENTS.md jsou anglicky.

- [Přehled projektu](../README.md)
- [Spuštění, instalace a vývoj](../docs/DEVELOPMENT.md)
- [Jednoduché vysvětlení](../docs/HOW_IT_WORKS.md)
- [Současná architektura](../docs/CURRENT_ARCHITECTURE.md)
- [Plánovaná architektura](../docs/PLANNED_ARCHITECTURE.md)
- [Pokyny pro další vývoj](../AGENTS.md)

Implementované jsou Dashboard a My Subjects se skutečnými předměty, termíny a studijním časem. V My Subjects otevři Questions pro správu témat a otázek. Nová databáze je prázdná. Kartičky, Ollama a ostatní obrazovky zůstávají plánované.

Practice Tests používá otázky ze zvoleného předmětu, ukládá odpovědi a výsledky a umožňuje pokračování po restartu. Nativní kontrola: `.venv-macos/bin/python soskuska/check_practice.py`. Dostupné od v0.4.0.

Flashcards: balíčky, vlastní kartičky, odhalení odpovědi a ukládané termíny opakování. [Návod](../docs/FLASHCARDS.md). Kontrola: `.venv-macos/bin/python soskuska/check_flashcards.py`. Zatím nevydané.
