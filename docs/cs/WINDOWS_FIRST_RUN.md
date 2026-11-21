# Windows od nuly — první spuštění SOSkúška

[English](../WINDOWS_FIRST_RUN.md) · [Čeština](WINDOWS_FIRST_RUN.md) · [Slovenčina](../sk/WINDOWS_FIRST_RUN.md) · [Русский](../ru/WINDOWS_FIRST_RUN.md)

Pro přenosné EXE bez Pythonu viz [Windows portable](WINDOWS_PORTABLE.md).

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

Fungují Dashboard, My Subjects, checklist, vyhledávání a časovač pro konkrétní předmět. Přidej svůj první předmět; nová databáze je prázdná a přehled ukazuje skutečně uložená data. Question bank, Practice Tests, Flashcards, Statistics, volitelný AI Tutor a Settings jsou také implementované.

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

## Banka témat a otázek

V My Subjects zvol u předmětu **Questions**. Přidej téma přes New topic a otázku přes New question. Každá otázka má čtyři různé povinné odpovědi A–D, právě jednu správnou odpověď, obtížnost Easy/Medium/Hard a volitelné vysvětlení. Téma je volitelné. Formulář zachová rozepsaný obsah při chybě validace nebo zápisu.

Témata lze přejmenovat a smazat; vyber téma ve filtru a použij Rename selected topic nebo Delete selected topic. Otázky lze upravovat a mazat. Hledání v textu otázky se kombinuje s filtrem tématu a obtížnosti. Počty na kartách předmětů vycházejí z uloženého obsahu. Smazání tématu ponechá jeho otázky v No topic. Smazání předmětu po výslovném upozornění odstraní jeho témata a otázky, ale zachová čas i historii studia.

Jde o editor obsahu: správná odpověď je viditelná. Procvičování a hodnocení najdeš v Practice Tests. Import otázek z CSV je dostupný; obrázky zatím nejsou implementované.

## Practice Tests — procvičování (v0.4.0)

Nejprve vytvoř předmět a otázky přes My Subjects → Questions. V Practice Tests vyber předmět, téma (všechna / bez tématu / konkrétní), obtížnost a 1–100 dostupných otázek. Volitelný limit je 5, 10, 15, 30 nebo 60 minut; Untimed nemá limit. Otázky se náhodně vyberou bez opakování.

Odpověď se uloží po každém výběru; lze ji změnit nebo vymazat přes Clear answer. Previous/Next mění uloženou pozici. Při návratu nebo restartu lze pokračovat přes Resume test. Najednou může být rozpracovaný jeden test. Discard test vyžaduje potvrzení a odstraní pouze tento rozpracovaný pokus.

Finish test po potvrzení uloží výsledek; nevyplněné otázky se počítají jako nesprávné. Správné odpovědi a vysvětlení se zobrazí až po odevzdání. Časový limit běží i mimo obrazovku a při zavřené aplikaci; po vypršení se test automaticky dokončí při běhu nebo návratu do aplikace. Výsledek a otázky jsou snímkem ze začátku pokusu: pozdější úprava či smazání původního obsahu je nezmění. Historie zpřístupňuje všechny dokončené testy po 20 na stránku s filtry uloženého názvu předmětu a místních dat.

Procvičování je dostupné od v0.4.0. Procvičování nepřidává smyšlený čas do součtů časovače. Import kartiček z CSV je dostupný; AI Tutor má vlastní volitelný chat; celkový přehled je ve Statistics.

## Kartičky a opakování (v0.5.0)

V postranní nabídce otevři **Flashcards**. New deck vytvoří balíček pro existující předmět; název musí být jedinečný mezi všemi balíčky. Předmět balíčku se potom nemění, název a popis ano. Open deck umožní přidat a upravovat kartičky. Přední strana má 1–2000 znaků, zadní 1–4000; Search hledá v obou stranách. Seznam zobrazuje nejvýše 100 výsledků, další najdeš užším hledáním.

