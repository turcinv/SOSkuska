# Přispívání do SOSkúška

[Slovenčina](docs/sk/CONTRIBUTING.md) · [Русский](docs/ru/CONTRIBUTING.md)

## Než začneš

Přečti [README](README.md), [práci s Gitem](docs/GIT_GUIDE.md), [vývojový návod](docs/DEVELOPMENT.md) a [současnou architekturu](docs/CURRENT_ARCHITECTURE.md). Vývojoví asistenti mají navíc pokyny v [AGENTS.md](AGENTS.md).

Pracuj v nové větvi z aktuálního `main`. Jedna změna má řešit jeden srozumitelný problém. Existují Dashboard, My Subjects a Question bank; další plánované obrazovky neprezentuj jako hotové funkce. Nová databáze musí zůstat prázdná, dokud uživatel nezadá vlastní data. Používej samostatnou vývojovou databázi přes `--data .local-data/dev.sqlite3`.

## Před odesláním

Na macOS s připraveným prostředím:

```sh
.venv-macos/bin/python -m compileall -q soskuska tests
.venv-macos/bin/python -m unittest discover -s tests -v
```

Na Windows/Linux použij odpovídající cestu k Pythonu svého prostředí. Při změně UI, časovače nebo posouvání spusť i nativní kontrolu a ručně ověř dotčené chování:

```sh
.venv-macos/bin/python soskuska/check_dashboard.py
.venv-macos/bin/python soskuska/check_question_bank.py
```

Kontrola GUI otevírá okno a potřebuje grafickou relaci. Změna samotné dokumentace obvykle vyžaduje kontrolu odkazů, příkazů a formátování; není nutné kvůli ní spouštět celé UI.

Zkontroluj `git diff --check` a obsah commitu. Nepřidávej virtuální prostředí, databáze, cache, tokeny ani `.env`. Zachovej uživatelská data, stabilitu UI a offline provoz. Při podstatné změně aktualizuj českou, slovenskou i ruskou dokumentaci. AGENTS.md zůstává anglicky, rozhraní aplikace zatím také.

## Pull request a hlášení problémů

Pushni svou větev a otevři pull request do `main`. Popiš problém, nové chování a skutečně provedené kontroly včetně OS, Pythonu a Tk. Screenshot přidej, pokud pomáhá posoudit změnu UI. Neoznačuj neprovedené kontroly jako úspěšné; syntetické události neprokazují ověření fyzického trackpadu.

Chybu založ přes šablonu v Issues: postup opakování, očekávané/skutečné chování, prostředí a úplný relevantní výpis. Návrh funkce má popsat potřebu uživatele a očekávané chování. Nepřikládej soukromou databázi ani přístupové údaje. V Issues a pull requestech můžeš psát česky, slovensky, anglicky nebo rusky.
