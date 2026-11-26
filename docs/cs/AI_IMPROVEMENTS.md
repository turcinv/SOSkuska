# Zlepšení AI: vysvětlení otázky

[English](../AI_IMPROVEMENTS.md) · [Čeština](AI_IMPROVEMENTS.md) · [Slovenčina](../sk/AI_IMPROVEMENTS.md) · [Русский](../ru/AI_IMPROVEMENTS.md)

Rozhodnutí o plánu · 26. listopadu 2026. Základ: v0.24.0, schéma 10. Jde o budoucí práci; funkce není implementovaná a toto plánovací PR neschvaluje implementaci, sloučení ani vydání.

## Cíl

Propojit dokončené výsledky Practice s AI Tutorem přes **Vysvětlit tuto otázku**. Student si prohlédne jednu uloženou otázku, výslovně připraví koncept a použije dosavadní Připojit a Odeslat. Běžné studium zůstává offline, Ollama je volitelná.

## Implementační kroky

### 1. Vymezit první funkci

Podporovat jednu otázku z dokončeného výsledku včetně otevření z historie. Nepřidávat akci do běžícího testu, přípravy ani banky otázek. AI vysvětluje, nemění správnou odpověď, skóre, obsah ani statistiky. Uložený klíč není zárukou věcné správnosti. Studijní režimy, generování z poznámek, přílohy a formátování patří do dalších PR.

### 2. Sestavit neměnný omezený prompt

Použít snímek pokusu podle `(attempt_id, position)`, nikoli `question_id` nebo dnešní banku otázek. Znovu ověřit existenci a dokončení. Kopírovat otázku, možnosti A–D, vybranou odpověď nebo Nezodpovězeno, správnou odpověď a uložené vysvětlení. Přidat stručnou žádost o odůvodnění a vysvětlení rozdílu, případně správného postupu u nezodpovězené otázky. Chyba čtení či chybějící záznam nabídne opakování bez ztráty obrazovky. Úprava/smazání zdroje nesmí obsah změnit.

### 3. Zachovat limit vstupu

Tutor dovoluje 4000 znaků; platná otázka s možnostmi a vysvětlením může být delší. Počítat celý sestavený prompt včetně popisků a instrukcí. Při překročení nic nepřipravit ani neposlat, ukázat délku a limit a ponechat výsledek použitelný. Uvést, že zkratka pro celý kontext tuto položku zatím nezvládne. Nic potichu nezkracovat a nezvyšovat dosavadní limity. Přílohy pro dlouhý kontext odložit; otestovat přesnou mez i překročení.

### 4. Přidat místní náhled výsledku

U každé dokončené otázky nabídnout akci dostupnou i u dlouhého textu a v malém okně. Ukázat přesný prompt a sdílený obsah, Připravit v Tutoru a Zrušit. Náhled neprovádí HTTP, neukládá konverzaci, nemění výsledek a nepřipojuje se. Callback zachová původní identitu pokusu/pozice a odmítne zastaralé či skryté akce; před předáním způsobilost znovu ověřit.

### 5. Předat bez ztráty konverzace

Připravit jen v nečinném Tutoru bez neuložené odpovědi a čekající obnovy/potvrzení, v čistém Novém chatu s prázdným promptem. Existující chat, koncept a úlohu zachovat; vysvětlit, jak práci dokončit nebo výslovně použít dosavadní potvrzený Nový chat a potom akci opakovat. Automaticky nic nemazat, neotvírat jinou historii, neměnit server/model, nezastavovat úlohu ani neplánovat odložené odeslání. Úspěšný koncept zobrazit v Tutoru a umožnit úpravu. Opakovaná akce nesmí duplikovat text ani nahradit změněný koncept.

### 6. Použít dosavadní Připojit/Odeslat

Server, model a jazyk odpovědi zůstávají viditelné. Připojení je výslovné; generování spustí jen Odeslat. Prompt uložit běžnou transakcí čekajícího dotazu před HTTP, takže historie obsahuje dodaný snímek jako text otázky. Nová tabulka kontextu ani migrace se neplánuje. Zachovat Stop, částečné odpovědi, opakování zápisu, obnovu, meze kontextu a vlastnictví serveru/modelu. Nerozšiřovat automatické přílohy ani síťového klienta. Pokud kód vyžaduje schéma, nejprve upravit plán.

