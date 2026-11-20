# Windows od nuly — prvé spustenie SOSkúška

[English](../WINDOWS_FIRST_RUN.md) · [Čeština](../cs/WINDOWS_FIRST_RUN.md) · [Slovenčina](WINDOWS_FIRST_RUN.md) · [Русский](../ru/WINDOWS_FIRST_RUN.md)

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

Fungujú Dashboard, My Subjects, zoznam úloh, vyhľadávanie a časovač pre konkrétny predmet. Pridaj svoj prvý predmet; nová databáza je prázdna a prehľad ukazuje skutočne uložené údaje. Question bank, Practice Tests, Flashcards, Statistics, voliteľný AI Tutor a Settings sú tiež implementované.

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

Ide o editor obsahu: správna odpoveď je viditeľná. Precvičovanie a hodnotenie nájdeš v Practice Tests. Import otázok z CSV je dostupný; obrázky zatiaľ nie sú implementované.

## Practice Tests — precvičovanie (v0.4.0)

Najprv vytvor predmet a otázky cez My Subjects → Questions. V Practice Tests vyber predmet, tému (všetky / bez témy / konkrétna), náročnosť a 1–100 dostupných otázok. Voliteľný limit je 5, 10, 15, 30 alebo 60 minút; Untimed nemá limit. Otázky sa náhodne vyberú bez opakovania.

Odpoveď sa uloží po každom výbere; možno ju zmeniť alebo vymazať cez Clear answer. Previous/Next menia uloženú pozíciu. Pri návrate alebo reštarte možno pokračovať cez Resume test. Naraz môže byť rozpracovaný jeden test. Discard test vyžaduje potvrdenie a odstráni iba tento rozpracovaný pokus.

Finish test po potvrdení uloží výsledok; nevyplnené otázky sa počítajú ako nesprávne. Správne odpovede a vysvetlenia sa zobrazia až po odovzdaní. Časový limit beží aj mimo obrazovky a pri zatvorenej aplikácii; po uplynutí sa test automaticky dokončí pri behu alebo návrate do aplikácie. Výsledok a otázky sú snímkou zo začiatku pokusu: neskoršia úprava či vymazanie pôvodného obsahu ich nezmení. História zobrazuje posledných 20 dokončených testov; staršie záznamy zostávajú v databáze.

Precvičovanie je dostupné od v0.4.0. Precvičovanie nepridáva vymyslený čas do súčtov časovača. Import kartičiek z CSV je dostupný; AI Tutor má vlastný voliteľný chat; celkový prehľad je v Statistics.

## Kartičky a opakovanie (v0.5.0)

V bočnej ponuke otvor **Flashcards**. New deck vytvorí balíček pre existujúci predmet; názov musí byť jedinečný medzi všetkými balíčkami. Predmet balíčka sa potom nemení, názov a popis áno. Open deck umožní pridať a upravovať kartičky. Predná strana má 1–2000 znakov, zadná 1–4000; Search hľadá v oboch stranách. Zoznam zobrazuje najviac 100 výsledkov, ďalšie nájdeš užším hľadaním.

[Podrobný návod a pravidlá](FLASHCARDS.md).

## Štatistiky (v0.6.0)

V ponuke **Statistics** zvoľ Last 7 days, Last 30 days alebo All time. Prehľad ukazuje uložený čas a relácie, úspešnosť dokončených testov váženú otázkami, počty vlastných hodnotení kartičiek, čas podľa predmetu a dennú aktivitu. Refresh alebo návrat na obrazovku načíta novú snímku. Nejde o meranie zvládnutia učiva.

[Podrobné pravidlá](STATISTICS.md).

## AI Tutor s Ollamou (v0.7.0)

V AI Tutor pripoj vlastný server Ollama cez Connect / refresh, vyber model a jazyk odpovede a zadaj otázku. Odpoveď prichádza priebežne; Stop ju zastaví. Ostatné obrazovky zostávajú použiteľné počas generovania aj bez Ollamy. Chat sa ukladá do miestnej databázy a možno ho otvoriť po reštarte; pozri sprievodcu históriou.

[Návod AI Tutor](AI_TUTOR.md).

## Nastavenia

Konverzácie sa ukladajú do miestnej databázy a záloh. Voľby spojenia možno výslovne uložiť v [Settings](SETTINGS.md); bez Save sú dočasné.

[Nastavenia](SETTINGS.md).

## Záloha a obnova

Settings teraz ponúka ručnú miestnu zálohu a overenú obnovu s bezpečnostnou kópiou pred nahradením. Aktuálna schéma je 7. Obnova zatvorí aplikáciu; potom ju spusti znovu. Pozri [Záloha a obnova](BACKUP_RESTORE.md).

## Import otázok z CSV

Banka otázok teraz podporuje import UTF-8 CSV do existujúceho predmetu: šablóna s hlavičkou, stránkovaný náhľad, odmietnutie presných duplicít a jedno atomické uloženie. Maximum 2 MiB / 500 záznamov; zoznam ukazuje 50 otázok na stránku. Aktuálna schéma je 7. [Import otázok z CSV](QUESTION_CSV_IMPORT.md).

## Import kartičiek z CSV

Flashcards teraz podporuje import UTF-8 CSV do existujúceho balíčka: šablónu s hlavičkou, stránkovaný náhľad, odmietnutie presných duplicít a jedno atomické uloženie. Maximum 2 MiB / 500 záznamov. Nové kartičky sú ihneď splatné; pôvodné termíny a história hodnotení zostávajú zachované. Aktuálna schéma je 7. [Import kartičiek z CSV](FLASHCARD_CSV_IMPORT.md).

## Uložené konverzácie AI Tutor

AI Tutor teraz ukladá konverzácie lokálne vrátane pôvodného servera/modelu a stavu odpovede. Históriu možno otvoriť bez siete, výslovne sa pripojiť na pokračovanie alebo vybranú konverzáciu po potvrdení zmazať. Vydané vo v0.12.0 so schémou 7, ktorá transakčne migruje pôvodné študijné údaje. [Uložené konverzácie AI Tutor](TUTOR_HISTORY.md).
