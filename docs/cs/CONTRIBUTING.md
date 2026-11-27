# Přispívání do SOSkúška

[English](../../CONTRIBUTING.md) · [Čeština](CONTRIBUTING.md) · [Slovenčina](../sk/CONTRIBUTING.md) · [Русский](../ru/CONTRIBUTING.md)

[Testy v kontejneru](CONTAINER_TESTS.md).

```sh
docker build -f Dockerfile.tests -t soskuska-tests .
docker run --rm --init --network none --cpus 2 --memory 2g soskuska-tests
```


## Než začneš

Přečti [README](README.md), [práci s Gitem](GIT_GUIDE.md), [vývojový návod](DEVELOPMENT.md) a [současnou architekturu](CURRENT_ARCHITECTURE.md). Vývojoví asistenti mají navíc pokyny v [AGENTS.md](../../AGENTS.md).

Pracuj v nové větvi z aktuálního `main`. Jedna změna má řešit jeden srozumitelný problém. Existují Dashboard, My Subjects, Question bank, Practice Tests, Flashcards, Statistics, volitelný AI Tutor a Settings; další plánované obrazovky neprezentuj jako hotové funkce. Nová databáze musí zůstat prázdná, dokud uživatel nezadá vlastní data. Používej samostatnou vývojovou databázi přes `--data .local-data/dev.sqlite3`.

## Před odesláním

Na macOS s připraveným prostředím:

```sh
.venv-macos/bin/python -m compileall -q soskuska tests
.venv-macos/bin/python -m unittest discover -s tests -v
```

Běžné kontroly UI, časovače a posouvání spouštěj v kontejneru výše. Nativní GUI skripty otevírají skutečná okna a slouží jen k nutnému platformnímu/ručnímu ověření; viditelný běh nejprve domluv s uživatelem. Úplný seznam je `GUI_CHECKS` v `tools/run_checks.py`. Na Windows/Linux použij odpovídající Python, například:

```sh
.venv-macos/bin/python soskuska/check_dashboard.py
.venv-macos/bin/python soskuska/check_note_generation.py
```

Kontrola GUI otevírá okno a potřebuje grafickou relaci. Změna samotné dokumentace obvykle vyžaduje kontrolu odkazů, příkazů a formátování; není nutné kvůli ní spouštět celé UI.

Zkontroluj `git diff --check` a obsah commitu. Nepřidávej virtuální prostředí, databáze, cache, tokeny ani `.env`. Zachovej uživatelská data, stabilitu UI a offline provoz. Při podstatné změně aktualizuj anglickou, českou, slovenskou i ruskou dokumentaci. AGENTS.md zůstává anglicky, rozhraní aplikace zatím také.

## Pull request a hlášení problémů

Pushni svou větev a otevři pull request do `main`. Popiš problém, nové chování a skutečně provedené kontroly včetně OS, Pythonu a Tk. Screenshot přidej, pokud pomáhá posoudit změnu UI. Neoznačuj neprovedené kontroly jako úspěšné; syntetické události neprokazují ověření fyzického trackpadu.

Chybu založ přes šablonu v Issues: postup opakování, očekávané/skutečné chování, prostředí a úplný relevantní výpis. Návrh funkce má popsat potřebu uživatele a očekávané chování. Nepřikládej soukromou databázi ani přístupové údaje. V Issues a pull requestech můžeš psát česky, slovensky, anglicky nebo rusky.

## Průběžná integrace (CI)

CI: Python 3.12, jednotkové testy na Ubuntu, Windows a macOS, GUI skripty uvedené v `tools/run_checks.py` (26 ve v0.30.1) na Ubuntu/Xvfb a kontrola sestavení přenosné verze pro Windows. [Výsledky](https://github.com/turcinv/SOSkuska/actions/workflows/ci.yml). Kontroly nenasazují ani nepublikují vydání. Při změně přehledů viz [pravidla statistik](STATISTICS.md); vlastní hodnocení se nesmí vydávat za změřené zvládnutí učiva. Změny promptů nebo schématu AI znovu ověř pomocí `tools/evaluate_ai.py` se skutečným místním modelem (viz [Vývoj](DEVELOPMENT.md)).

## Statistiky (v0.6.0)

V nabídce **Statistics** zvol Last 7 days, Last 30 days nebo All time. Přehled ukazuje uložený čas a sezení, otázkami váženou úspěšnost dokončených testů, počty vlastních hodnocení kartiček, čas podle předmětu a denní aktivitu. Refresh nebo návrat na obrazovku načte nový snímek. Nejde o měření zvládnutí učiva.

[Podrobná pravidla](STATISTICS.md).

`tests/test_flashcard_csv_import.py`, `soskuska/check_flashcard_import.py`.
