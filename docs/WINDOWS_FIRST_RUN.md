# Windows od nuly — první spuštění SOSkúška

Návod pro člověka, který na Windows 10/11 zatím nemá Python ani vývojové nástroje. Potřebuješ internet pro první instalaci a zdrojové soubory SOSkuska. Git, VS Code, Node.js, Ollama ani placené služby nejsou pro současný Dashboard potřeba.

**Důležité:** postup vychází z aktuálního kódu a oficiální dokumentace Pythonu. Na skutečných Windows ještě nebyl celý průchod ověřený; aplikace zatím nemá vlastní instalátor `.exe`.

## 1. Nainstaluj správce Pythonu

1. Otevři prohlížeč a přejdi na [oficiální stránku Pythonu pro Windows](https://www.python.org/downloads/windows/).
2. Vyber **Python install manager** a stáhni jeho instalátor. Samotný správce ještě není požadovaná verze Pythonu; tu přidáš v dalším kroku.
3. Otevři stažený soubor a klikni na **Install / Instalovat**. Pokud je dostupné tlačítko **Launch / Spustit**, můžeš ho použít pro dokončení počátečního nastavení.
4. Po dokončení zavři případná stará okna terminálu.

Nevol **embeddable package** ani archiv zdrojového kódu Pythonu. Tento návod používá běžný Python přes správce, podle [oficiálního postupu instalace na Windows](https://docs.python.org/3/using/windows.html).

## 2. Otevři PowerShell a přidej Python 3.12

Klikni na **Start**, napiš `PowerShell` a otevři **Windows PowerShell** nebo **Terminal** s profilem PowerShell. Není potřeba spouštět jako správce. Příkazy kopíruj po jednom řádku a každý potvrď klávesou Enter. Značky `PS>` nebo trojité zpětné apostrofy nekopíruj.

```powershell
py install 3.12
```

Počkej na dokončení stažení a instalace. Pak ověř verzi:

```powershell
py -3.12 --version
```

Očekávej `Python 3.12.x`; poslední číslo se může lišit. Záměrně vybíráme řadu 3.12, nikoli automaticky nejnovější Python.

Pokud `py install` hlásí, že se snaží otevřít soubor `install`, počítač nejspíš používá starý launcher. Správce má také jednoznačný příkaz:

```powershell
pymanager install 3.12
```

Pokud není rozpoznané ani `py`, ani `pymanager`, zavři terminál, znovu jej otevři a ověř dokončení instalace správce. Nepokračuj, dokud kontrola verze nefunguje.

## 3. Ověř podporu oken

```powershell
py -3.12 -m tkinter
```

Má se otevřít malé demonstrační okno Tk. Zavři ho křížkem a vrať se do PowerShellu. Tím ověříš, že Python umí vytvářet okna. Samotná instalace CustomTkinteru chybějící modul `_tkinter` neopraví.

## 4. Získej a rozbal projekt

Projekt získáš v soukromém repozitáři [turcinv/SOSkuska](https://github.com/turcinv/SOSkuska): přihlas se k účtu s přístupem, klikni na **Code → Download ZIP** a archiv rozbal. Pokud přístup nemáš, požádej autora o archiv **SOSkuska-source.zip**. Git není potřeba. GitHub ZIP obvykle obsahuje složku `SOSkuska-main`; po rozbalení ji přejmenuj na `SOSkuska`.

1. Klikni na ZIP pravým tlačítkem a zvol **Extract All / Extrahovat vše**.
2. Uvnitř najdi složku **SOSkuska**, která přímo obsahuje `README.md`, `docs` a podsložku `soskuska`.
3. Tuto složku přesuň do své uživatelské složky. Výsledná cesta má být `C:\Users\tvoje-jmeno\SOSkuska`.
4. Ve složce `SOSkuska\soskuska` musí být `app.py` a `requirements.txt`. Pozor na dvojí zanoření `SOSkuska\SOSkuska\soskuska`.

Projekt musí být rozbalený, ne otevřený přímo uvnitř ZIPu. Virtuální prostředí z Macu nekopíruj; na Windows vytvoříš nové.

## 5. Přejdi do projektu

V PowerShellu:

```powershell
cd "$HOME\SOSkuska"
Test-Path .\soskuska\app.py
Test-Path .\soskuska\requirements.txt
```

Obě kontroly mají vypsat `True`. `$HOME` znamená tvou uživatelskou složku, nemusíš nahrazovat uživatelské jméno. Pokud jsi projekt uložil jinam, uprav cestu v `cd` a nech ji v uvozovkách. Při výsledku `False` nejdříve najdi správnou složku.

## 6. Vytvoř prostředí a nainstaluj knihovny

```powershell
py -3.12 -m venv .venv
```

Po dokončení vznikne složka `.venv`. Prázdný výstup bez chyby je v pořádku. Potom:

```powershell
.\.venv\Scripts\python.exe -m pip install -r soskuska/requirements.txt
```

Počkej na úspěšné dokončení instalace. Knihovny se instalují do projektu, ne globálně. Prostředí není potřeba aktivovat; **neměň PowerShell execution policy**. Pokud instalace vypíše chybu, nespouštěj další krok naslepo a ulož celý chybový výpis.

## 7. Spusť aplikaci

```powershell
.\.venv\Scripts\python.exe soskuska/app.py
```

Má se otevřít tmavé okno **SOSkúška** s Dashboardem a levou navigací. PowerShell nech otevřený; dokud aplikace běží, nevrátí se nový příkazový řádek. Aplikaci běžně ukonči křížkem jejího okna.

Zatím funguje Dashboard, checklist, vyhledávání a časovač. Další obrazovky jsou plánované; většina zobrazených studijních údajů je demonstrace.

## 8. Jak spouštět příště

Už neopakuj instalaci Pythonu, vytvoření prostředí ani instalaci knihoven. Otevři PowerShell a zadej:

```powershell
cd "$HOME\SOSkuska"
.\.venv\Scripts\python.exe soskuska/app.py
```

Po úspěšné první instalaci Dashboard nepotřebuje internet. Běžná data se ukládají do `%LOCALAPPDATA%\SOSkuska\dashboard.sqlite3`. Pro otevření adresáře můžeš vložit `%LOCALAPPDATA%\SOSkuska` do adresního řádku Průzkumníka; soubor nemaž, pokud chceš zachovat úkoly a čas.

## 9. Volitelné — vývoj a kontrola funkčnosti

Pro vlastní experimenty používej samostatnou databázi:

```powershell
.\.venv\Scripts\python.exe soskuska/app.py --data .local-data/dev.sqlite3
```

Kontrolní skript otevře krátce okno a používá vlastní dočasnou databázi:

```powershell
.\.venv\Scripts\python.exe soskuska/check_dashboard.py
```

Při úspěchu vypíše `PASS` a okno zavře. Pokud kontrola nebo běh selže na Windows, jde o důležitý dosud neověřený případ — pošli celý výpis, ne pouze poslední řádek.

## Nejčastější problémy

| Problém | Co udělat |
| --- | --- |
| `py` není rozpoznaný | Dokonči instalaci Python install manageru a otevři nový PowerShell; ověř také `pymanager` |
| `No suitable Python runtime found` | Proveď `py install 3.12`, při kolizi launcheru `pymanager install 3.12` |
| Kontroly souborů vracejí `False` | Jsi v nesprávné složce nebo je ZIP špatně rozbalený |
| Cesta s mezerami nefunguje | V příkazu `cd` ponech celou cestu v dvojitých uvozovkách |
| `No module named customtkinter` | Znovu proveď instalaci requirements přes `.\.venv\Scripts\python.exe` |
| Chybí `_tkinter` | Vrať se k instalaci plného Pythonu a kontrole v kroku 3; neinstaluj jen balíček přes pip |
| PowerShell blokuje `Activate.ps1` | Aktivaci vynech; všechny příkazy výše přímo spouštějí `python.exe` |
| Okno se po dvojkliku hned zavře | Spusť aplikaci z PowerShellu podle kroku 7; chyba zůstane viditelná |
| Instalace knihoven selže na síti | Ověř internet nebo firemní proxy; nevypínej ověřování certifikátů |

Podrobnosti pro další práci jsou v [návodu pro vývojáře](DEVELOPMENT.md).


Kompatibilita s původním názvem: pokud nová databáze v `SOSkuska` neexistuje a původní `ExamPrep/dashboard.sqlite3` existuje, aplikace použije tento původní soubor. Nic automaticky nekopíruje, nepřesouvá ani nepřepisuje. Explicitní `--data` má vždy přednost.
