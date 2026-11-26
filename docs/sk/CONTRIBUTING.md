# Prispievanie do SOSkúška

[English](../../CONTRIBUTING.md) · [Čeština](../cs/CONTRIBUTING.md) · [Slovenčina](CONTRIBUTING.md) · [Русский](../ru/CONTRIBUTING.md)

[Testy v kontajneri](CONTAINER_TESTS.md).

```sh
docker build -f Dockerfile.tests -t soskuska-tests .
docker run --rm --init --network none --cpus 2 --memory 2g soskuska-tests
```


## Skôr než začneš

Prečítaj [README](README.md), [prácu s Gitom](GIT_GUIDE.md), [vývojový návod](DEVELOPMENT.md) a [súčasnú architektúru](CURRENT_ARCHITECTURE.md). Vývojoví asistenti majú navyše pokyny v [AGENTS.md](../../AGENTS.md).

Pracuj v novej vetve z aktuálneho `main`. Jedna zmena má riešiť jeden zrozumiteľný problém. Existujú Dashboard, My Subjects, Question bank, Practice Tests, Flashcards, Statistics, voliteľný AI Tutor a Settings; ďalšie plánované obrazovky neprezentuj ako hotové funkcie. Nová databáza musí zostať prázdna, kým používateľ nezadá vlastné údaje. Používaj samostatnú vývojovú databázu cez `--data .local-data/dev.sqlite3`.

## Pred odoslaním

Na macOS s pripraveným prostredím:

```sh
.venv-macos/bin/python -m compileall -q soskuska tests
.venv-macos/bin/python -m unittest discover -s tests -v
```

Bežné kontroly UI, časovača a posúvania spúšťaj v kontajneri vyššie. Natívne GUI skripty otvárajú skutočné okná a slúžia len na potrebné platformné/ručné overenie; viditeľný beh najprv dohodni s používateľom. Úplný zoznam je `GUI_CHECKS` v `tools/run_checks.py`. Na Windows/Linux použi zodpovedajúci Python, napríklad:

```sh
.venv-macos/bin/python soskuska/check_dashboard.py
.venv-macos/bin/python soskuska/check_note_generation.py
```

Kontrola GUI otvára okno a potrebuje grafickú reláciu. Zmena samotnej dokumentácie zvyčajne vyžaduje kontrolu odkazov, príkazov a formátovania; netreba kvôli nej spúšťať celé UI.

Skontroluj `git diff --check` a obsah commitu. Nepridávaj virtuálne prostredia, databázy, cache, tokeny ani `.env`. Zachovaj používateľské údaje, stabilitu UI a offline prevádzku. Pri podstatnej zmene aktualizuj anglickú, českú, slovenskú aj ruskú dokumentáciu. AGENTS.md zostáva anglicky, rozhranie aplikácie zatiaľ tiež.

## Pull request a hlásenie problémov

Odošli svoju vetvu a otvor pull request do `main`. Opíš problém, nové správanie a skutočne vykonané kontroly vrátane OS, Pythonu a Tk. Snímku obrazovky pridaj, ak pomáha posúdiť zmenu UI. Neoznačuj nevykonané kontroly ako úspešné; syntetické udalosti nedokazujú overenie fyzického trackpadu.

Chybu nahlás cez šablónu v Issues: postup opakovania, očakávané/skutočné správanie, prostredie a úplný relevantný výpis. Návrh funkcie má opísať potrebu používateľa a očakávané správanie. Neprikladaj súkromnú databázu ani prístupové údaje. V Issues a pull requestoch môžeš písať česky, slovensky, anglicky alebo rusky.

## Priebežná integrácia (CI)

CI: Python 3.12, jednotkové testy na Ubuntu, Windows a macOS, GUI skripty uvedené v `tools/run_checks.py` (26 vo v0.30.1) na Ubuntu/Xvfb a kontrola zostavenia prenosnej verzie pre Windows. [Výsledky](https://github.com/turcinv/SOSkuska/actions/workflows/ci.yml). Kontroly nenasadzujú ani nepublikujú vydania. Pri zmene prehľadov pozri [pravidlá štatistík](STATISTICS.md); vlastné hodnotenia sa nesmú vydávať za zmerané zvládnutie učiva. Zmeny promptov alebo schémy AI znova over pomocou `tools/evaluate_ai.py` so skutočným miestnym modelom (pozri [Vývoj](DEVELOPMENT.md)).

## Štatistiky (v0.6.0)

V ponuke **Statistics** zvoľ Last 7 days, Last 30 days alebo All time. Prehľad ukazuje uložený čas a relácie, úspešnosť dokončených testov váženú otázkami, počty vlastných hodnotení kartičiek, čas podľa predmetu a dennú aktivitu. Refresh alebo návrat na obrazovku načíta novú snímku. Nejde o meranie zvládnutia učiva.

[Podrobné pravidlá](STATISTICS.md).

`tests/test_flashcard_csv_import.py`, `soskuska/check_flashcard_import.py`.
