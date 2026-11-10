# Klonovanie a základná práca s Gitom

Git ukladá históriu zmien na tvojom počítači. GitHub uchováva vzdialenú kópiu a umožňuje spoluprácu. ZIP stačí na spustenie aplikácie; na vývoj a odosielanie zmien použi klon.

## 1. Získaj prístup a Git

Repozitár [turcinv/SOSkuska](https://github.com/turcinv/SOSkuska) je **súkromný**. Najprv ho otvor v prehliadači pod účtom, ktorý má prístup. Chyba 404 môže znamenať chýbajúce oprávnenie.

Over inštaláciu Gitu:

```sh
git --version
```

Ak príkaz neexistuje, nainštaluj Git podľa [oficiálneho návodu pre svoju platformu](https://git-scm.com/downloads/). Na Windows použi Git for Windows a ponechaj Git Credential Manager; po inštalácii otvor nový PowerShell. Na macOS môžeš využiť Apple Command Line Tools podľa ponuky systému alebo inú možnosť z oficiálneho návodu. Na Linuxe použi balík svojej distribúcie.

Pri HTTPS klonovaní môže Git Credential Manager otvoriť prihlásenie v prehliadači. Prihlás sa účtom s prístupom. Samotné prihlásenie na webe nemusí prihlásiť aj Git. Heslo účtu nevkladaj do adresy repozitára; podrobnosti opisuje [GitHub dokumentácia prihlasovania](https://docs.github.com/en/get-started/git-basics/caching-your-github-credentials-in-git). Ak už používaš GitHub CLI, môžeš využiť `gh auth login` a `gh auth setup-git`.

## 2. Naklonuj projekt

V termináli prejdi do nadradeného priečinka, kam chceš projekt uložiť. Potom spusti:

```sh
git clone https://github.com/turcinv/SOSkuska.git
cd SOSkuska
git status
```

Vznikne nový priečinok `SOSkuska` s históriou `.git`. Výpis má ukázať vetvu `main` a žiadne neuložené zmeny. Ak cieľový priečinok už existuje, neklonuj cezň; použi iný nadradený priečinok. Existujúci skutočný klon aktualizuj cez `git pull --ff-only`.

## 3. Priprav Python a spusť aplikáciu

Klon neobsahuje virtuálne prostredie ani databázu. Na každom počítači vytvor vlastné prostredie. Ak na Windows ešte nemáš Python, najprv prejdi [návod Windows od nuly](WINDOWS_FIRST_RUN.md); kroky na stiahnutie ZIPu preskoč, pretože už máš klon.

Windows / PowerShell, ak je Python 3.12 už nainštalovaný:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r soskuska/requirements.txt
.\.venv\Scripts\python.exe soskuska/app.py --data .local-data/dev.sqlite3
```

macOS s Pythonom 3.12 a Tk:

```sh
python3.12 -m venv .venv-macos
.venv-macos/bin/python -m pip install -r soskuska/requirements.txt
.venv-macos/bin/python soskuska/app.py --data .local-data/dev.sqlite3
```

Linux, požiadavky Tk a riešenie problémov sú v [návode pre vývojárov](DEVELOPMENT.md).

## 4. Nastav autora pre tento klon

Pred prvým commitom nastav vlastné meno a adresu, ktorú chceš mať v histórii. Nasledujúce dve hodnoty sú príklady — nahraď ich svojimi. GitHub ponúka aj súkromnú adresu `noreply` v nastaveniach e-mailu.

```sh
git config user.name "Tvoje meno"
git config user.email "tvoja-adresa@example.com"
```

Príkazy bez `--global` menia iba tento repozitár. Autor commitu a prihlásenie do GitHubu sú dve odlišné veci.

## 5. Bežný pracovný postup

Začni z čistej vetvy `main`:

```sh
git switch main
git pull --ff-only
git switch -c feature/my-change
```

Uprav súbory a spusti relevantné kontroly podľa [CONTRIBUTING](CONTRIBUTING.md). Potom skontroluj a ulož zmeny:

```sh
git status
git diff
git add README.md
git diff --cached
git commit -m "docs: clarify setup instructions"
git push -u origin feature/my-change
```

`README.md`, názov vetvy a správa sú príklady. Do `git add` uveď súbory skutočnej zmeny; odosielaj iba skontrolované súbory. `commit` uloží históriu lokálne, `push` ju odošle na GitHub. Zápis vyžaduje oprávnenie k repozitáru.

Na GitHube otvor **Compare & pull request**, vyber základ `main`, opíš zmenu a skutočne vykonané kontroly. Po kontrole a zlúčení sa vráť na `main` a aktualizuj ju. Táto inštrukcia sama neudeľuje oprávnenie meniť prístup alebo viditeľnosť repozitára.

## 6. Aktualizácia existujúceho klonu

```sh
git status
git switch main
git pull --ff-only
```

Pred prepnutím a stiahnutím vyrieš vlastné neuložené zmeny. Ak `--ff-only` oznámi rozdielnu históriu, zastav sa a skontroluj ju; nepridávaj naslepo `--force` ani nemaž prácu cez `reset --hard`.

Po zmene `requirements.txt` zopakuj inštaláciu knižníc cez Python svojho prostredia. Po aktualizácii kódu aplikáciu reštartuj. Databázy a prostredia sa Gitom nesynchronizujú.

## Rýchly prehľad

| Príkaz | Význam |
| --- | --- |
| `git status` | Stav vetvy a upravené súbory |
| `git diff` | Zmeny ešte nepripravené do commitu |
| `git diff --cached` | Obsah ďalšieho commitu |
| `git log --oneline -5` | Posledných päť commitov |
| `git remote -v` | Adresa vzdialeného repozitára |
| `git pull --ff-only` | Stiahnutie zmien bez automatického zlučovacieho commitu |

Nahrávajú sa zdroje a dokumentácia. Virtuálne prostredia, `.local-data/`, SQLite databázy a `.env` sú ignorované. Stiahnutý ZIP nemá históriu `.git`; na prácu s Gitom začni klonovaním do iného priečinka.
