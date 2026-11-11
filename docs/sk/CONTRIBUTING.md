# Prispievanie do SOSkúška

[Čeština](../../CONTRIBUTING.md) · [Русский](../ru/CONTRIBUTING.md)

## Skôr než začneš

Prečítaj [README](README.md), [prácu s Gitom](GIT_GUIDE.md), [vývojový návod](DEVELOPMENT.md) a [súčasnú architektúru](CURRENT_ARCHITECTURE.md). Vývojoví asistenti majú navyše pokyny v [AGENTS.md](../../AGENTS.md).

Pracuj v novej vetve z aktuálneho `main`. Jedna zmena má riešiť jeden zrozumiteľný problém. Existujú Dashboard a My Subjects; ďalšie plánované obrazovky neprezentuj ako hotové funkcie. Nová databáza musí zostať prázdna, kým používateľ nezadá vlastné údaje. Používaj samostatnú vývojovú databázu cez `--data .local-data/dev.sqlite3`.

## Pred odoslaním

Na macOS s pripraveným prostredím:

```sh
.venv-macos/bin/python -m compileall -q soskuska tests
.venv-macos/bin/python -m unittest discover -s tests -v
```

Na Windows/Linux použi zodpovedajúcu cestu k Pythonu svojho prostredia. Pri zmene UI, časovača alebo posúvania spusti aj natívnu kontrolu a ručne over dotknuté správanie:

```sh
.venv-macos/bin/python soskuska/check_dashboard.py
```

Kontrola GUI otvára okno a potrebuje grafickú reláciu. Zmena samotnej dokumentácie zvyčajne vyžaduje kontrolu odkazov, príkazov a formátovania; netreba kvôli nej spúšťať celé UI.

Skontroluj `git diff --check` a obsah commitu. Nepridávaj virtuálne prostredia, databázy, cache, tokeny ani `.env`. Zachovaj používateľské údaje, stabilitu UI a offline prevádzku. Pri podstatnej zmene aktualizuj českú, slovenskú aj ruskú dokumentáciu. AGENTS.md zostáva anglicky, rozhranie aplikácie zatiaľ tiež.

## Pull request a hlásenie problémov

Odošli svoju vetvu a otvor pull request do `main`. Opíš problém, nové správanie a skutočne vykonané kontroly vrátane OS, Pythonu a Tk. Snímku obrazovky pridaj, ak pomáha posúdiť zmenu UI. Neoznačuj nevykonané kontroly ako úspešné; syntetické udalosti nedokazujú overenie fyzického trackpadu.

Chybu nahlás cez šablónu v Issues: postup opakovania, očakávané/skutočné správanie, prostredie a úplný relevantný výpis. Návrh funkcie má opísať potrebu používateľa a očakávané správanie. Neprikladaj súkromnú databázu ani prístupové údaje. V Issues a pull requestoch môžeš písať česky, slovensky, anglicky alebo rusky.
