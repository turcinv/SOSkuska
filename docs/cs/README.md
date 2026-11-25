# SOSkúška

[English](../../README.md) · [Čeština](README.md) · [Slovenčina](../sk/README.md) · [Русский](../ru/README.md)

**Vydání: [v0.19.0](https://github.com/turcinv/SOSkuska/releases/tag/v0.19.0)** — zdrojový kód a přenosný ZIP pro Windows x64. Přehled je v [historii změn](CHANGELOG.md). Instalátor není součástí.

Název aplikace je **SOSkúška**. Repozitář a kořenová složka jsou **SOSkuska**, zdrojový adresář `soskuska/`; technické názvy používají podobu bez diakritiky.

Lokální desktopový studijní asistent v Pythonu a CustomTkinteru. Implementované jsou Dashboard a My Subjects: správa předmětů a termínů zkoušek, denní checklist, vyhledávání a časovač propojený s předmětem. Úkoly a odstudovaný čas ukládá do SQLite na zařízení uživatele.

**Stav: funkční prototyp se skutečnými lokálními daty.** Předměty lze vytvářet, upravovat a mazat; přehled používá uložené časy a termíny. Nová databáze začíná prázdná. AI Tutor nabízí volitelný chat s místní historií přes Ollamu. Běh nevyžaduje Superdesign, placené API ani internet.

## Klonování a první instalace

Repozitář je soukromý; potřebuješ Git a účet s přístupem. V terminálu přejdi do složky, kam chceš projekt uložit:

```sh
git clone https://github.com/turcinv/SOSkuska.git
cd SOSkuska
```

Klon neobsahuje Python prostředí ani databázi. Pokračuj podle [instalace pro svůj systém](DEVELOPMENT.md). Instalaci Gitu, přihlášení, aktualizace a práci s větvemi popisuje [Git krok za krokem](GIT_GUIDE.md).

## Rychlé spuštění na tomto Macu

Z kořenové složky projektu:

```sh
.venv-macos/bin/python soskuska/app.py
```

Nebo otevři `soskuska/run-macos.command`. Připravené prostředí používá Python 3.12.13 / Tk 9.0. Staré `.venv-desktop` nepoužívej: na tomto Macu zobrazovalo prázdné okno.

## Dokumentace

**Začínáš na čistých Windows?** Použij podrobný návod: [Česky](WINDOWS_FIRST_RUN.md) · [Slovensky](../sk/WINDOWS_FIRST_RUN.md) · [Русский](../ru/WINDOWS_FIRST_RUN.md). Vede od instalace Pythonu až po první spuštění; Git ani editor nejsou potřeba.


| Dokument | Obsah |
| --- | --- |
| [Jednoduché vysvětlení](HOW_IT_WORKS.md) | Co se děje při spuštění, klikání a ukládání |
| [Současná architektura](CURRENT_ARCHITECTURE.md) | Skutečné moduly, datové toky, databáze a omezení |
| [Plánovaná architektura](PLANNED_ARCHITECTURE.md) | Budoucí členění, Ollama a etapy rozvoje |
| [Vývoj a spuštění](DEVELOPMENT.md) | Instalace, příkazy, kontroly a řešení problémů |
| [Práce s Gitem](GIT_GUIDE.md) | Klonování, přihlášení, větve, commity a aktualizace |
| [Přispívání](CONTRIBUTING.md) | Kontroly, pull requesty a hlášení chyb |
| [Historie změn](CHANGELOG.md) | Přehled změn prototypu |
| [Pokyny pro asistenty](../../AGENTS.md) | AGENTS.md pro další vývoj aplikace |

## Složky

```text
soskuska/          Nativní aplikace a kontrolní skript
soskuska-local/    Starší samostatný HTML návrh; vizuální reference
docs/             Dokumentace
```

Primární cílové platformy jsou Windows/Linux; macOS je také aktuální vývojové prostředí. Nativní kontroly prošly na macOS; CI ověřuje jednotkové testy na třech systémech a GUI na Linuxu. Ruční ověření Windows/Linux a fyzických gest zatím chybí. Instalátor zatím není vytvořený. Samostatný repozitář: [turcinv/SOSkuska](https://github.com/turcinv/SOSkuska). Repozitář je soukromý; přístup vyžaduje oprávnění.

## Banka témat a otázek

V My Subjects zvol u předmětu **Questions**. Přidej téma přes New topic a otázku přes New question. Každá otázka má čtyři různé povinné odpovědi A–D, právě jednu správnou odpověď, obtížnost Easy/Medium/Hard a volitelné vysvětlení. Téma je volitelné. Formulář zachová rozepsaný obsah při chybě validace nebo zápisu.

Témata lze přejmenovat a smazat; vyber téma ve filtru a použij Rename selected topic nebo Delete selected topic. Otázky lze upravovat a mazat. Hledání v textu otázky se kombinuje s filtrem tématu a obtížnosti. Počty na kartách předmětů vycházejí z uloženého obsahu. Smazání tématu ponechá jeho otázky v No topic. Smazání předmětu po výslovném upozornění odstraní jeho témata a otázky, ale zachová čas i historii studia.

Jde o editor obsahu: správná odpověď je viditelná. Procvičování a hodnocení najdeš v Practice Tests. Import otázek z CSV je dostupný; obrázky zatím nejsou implementované.

## Practice Tests — procvičování (v0.4.0)

Nejprve vytvoř předmět a otázky přes My Subjects → Questions. V Practice Tests vyber předmět, téma (všechna / bez tématu / konkrétní), obtížnost a 1–100 dostupných otázek. Volitelný limit je 5, 10, 15, 30 nebo 60 minut; Untimed nemá limit. Otázky se náhodně vyberou bez opakování.

Odpověď se uloží po každém výběru; lze ji změnit nebo vymazat přes Clear answer. Previous/Next mění uloženou pozici. Při návratu nebo restartu lze pokračovat přes Resume test. Najednou může být rozpracovaný jeden test. Discard test vyžaduje potvrzení a odstraní pouze tento rozpracovaný pokus.

Finish test po potvrzení uloží výsledek; nevyplněné otázky se počítají jako nesprávné. Správné odpovědi a vysvětlení se zobrazí až po odevzdání. Časový limit běží i mimo obrazovku a při zavřené aplikaci; po vypršení se test automaticky dokončí při běhu nebo návratu do aplikace. Výsledek a otázky jsou snímkem ze začátku pokusu: pozdější úprava či smazání původního obsahu je nezmění. Historie zpřístupňuje všechny dokončené testy po 20 na stránku s filtry uloženého názvu předmětu a místních dat.

Procvičování je dostupné od v0.4.0. Procvičování nepřidává smyšlený čas do součtů časovače. Import kartiček z CSV je dostupný; AI Tutor má vlastní volitelný chat; celkový přehled je ve Statistics.

## Průběžná integrace (CI)

CI: Python 3.12, jednotkové testy na třech systémech a čtrnáct GUI kontrol na Ubuntu/Xvfb. [Výsledky](https://github.com/turcinv/SOSkuska/actions/workflows/ci.yml).

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

Hlavní dokumentace je anglicky v kořeni repozitáře a v `docs/`. Česká verze je v `docs/cs/`, slovenská v `docs/sk/` a ruská v `docs/ru/`. AGENTS.md zůstává anglicky; konverzace může být česky, slovensky, anglicky nebo rusky.

## Záloha a obnova

Settings nyní nabízí ruční místní zálohu a ověřenou obnovu s bezpečnostní kopií před nahrazením. Aktuální schéma je 10. Obnova zavře aplikaci; potom ji spusť znovu. Viz [Záloha a obnova](BACKUP_RESTORE.md).

## Import otázek z CSV

Banka otázek nyní podporuje import UTF-8 CSV do existujícího předmětu: šablona s hlavičkou, stránkovaný náhled, odmítnutí přesných duplicit a jedno atomické uložení. Maximum 2 MiB / 500 záznamů; seznam ukazuje 50 otázek na stránku. Aktuální schéma je 10. [Import otázek z CSV](QUESTION_CSV_IMPORT.md).

## Import kartiček z CSV

Flashcards nyní podporuje import UTF-8 CSV do existujícího balíčku: šablonu s hlavičkou, stránkovaný náhled, odmítnutí přesných duplicit a jedno atomické uložení. Maximum 2 MiB / 500 záznamů. Nové kartičky jsou ihned splatné; původní termíny a historie hodnocení zůstávají zachované. Aktuální schéma je 10. [Import kartiček z CSV](FLASHCARD_CSV_IMPORT.md).

[Poznatky ze sezení a předání projektu](SESSION_LESSONS.md)

## Uložené konverzace AI Tutor

AI Tutor nyní ukládá konverzace lokálně včetně původního serveru/modelu a stavu odpovědi. Historii lze otevřít bez sítě, výslovně se připojit pro pokračování nebo vybranou konverzaci po potvrzení smazat. Vydáno ve v0.12.0 se schématem 7, které transakčně migruje původní studijní data. [Uložené konverzace AI Tutor](TUTOR_HISTORY.md).

## Jazyk rozhraní

Výběr jazyka rozhraní je dostupný ve v0.13.0: angličtina, čeština, slovenština a ruština. Ukládá se zvlášť od jazyka AI a použije se po restartu. Aktuální schéma je 10. [Jazyk rozhraní](UI_LANGUAGES.md).

## Historie testů

Historie testů nyní nabízí všechny dokončené pokusy po 20 na stránku, filtr uloženého názvu předmětu a místních dat včetně obou hranic a otevření uloženého rozboru odpovědí. Koncepty filtrů a použitá stránka přežijí navigaci; chyba čtení zachová předchozí výsledky. Schéma zůstává 8. [Historie testů](PRACTICE_HISTORY.md).

## Přenosná verze Windows a přejímka

v0.15.0 přidává nepodepsaný přenosný ZIP pro Windows x64, sestavený a ověřený pátou úlohou CI. Přibalený pomocný program zachová oddělené CSV/zálohovací procesy; cílový počítač nepotřebuje Python. Automatické hostované kontroly a ruční seznam pro čistý počítač jsou oddělené; ruční přejímka zatím není dokončená. Vydaná verze je v0.19.0, schéma 10. [Přenosná verze Windows a přejímka](WINDOWS_PORTABLE.md) · [Kontrolní seznam](WINDOWS_ACCEPTANCE.md).

## Nastavení vzhledu

v0.16.0 přidává uložené Light/Dark/System, použité po Save bez obnovy obrazovek a ztráty aktivní práce. System sleduje Windows/macOS, na Linuxu používá Light. Aktuální schéma je 10. Uživatel 22. listopadu 2026 potvrdil dokončení testování základu a schválil sloučení PR #32. [Nastavení vzhledu](APPEARANCE.md).

## Další kroky · 22. listopadu 2026

Stav 22. listopadu 2026: uživatel potvrdil dokončení testování v0.15.0 a schválil PR #32. Tento seznam nyní cílí na v0.19.0; jednotlivé výsledky čistého počítače/DPI zde nejsou zaznamenané. Nezaškrtnuté body zůstávají neověřené; při testování nového vydání doplň důkazy pro konkrétní zařízení. [Další kroky · 22. listopadu 2026](NEXT_STEPS.md).

## Obnova soustředění po pádu

v0.17.0 přidává obnovu soustředění po pádu se schématem **10**. Před otevřením původních dat vytvoř zálohu: migrace je transakční, ale v0.16.0 databázi schématu 10 neotevře. [Obnova soustředění po pádu](FOCUS_RECOVERY.md).

## Plánované místní zálohy

Plánované místní zálohy jsou dostupné ve **v0.18.0**. Schéma SQLite zůstává **10**. Ruční záloha a obnova fungují samostatně. [Plánované místní zálohy](SCHEDULED_BACKUPS.md).

[Opravy po revizi hlavní větve](REVIEW_FINDINGS.md).