### 7. Přeložit a ověřit ovládání

Doplnit angličtinu, češtinu, slovenštinu a ruštinu; uživatelský text neměnit. Jazyk odpovědi je nezávislý na rozhraní. U Automaticky požádat model o jazyk dodané otázky a vyhodnotit smíšené jazyky; výslovná volba zůstává uživatelským řízením, rozpoznání modelu není zaručené. Ověřit klávesnici, čitelnost, chyby a dosah akcí při 1024×700/1440×900, Light/Dark/System a počátečním měřítku 100/150 %. Skrytá aktualizace nesmí změnit posun ani koncept jiné stránky.

### 8. Otestovat chování a chyby

Čisté testy: sestavení snímku, správná/chybná/žádná odpověď, meze, neplatná identita a stav. GUI: historie po úpravě/smazání zdroje, Zrušit, žádná síť před Připojit/Odeslat, odmítnutí zaneprázdněného či rozepsaného Tutora, idempotentní předání, selhání prvního zápisu, stream/Stop a opakování uložení bez duplicit. FakeOllama přes loopback ověří požadavek a persistenci, nikoli kvalitu odpovědi. Použít dočasná data a kontejnerové GUI.

### 9. Dodat jedno soustředěné PR

Z aktuální main založit např. `feature/ai-question-explanation`. Nejprve čistý sestavovač, potom náhled, chráněné předání, integrace a dokumentace; závislé commity držet v jednom PR. Provést vhodné jednotkové/kontejnerové kontroly a CI, nezávislou revizi Sol na medium a opravy i opětovnou revizi na stejné větvi. Aktualizovat Tutor, historii testů, architekturu a všechny čtyři jazykové verze. Verzi neměnit do schválení vydání.

### 10. Vyhodnotit a rozhodnout o pokračování

Před ukázkou vyzkoušet skutečný model na dočasných správných, chybných, nezodpovězených, nejednoznačných a vícejazyčných otázkách. Zapsat verzi Ollamy/modelu, hardware, jazyk, odezvu/Stop a užitečnost vysvětlení. Oddělit to od automatických testů. Finální přejímka a prezentace stále zbývají. Sloučení a vydání potřebují vlastní rozhodnutí; budoucí funkční vydání obvykle použije další volnou vedlejší verzi 0.x, kterou tento plán nerezervuje.

## Pravděpodobná místa změn

Při implementaci ověřit zejména `soskuska/practice_page.py` (`render_result`), nový čistý modul např. `soskuska/question_explanation.py`, předání v `soskuska/app.py`, přípravu konceptu v `soskuska/tutor_page.py`, dosavadní čtecí API `soskuska/storage.py`, případnou omezenou jazykovou instrukci v `soskuska/tutor.py`, čtyři katalogy `soskuska/i18n/`, testy a `tools/run_checks.py`. Nepřidávat nesouvisející refaktoring, nastavení ani migrace.

## Podmínky dokončení

Hotovo znamená: místní náhled jednoho dokončeného snímku, zachovaná existující práce, výslovné Odeslat vytvoří běžný uložený tah, chyby/Stop lze obnovit, skóre a historie se nemění, revize/testy projdou a dokumentace uvádí omezení. Odmítnutí příliš dlouhé otázky je výslovné omezení první verze, nikoli tiché krácení.

## Další zlepšení AI

Po samostatném určení priorit: (A) jednodušší vysvětlení, nápověda a zkoušení; (B) nativní seznamy, nadpisy a bloky kódu; (C) generování otázek/kartiček z vložených poznámek s validací, upravitelným náhledem a výslovným atomickým uložením. Generování potřebuje vlastní plán chybných výstupů, duplicit, opakování a kontroly obsahu. RAG, automatický kontext celé databáze a cloudový záložní server sem nepatří.
