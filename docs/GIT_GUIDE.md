# Klonování a základní práce s Gitem

Git ukládá historii změn na tvém počítači. GitHub uchovává vzdálenou kopii a umožňuje spolupráci. ZIP stačí ke spuštění aplikace; pro vývoj a odesílání změn použij klon.

## 1. Získej přístup a Git

Repozitář [turcinv/SOSkuska](https://github.com/turcinv/SOSkuska) je **soukromý**. Nejdříve jej otevři v prohlížeči pod účtem, který má přístup. Chyba 404 může znamenat chybějící oprávnění.

Ověř instalaci Gitu:

```sh
git --version
```

Pokud příkaz neexistuje, nainstaluj Git podle [oficiálního návodu pro svou platformu](https://git-scm.com/downloads/). Na Windows použij Git for Windows a ponech Git Credential Manager; po instalaci otevři nový PowerShell. Na macOS můžeš využít Apple Command Line Tools podle nabídky systému nebo jinou možnost z oficiálního návodu. Na Linuxu použij balíček své distribuce.

Při HTTPS klonování může Git Credential Manager otevřít přihlášení v prohlížeči. Přihlas se účtem s přístupem. Samotné přihlášení na webu nemusí přihlásit také Git. Heslo k účtu nevkládej do adresy repozitáře; podrobnosti popisuje [GitHub dokumentace přihlašování](https://docs.github.com/en/get-started/git-basics/caching-your-github-credentials-in-git). Pokud už používáš GitHub CLI, můžeš využít `gh auth login` a `gh auth setup-git`.

## 2. Naklonuj projekt

Přejdi v terminálu do nadřazené složky, kam chceš projekt uložit. Pak spusť:

```sh
git clone https://github.com/turcinv/SOSkuska.git
cd SOSkuska
git status
```

Vznikne nová složka `SOSkuska` s historií `.git`. Výpis má ukázat větev `main` a žádné neuložené změny. Pokud cílová složka už existuje, neklonuj přes ni; použij jinou nadřazenou složku. Existující skutečný klon aktualizuj pomocí `git pull --ff-only`.

## 3. Připrav Python a spusť aplikaci

Klon neobsahuje virtuální prostředí ani databázi. Na každém počítači vytvoř vlastní prostředí. Pokud ještě nemáš Python na Windows, projdi nejprve [návod Windows od nuly](WINDOWS_FIRST_RUN.md); kroky pro stažení ZIPu přeskoč, protože už máš klon.

Windows / PowerShell, pokud je Python 3.12 již nainstalovaný:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r soskuska/requirements.txt
.\.venv\Scripts\python.exe soskuska/app.py --data .local-data/dev.sqlite3
```

macOS s Pythonem 3.12 a Tk:

```sh
python3.12 -m venv .venv-macos
.venv-macos/bin/python -m pip install -r soskuska/requirements.txt
.venv-macos/bin/python soskuska/app.py --data .local-data/dev.sqlite3
```

Linux, požadavky Tk a řešení problémů jsou v [návodu pro vývojáře](DEVELOPMENT.md).

## 4. Nastav autora pro tento klon

Před prvním commitem nastav vlastní jméno a adresu, kterou chceš mít v historii. Následující dvě hodnoty jsou příklady — nahraď je svými. GitHub nabízí také soukromou adresu `noreply` v nastavení e-mailu.

```sh
git config user.name "Tvoje jméno"
git config user.email "tvoje-adresa@example.com"
```

Příkazy bez `--global` mění pouze tento repozitář. Autor commitu a přihlášení ke GitHubu jsou dvě různé věci.

## 5. Běžný pracovní postup

Začni z čisté větve `main`:

```sh
git switch main
git pull --ff-only
git switch -c feature/my-change
```

Uprav soubory a spusť relevantní kontroly podle [CONTRIBUTING](../CONTRIBUTING.md). Pak zkontroluj a ulož změny:

```sh
git status
git diff
git add README.md
git diff --cached
git commit -m "docs: clarify setup instructions"
git push -u origin feature/my-change
```

`README.md`, název větve a zpráva jsou příklady. Do `git add` uveď soubory své skutečné změny; odesílej jen zkontrolované soubory. `commit` uloží historii lokálně, `push` ji odešle na GitHub. Zápis vyžaduje oprávnění k repozitáři.

Na GitHubu otevři **Compare & pull request**, zvol základ `main`, popiš změnu a skutečně provedené kontroly. Po kontrole a sloučení se vrať na `main` a aktualizuj ji. Tato instrukce sama neuděluje oprávnění měnit přístup nebo viditelnost repozitáře.

## 6. Aktualizace existujícího klonu

```sh
git status
git switch main
git pull --ff-only
```

Před přepnutím a stažením vyřeš vlastní neuložené změny. Pokud `--ff-only` oznámí rozdílnou historii, zastav se a zkontroluj ji; nepřidávej naslepo `--force` ani nemaž práci přes `reset --hard`.

Po změně `requirements.txt` zopakuj instalaci knihoven přes Python svého prostředí. Po aktualizaci kódu aplikaci restartuj. Databáze a prostředí se Gitem nesynchronizují.

## Rychlý přehled

| Příkaz | Význam |
| --- | --- |
| `git status` | Stav větve a upravené soubory |
| `git diff` | Změny ještě nepřipravené do commitu |
| `git diff --cached` | Obsah příštího commitu |
| `git log --oneline -5` | Posledních pět commitů |
| `git remote -v` | Adresa vzdáleného repozitáře |
| `git pull --ff-only` | Stažení změn bez automatického slučovacího commitu |

Nahrávají se zdroje a dokumentace. Virtuální prostředí, `.local-data/`, SQLite databáze a `.env` jsou ignorované. Stažený ZIP nemá historii `.git`; ke Git práci začni klonováním do jiné složky.
