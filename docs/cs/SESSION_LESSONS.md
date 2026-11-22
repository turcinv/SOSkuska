# Poznatky ze sezení a předání projektu

[English](../SESSION_LESSONS.md) · [Čeština](SESSION_LESSONS.md) · [Slovenčina](../sk/SESSION_LESSONS.md) · [Русский](../ru/SESSION_LESSONS.md)

Zapsáno **20. listopadu 2026**, po vydání **v0.11.0 — Flashcard CSV import**. Jde o datované předání, nikoli živý stav. Před novým tvrzením ověř Git, vydání, kód a CI.

## Projekt a pracovní preference

SOSkúška je nativní semestrální projekt v Pythonu/CustomTkinter/SQLite. Dodávej zvládnutelné týdenní funkce a ponech čas na semestrální dokumentaci. Aplikace funguje offline; Ollama je volitelná. Uživatel zvolil místní vývoj kvůli placenému generování návrhů. HTML v `soskuska-local/` je vizuální reference.

Konverzace může střídat češtinu, slovenštinu, angličtinu a ruštinu; odpovídej v posledním jazyce. UI zůstává anglické. Hlavní dokumentace je anglicky a překlady jsou samostatně. Interní pokyny pro agenty zůstávají anglicky.

## Postup vývoje a vydání

1. Nová větev z aktuálního main; implementuj požadovaný krok plánu. Nikdy necommituj ani nepushuj přímo do main.
2. Používej dočasná data, proveď odpovídající kontroly a pro implementaci funkcí vyžádej nezávislou kontrolu **Sol se středním úsilím**. Nálezy oprav ve stejné větvi a opravy nech znovu zkontrolovat.
3. Otevři PR, popiš skutečné ověření a zkontroluj CI. Chyby oprav bez oslabování kontrol. Zelené CI samo nepovoluje sloučení.
4. Slučuj až po souhlasu uživatele. Požadavek sloučit a vydat zahrnuje potřebné PR pro označení verze a publikaci. Před označením přesného sloučeného commitu sjednoť patičku, čtyři README, nadpisy changelogů a stav architektury.
5. Ověř vydání a čistý main synchronizovaný s GitHubem. Další funkce, sloučení, vydání či úklid větví nejsou automaticky povolené předchozí prací.

## Poznatky k zachování

- **Odděl zápis od opakování čtení.** Po úspěšném uložení zneplatni dávku před načtením součtů. Chyba obnovy nesmí opakovat import. Neznámý výsledek procesu již mohl být uložen; nejprve ověř data.
- **Náhled musí být stabilní.** Uchovej soukromou dávku; změny CSV vyžadují nový výběr. Cíl/název a duplicity ověř znovu pod zámkem zápisu a ulož vše jednou transakcí.
- **Pro CSV/zálohy používej procesy.** Uvolňování objektů ve vlákně Pythonu dříve zrušilo objekty Tk a shodilo macOS aplikaci. Tk patří do hlavního vlákna. Výstup procesu směruj do dočasného souboru; nečtené roury se na Windows mohou zablokovat.
- **Náhled pouze pro čtení.** Existující databázi neotvírej s vytvářením či migrací. Použij již zobrazený cíl; synchronní dotaz při výběru souboru může pod databázovým zámkem zablokovat Tk.
- **Zachovej rozepsaný text.** Překreslení může ztratit nepotvrzené hledání či formulář. Uchovej jej odděleně od použitého filtru a ověř navigaci i obnovu po uložení.
- **Kontroluj také drobnosti UI.** Čekací zpráva patří aktivnímu importu. Test duplicity za limitem seznamu musí skutečně vytvořit dost záznamů.
- **Přesně popisuj platformní ověření.** macOS a Linux/Xvfb neověřují ruční UI na Windows ani fyzický trackpad. Na připraveném Macu používej `.venv-macos`; Apple Tk 8.5 v `.venv-desktop` vykreslil prázdné okno.

## Ověřený stav při předání

- Vydání **v0.11.0**, commit `b5acbdcc47310b1fab0ba9fb4b24dbac0db041ce`; implementace **#19**, sjednocení verze **#20**.
- **202 jednotkových testů** a **12 nativních GUI skriptů** prošlo lokálně na macOS. Čtyři CI úlohy funkce prošly: testy Linux/Windows/macOS a GUI Ubuntu/Xvfb. Označení vydání mělo cílenou kontrolu verzí, syntaxe a dokumentace.
- Schéma **6**. Import otázek i kartiček z CSV existuje. Kartičky: UTF-8/BOM, čárky, právě `front,back`, nejvýše **2 MiB / 500 záznamů**, odmítnutí přesných duplicit a atomické uložení do existujícího balíčku. Nové kartičky jsou ihned splatné; původní termíny a historie se nemění.

## Úsporný kontext pro další sezení

Kořenový `AGENTS.md` slouží jako stručný rozcestník. Před úpravou oblasti načti požadované soubory `@docs/agents/...`; ostatní pravidla načítej až podle potřeby. Jde o výslovné pokyny ke čtení souborů, nikoli příslib automatického vložení. Oficiální [návod Codex k AGENTS.md](https://developers.openai.com/codex/guides/agents-md) popisuje hierarchické načítání pokynů; projekt proto výslovně požaduje otevření odkazovaných souborů.

Trvalá pravidla patří do příslušného souboru pokynů, nové datované ověření sem a historie vydání do changelogu. Změny chování promítni do pravidel a všech jazyků uživatelské dokumentace.

## Další kroky · 22. listopadu 2026

Stav 22. listopadu 2026: uživatel potvrdil dokončení testování v0.15.0 a schválil PR #32. Tento seznam nyní cílí na v0.18.0; jednotlivé výsledky čistého počítače/DPI zde nejsou zaznamenané. Nezaškrtnuté body zůstávají neověřené; při testování nového vydání doplň důkazy pro konkrétní zařízení. [Další kroky · 22. listopadu 2026](NEXT_STEPS.md).