[Podrobný návod a pravidla](FLASHCARDS.md).

## Statistiky (v0.6.0)

V nabídce **Statistics** zvol Last 7 days, Last 30 days nebo All time. Přehled ukazuje uložený čas a sezení, otázkami váženou úspěšnost dokončených testů, počty vlastních hodnocení kartiček, čas podle předmětu a denní aktivitu. Refresh nebo návrat na obrazovku načte nový snímek. Nejde o měření zvládnutí učiva.

[Podrobná pravidla](STATISTICS.md).

## AI Tutor s Ollamou (v0.7.0)

V AI Tutor připoj vlastní Ollama server přes Connect / refresh, vyber model a jazyk odpovědi a zadej otázku. Odpověď přichází průběžně; Stop ji zastaví. Ostatní obrazovky zůstávají použitelné během generování i bez Ollamy. Chat se ukládá do místní databáze a lze jej otevřít po restartu; viz průvodce historií.

[Návod AI Tutor](AI_TUTOR.md).

## Nastavení

Konverzace se ukládají do místní databáze a záloh. Volby spojení lze výslovně uložit v [Settings](SETTINGS.md); bez Save jsou dočasné.

[Nastavení](SETTINGS.md).

## Záloha a obnova

Settings nyní nabízí ruční místní zálohu a ověřenou obnovu s bezpečnostní kopií před nahrazením. Aktuální schéma je 8. Obnova zavře aplikaci; potom ji spusť znovu. Viz [Záloha a obnova](BACKUP_RESTORE.md).

## Import otázek z CSV

Banka otázek nyní podporuje import UTF-8 CSV do existujícího předmětu: šablona s hlavičkou, stránkovaný náhled, odmítnutí přesných duplicit a jedno atomické uložení. Maximum 2 MiB / 500 záznamů; seznam ukazuje 50 otázek na stránku. Aktuální schéma je 8. [Import otázek z CSV](QUESTION_CSV_IMPORT.md).

## Import kartiček z CSV

Flashcards nyní podporuje import UTF-8 CSV do existujícího balíčku: šablonu s hlavičkou, stránkovaný náhled, odmítnutí přesných duplicit a jedno atomické uložení. Maximum 2 MiB / 500 záznamů. Nové kartičky jsou ihned splatné; původní termíny a historie hodnocení zůstávají zachované. Aktuální schéma je 8. [Import kartiček z CSV](FLASHCARD_CSV_IMPORT.md).

## Uložené konverzace AI Tutor

AI Tutor nyní ukládá konverzace lokálně včetně původního serveru/modelu a stavu odpovědi. Historii lze otevřít bez sítě, výslovně se připojit pro pokračování nebo vybranou konverzaci po potvrzení smazat. Vydáno ve v0.12.0 se schématem 7, které transakčně migruje původní studijní data. [Uložené konverzace AI Tutor](TUTOR_HISTORY.md).

## Jazyk rozhraní

Výběr jazyka rozhraní je dostupný ve v0.13.0: angličtina, čeština, slovenština a ruština. Ukládá se zvlášť od jazyka AI a použije se po restartu. Aktuální schéma je 8. [Jazyk rozhraní](UI_LANGUAGES.md).

## Přenosná verze Windows a přejímka

v0.15.0 přidává nepodepsaný přenosný ZIP pro Windows x64, sestavený a ověřený pátou úlohou CI. Přibalený pomocný program zachová oddělené CSV/zálohovací procesy; cílový počítač nepotřebuje Python. Automatické hostované kontroly a ruční seznam pro čistý počítač jsou oddělené; ruční přejímka zatím není dokončená. Vydaná verze je v0.15.0, schéma 8. [Přenosná verze Windows a přejímka](WINDOWS_PORTABLE.md) · [Kontrolní seznam](WINDOWS_ACCEPTANCE.md).
