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

Stav 22. listopadu 2026: uživatel potvrdil dokončení testování v0.15.0 a schválil PR #32. Tento seznam nyní cílí na v0.18.1; jednotlivé výsledky čistého počítače/DPI zde nejsou zaznamenané. Nezaškrtnuté body zůstávají neověřené; při testování nového vydání doplň důkazy pro konkrétní zařízení. [Další kroky · 22. listopadu 2026](NEXT_STEPS.md).

## Revize Dashboardu · 25. listopadu 2026

Dashboard, krok 2, sdružuje studijní akce, pod nimi předměty/hledání, kompaktní souhrn a výběr sidebaru. Rozměry plochy a zalamování převádět z nativních pixelů na logické CTk jednotky uvnitř adaptéru posouvání; meze ověřovat proti skutečné ploše. Simulované DPI nastavit před konstrukcí widgetů v nových procesech: živá změna CTk 5.2.2 může znovu zobrazit skryté stránky. Revize bez blokujících nálezů; 308 unit testů (dva přeskočené), všech 18 GUI skriptů v kontejneru včetně čtyř jazyků a obnovy/opakování při počátečním měřítku 100/150 %. Nativní/živé DPI ověření je oddělené.

## Revize redesignu testů · 25. listopadu 2026

CTkFrame.bind předává Configure na canvas: lokální změnu velikosti neodmítat porovnáním event.widget s obalem. Před zalamováním převést pixely na logické jednotky. Výběr odpovědi kreslit z uloženého snímku, po chybě obnovit; řádek/text/radio chránit aktuální stránkou i viditelností testu. Kontrast radia ověřit proti vybranému pozadí. Testovat skutečné kreslicí/textové cíle událostí, nejen přímá volání. Postup počítá uložené odpovědi, nikoli správnost.

## 2026-11-25 · Flashcard retry

Odlišuj chybu zápisu hodnocení od chyby následného čtení. Při chybě zápisu zachovej odhalenou odpověď; po úspěšném zápisu vypni stará hodnocení a opakuj pouze čtení další kartičky. Zprávu o opakování zobraz u hodnocení dlouhé odpovědi a použij přeložené názvy akcí.

## 2026-11-25 · Responzivní přehledy a Tutor

Popisky ve stejně širokých sloupcích zalamuj podle stabilní šířky společného kontejneru. Šířka jednotlivých zaokrouhlených karet může při změně velikosti způsobit smyčku o jeden pixel. Rozložení měň jen při přepnutí počtu sloupců a varování zobraz u potvrzovacích tlačítek.

## 2026-11-26 · Kočičí značka, AI generování a hodnocení se skutečným modelem (v0.29.0–v0.30.1)

- **Paleta značky a kontrast.** Značková levandulová `#9884D6` dává bílému textu jen asi 3,2:1. Tlačítka používají tmavší `#6E5ABF`, značková barva zůstává pro obrysy. Každý dekorativní obrázkový štítek potřebuje čitelné `text_color`, protože živý audit kontroluje všechny namapované štítky.
- **Kompaktní rozložení má málo svislé rezervy.** Kontrola viditelnosti Finish v 1024 × 700 selhala po přidání obrázku banneru. Dekorativní scény se zobrazují jen v širokém rozložení a obrázek postranního panelu se umístí do mřížky, jen když se jeho vážený řádek vejde celý.
- **Náklady na start jsou testované omezení.** Start v čerstvém procesu má v CI rozpočet CPU a času (viz WORKFLOW). Dva další panely vytvářené při startu tento limit překročily. Volitelné panely, například panely AI generování, vytvářej až při prvním použití.
- **Test se skutečným modelem odhalí, co fixtury nezachytí.** Model s 4 miliardami parametrů označil špatné písmeno odpovědi u 3 z 22 otázek a řídil se pokyny vloženými do poznámek. Nikdy nenech model vybírat písmeno odpovědi. Poznámky ohraň jako data a úkol zopakuj až za nimi. Návrhy se slabou oporou zobraz nezaškrtnuté, neodmítej je. Po každé změně promptu nebo schématu znovu spusť `tools/evaluate_ai.py`.
- **Běhy v kontejneru potřebují `--init`.** Bez něj se `xvfb-run` zasekne dřív, než kontrola začne. Spuštění jednoho skriptu ohraničuj pomocí `timeout`.
- **Souběžná volání nástrojů.** Volání v jednom kroku běží v nezaručeném pořadí, proto nikdy neprováděj sestavení a úpravu v jednom kroku a nespoléhej na výsledek. Po provedení úpravy kontrolu zopakuj.

## 2026-11-27 · Vrstva dotazů MCP, fáze 1

- **Bezokenní kód nesmí záviset na aktuální složce.** Prázdná nebo relativní `LOCALAPPDATA`/`XDG_DATA_HOME` dříve umístila databázi tam, kde proces zrovna začal. Hostitelé MCP spouštějí servery odkudkoli, proto `user_database_path()` takové hodnoty považuje za nenastavené.
- **Klíče odpovědí se týkají i hledání.** Skrýt `correct_option` a vysvětlení nestačí, pokud hledání prohledává text vysvětlení; shoda by napověděla odpověď. Vysvětlení nechte mimo hledaný text a ponechte negativní test.
- **Nevnořujte čtecí transakce.** `practice_history_page` a `statistics_report` otevírají vlastní `BEGIN`; volejte je mimo `_snapshot` a zdokumentujte, proč navazující čtení stále souhlasí.
- **Startovní limity v hostovaném CI jsou pod zátěží nestabilní.** Sedmisekundová sonda čerstvého procesu selhala v PR i u commitu na `main` jen s dokumentací a po opakování prošla. Hlaste ji jako nestabilní s důkazy; netvrďte, že ji způsobilo PR, a nezvyšujte limit kvůli zelenému výsledku.
- **Výstup recenzenta držte krátký.** Dlouhá recenze subagenta byla useknuta po prvním zjištění; žádejte omezenou závěrečnou zprávu a před uzavřením recenze přečtěte celý výsledek.
- **Rozpočet pro start, ne pro celou sondu.** Nestabilní limit měřil start i všechny funkční kroky (asi 3,7 s v kontejneru, přes 7 s na zatížených strojích). `check_studio_layout.py` nyní kontroluje jen start: čas CPU (asi 0,7 s, stabilní i při čtvrtině CPU) proti 2 s a reálný čas proti 6 s kvůli blokujícímu čekání. Mutace s 1,5 s CPU navíc i s 5,5 s spánkem ji shodí. Okamžité vytvoření obou panelů AI generování stojí jen asi 0,05 s CPU, takže dřívější překročení kvůli „dvěma panelům“ nejspíš způsobila také zátěž strojů.
