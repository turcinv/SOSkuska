# Windows od nuly — prvé spustenie SOSkúška

Návod pre človeka, ktorý na Windows 10/11 zatiaľ nemá Python ani vývojové nástroje. Potrebuješ internet na prvú inštaláciu a zdrojové súbory SOSkuska. Git, VS Code, Node.js, Ollama ani platené služby pre súčasný Dashboard nepotrebuješ.

**Dôležité:** postup vychádza z aktuálneho kódu a oficiálnej dokumentácie Pythonu. Na skutočných Windows ešte nebol celý priechod overený; aplikácia zatiaľ nemá vlastný inštalátor `.exe`.

## 1. Nainštaluj správcu Pythonu

1. Otvor prehliadač a prejdi na [oficiálnu stránku Pythonu pre Windows](https://www.python.org/downloads/windows/).
2. Vyber **Python install manager** a stiahni jeho inštalátor. Samotný správca ešte nie je požadovaná verzia Pythonu; tú pridáš v ďalšom kroku.
3. Otvor stiahnutý súbor a klikni na **Install / Inštalovať**. Ak je dostupné tlačidlo **Launch / Spustiť**, môžeš ho použiť na dokončenie úvodného nastavenia.
4. Po dokončení zatvor prípadné staré okná terminálu.

Nevyberaj **embeddable package** ani archív zdrojového kódu Pythonu. Tento návod používa bežný Python cez správcu podľa [oficiálneho postupu inštalácie na Windows](https://docs.python.org/3/using/windows.html).

## 2. Otvor PowerShell a pridaj Python 3.12

Klikni na **Štart**, napíš `PowerShell` a otvor **Windows PowerShell** alebo **Terminal** s profilom PowerShell. Netreba spúšťať ako správca. Príkazy kopíruj po jednom riadku a každý potvrď klávesom Enter. Značky `PS>` ani trojité spätné apostrofy nekopíruj.

```powershell
py install 3.12
```

Počkaj na dokončenie sťahovania a inštalácie. Potom over verziu:

```powershell
py -3.12 --version
```

Očakávaj `Python 3.12.x`; posledné číslo sa môže líšiť. Zámerne vyberáme rad 3.12, nie automaticky najnovší Python.

Ak `py install` hlási, že sa snaží otvoriť súbor `install`, počítač zrejme používa starý spúšťač. Správca má aj jednoznačný príkaz:

```powershell
pymanager install 3.12
```

Ak nie je rozpoznané ani `py`, ani `pymanager`, zatvor terminál, znovu ho otvor a over dokončenie inštalácie správcu. Nepokračuj, kým kontrola verzie nefunguje.

## 3. Over podporu okien

```powershell
py -3.12 -m tkinter
```

Má sa otvoriť malé demonštračné okno Tk. Zatvor ho krížikom a vráť sa do PowerShellu. Tým overíš, že Python vie vytvárať okná. Samotná inštalácia CustomTkinteru chýbajúci modul `_tkinter` neopraví.

## 4. Získaj a rozbaľ projekt

Projekt získaš v súkromnom repozitári [turcinv/SOSkuska](https://github.com/turcinv/SOSkuska): prihlás sa účtom s prístupom, klikni na **Code → Download ZIP** a archív rozbaľ. Ak nemáš prístup, požiadaj autora o archív **SOSkuska-source.zip**. Git netreba. GitHub ZIP zvyčajne obsahuje priečinok `SOSkuska-main`; po rozbalení ho premenuj na `SOSkuska`.

1. Klikni na ZIP pravým tlačidlom a zvoľ **Extract All / Extrahovať všetko**.
2. Vnútri nájdi priečinok **SOSkuska**, ktorý priamo obsahuje `README.md`, `docs` a podpriečinok `soskuska`.
3. Tento priečinok presuň do svojho používateľského priečinka. Výsledná cesta má byť `C:\Users\tvoje-meno\SOSkuska`.
4. V priečinku `SOSkuska\soskuska` musia byť `app.py` a `requirements.txt`. Pozor na dvojité vnorenie `SOSkuska\SOSkuska\soskuska`.

Projekt musí byť rozbalený, nie otvorený priamo v ZIPe. Virtuálne prostredie z Macu nekopíruj; na Windows vytvoríš nové.

## 5. Prejdi do projektu

V PowerShelli:

```powershell
cd "$HOME\SOSkuska"
Test-Path .\soskuska\app.py
Test-Path .\soskuska\requirements.txt
```

Obe kontroly majú vypísať `True`. `$HOME` znamená tvoj používateľský priečinok, nemusíš nahrádzať používateľské meno. Ak si projekt uložil inam, uprav cestu v `cd` a ponechaj ju v úvodzovkách. Pri výsledku `False` najprv nájdi správny priečinok.

## 6. Vytvor prostredie a nainštaluj knižnice

```powershell
py -3.12 -m venv .venv
```

Po dokončení vznikne priečinok `.venv`. Prázdny výstup bez chyby je v poriadku. Potom:

```powershell
.\.venv\Scripts\python.exe -m pip install -r soskuska/requirements.txt
```

Počkaj na úspešné dokončenie inštalácie. Knižnice sa inštalujú do projektu, nie globálne. Prostredie netreba aktivovať; **nemeň PowerShell execution policy**. Ak inštalácia vypíše chybu, nespúšťaj ďalší krok naslepo a ulož celý chybový výpis.

## 7. Spusť aplikáciu

```powershell
.\.venv\Scripts\python.exe soskuska/app.py
```

Má sa otvoriť tmavé okno **SOSkúška** s Dashboardom a ľavou navigáciou. PowerShell nechaj otvorený; kým aplikácia beží, nezobrazí sa nový príkazový riadok. Aplikáciu bežne ukonči krížikom jej okna.

Fungujú Dashboard, My Subjects, zoznam úloh, vyhľadávanie a časovač pre konkrétny predmet. Pridaj svoj prvý predmet; nová databáza je prázdna a prehľad ukazuje skutočne uložené údaje. Ostatné študijné obrazovky zostávajú plánované.

## 8. Ako spúšťať nabudúce

Už neopakuj inštaláciu Pythonu, vytvorenie prostredia ani inštaláciu knižníc. Otvor PowerShell a zadaj:

```powershell
cd "$HOME\SOSkuska"
.\.venv\Scripts\python.exe soskuska/app.py
```

Po úspešnej prvej inštalácii Dashboard nepotrebuje internet. Bežné údaje sa ukladajú do `%LOCALAPPDATA%\SOSkuska\dashboard.sqlite3`. Na otvorenie adresára môžeš vložiť `%LOCALAPPDATA%\SOSkuska` do adresného riadka Prieskumníka; súbor nemaž, ak chceš zachovať úlohy a čas.

## 9. Voliteľné — vývoj a kontrola funkčnosti

Na vlastné experimenty používaj samostatnú databázu:

```powershell
.\.venv\Scripts\python.exe soskuska/app.py --data .local-data/dev.sqlite3
```

Kontrolný skript krátko otvorí okno a používa vlastnú dočasnú databázu:

```powershell
.\.venv\Scripts\python.exe soskuska/check_dashboard.py
```

Pri úspechu vypíše `PASS` a okno zatvorí. Ak kontrola alebo beh na Windows zlyhá, ide o dôležitý dosiaľ neoverený prípad — pošli celý výpis, nie iba posledný riadok.

## Najčastejšie problémy

| Problém | Čo urobiť |
| --- | --- |
| `py` nie je rozpoznaný | Dokonči inštaláciu Python install managera a otvor nový PowerShell; over aj `pymanager` |
| `No suitable Python runtime found` | Vykonaj `py install 3.12`, pri konflikte spúšťača `pymanager install 3.12` |
| Kontroly súborov vracajú `False` | Si v nesprávnom priečinku alebo je ZIP zle rozbalený |
| Cesta s medzerami nefunguje | V príkaze `cd` ponechaj celú cestu v dvojitých úvodzovkách |
| `No module named customtkinter` | Znovu nainštaluj requirements cez `.\.venv\Scripts\python.exe` |
| Chýba `_tkinter` | Vráť sa k inštalácii plného Pythonu a kontrole v kroku 3; neinštaluj iba balík cez pip |
| PowerShell blokuje `Activate.ps1` | Aktiváciu vynechaj; všetky príkazy vyššie priamo spúšťajú `python.exe` |
| Okno sa po dvojkliku hneď zatvorí | Spusť aplikáciu z PowerShellu podľa kroku 7; chyba zostane viditeľná |
| Inštalácia knižníc zlyhá na sieti | Over internet alebo firemné proxy; nevypínaj overovanie certifikátov |

Podrobnosti pre ďalšiu prácu sú v [návode pre vývojárov](DEVELOPMENT.md).


Kompatibilita s pôvodným názvom: ak nová databáza v `SOSkuska` neexistuje a pôvodná `ExamPrep/dashboard.sqlite3` existuje, aplikácia použije tento pôvodný súbor. Nič automaticky nekopíruje, nepresúva ani neprepisuje. Výslovné `--data` má vždy prednosť.

## Banka tém a otázok

V My Subjects zvoľ pri predmete **Questions**. Pridaj tému cez New topic a otázku cez New question. Každá otázka má štyri rôzne povinné odpovede A–D, práve jednu správnu odpoveď, náročnosť Easy/Medium/Hard a voliteľné vysvetlenie. Téma je voliteľná. Formulár zachová rozpísaný obsah pri chybe validácie alebo zápisu.

Témy možno premenovať a vymazať; vyber tému vo filtri a použi Rename selected topic alebo Delete selected topic. Otázky možno upravovať a mazať. Hľadanie v texte otázky sa kombinuje s filtrom témy a náročnosti. Počty na kartách predmetov vychádzajú z uloženého obsahu. Vymazanie témy ponechá jej otázky v No topic. Vymazanie predmetu po výslovnom upozornení odstráni jeho témy a otázky, ale zachová čas aj históriu štúdia.

Ide o editor obsahu: správna odpoveď je viditeľná. Spúšťanie a hodnotenie cvičných testov, import a obrázky zatiaľ nie sú implementované.
