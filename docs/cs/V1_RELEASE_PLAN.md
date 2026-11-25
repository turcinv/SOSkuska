# Přejímací kroky před v1.0.0

[English](../V1_RELEASE_PLAN.md) · [Čeština](V1_RELEASE_PLAN.md) · [Slovenčina](../sk/V1_RELEASE_PLAN.md) · [Русский](../ru/V1_RELEASE_PLAN.md)

Rozhodnutí z **23. listopadu 2026**. Před přípravou v1.0.0 ověřit vydanou **v0.18.1**, schéma **10**. Základní implementace pro současný semestrální rozsah je hotová; ruční Windows kontroly a skutečný model dosud nemají důkazy. Tento plán nepotvrzuje úspěch ani neschvaluje sloučení/vydání. Během přejímky pozastavit nové funkce. Práce a prezentace mohou pokračovat samostatně a neblokují vydání aplikace.

## 1 Získat Windows verzi

Na Windows x64 bez Pythonu stáhnout `SOSkuska-windows-x64.zip` a `.sha256` z [v0.18.1](https://github.com/turcinv/SOSkuska/releases/tag/v0.18.1); je nutný přístup do soukromého repozitáře. Ověřit součet a celý ZIP rozbalit do zapisovatelné složky. Ponechat pohromadě `SOSkuska.exe`, `_internal` a `SOSkuska-worker.exe`. Použít [přenosnou verzi](WINDOWS_PORTABLE.md); blokování bezpečnostní politikou zaznamenat, ochranu nevypínat.

## 2 Použít dočasná data

Ve složce rozbalené aplikace otevřít PowerShell a spustit:

```powershell
$acceptanceDb = Join-Path $env:TEMP ("SOSkuska-acceptance-" + [guid]::NewGuid().ToString() + ".sqlite3")
.\SOSkuska.exe --data "$acceptanceDb"
```

Zapsat hodnotu `$acceptanceDb`. Při každém opětovném otevření spustit pouze druhý řádek se **stejnou cestou**, negenerovat nový GUID. Po zavření PowerShellu do proměnné vrátit zapsanou cestu. Zálohu/obnovu testovat jen s touto databází a před obnovou zavřít ostatní instance. Běžná studijní data neměnit.

## 3 Dokončit Windows přejímku

Projít celý [Windows seznam](WINDOWS_ACCEPTANCE.md), samotný start nestačí. Ověřit prázdný začátek, Unicode předměty/témata/otázky, CSV náhled/import, testy a uložené výsledky, hodnocení/historii kartiček a pauzu/dokončení soustředění. Po zavření znovu otevřít stejnou databázi a ověřit uložení. Pro obnovu soustředění přerušit pouze dočasnou testovací instanci po kontrolním bodu; ověřit pozastavenou obnovu bez započítání vypnuté doby i zahození. Ověřit zálohu/obnovu a bezpečnostní kopii, zapnuté denní zálohy za běhu, jazyky/vzhled, vnořené posouvání, rozměry 1440×900/1024×700 a podporovaná měřítka 100/125/150 %. Nepodporované kombinace výslovně zapsat.

## 4 Ověřit skutečný model Ollama

Ollama zůstává pro běžné studium volitelná, Tutor ale před dokončením přejímky potřebuje skutečný test. Zapsat verze serveru/modelu, identifikátor modelu, hardware, datum a adresu bez přihlašovacích údajů. Výslovně Connect a Send; ověřit streamování, Stop, opětovné připojení a otevření uloženého chatu. Vypnout server a ověřit offline studium. Zapsat omezení kvality/rychlosti; falešný server CI není důkaz skutečného modelu. Neproveditelné kontroly ponechat NOT RUN s důvodem, přejímku neoznačovat hotovou.

## 5 Zapsat výsledky

Záznam kopírovat pro každé zařízení/běh a připojit důkazy ke každému bodu. Použít PASS / FAIL / NOT RUN; prázdné pole není úspěch. Snímky nesmějí obsahovat osobní studijní obsah ani přihlašovací údaje.

| Pole | Hodnota |
| --- | --- |
| Datum a testující | [DATUM / TESTUJÍCÍ] |
| Edice/build Windows a architektura CPU | [WINDOWS / ARCHITEKTURA] |
| Hardware, rozlišení a měřítko | [HARDWARE / ROZLIŠENÍ / MĚŘÍTKO] |
| Verze aplikace, commit artefaktu a SHA-256 ZIPu | [VERZE / COMMIT / SHA-256] |
| Cesta dočasné databáze | [CESTA] |
| Bod, očekávané a skutečné chování | [BOD / OČEKÁVÁNÍ / SKUTEČNOST] |
| Výsledek a odkaz na snímek/log | NOT RUN — [DŮKAZ / DŮVOD] |
| Verze serveru/modelu Ollama a adresa | [SERVER / MODEL / ADRESA] |
| Reprodukce chyby a opravné PR | [KROKY / PR NEBO ŽÁDNÉ] |

## 6 Vyřešit nálezy

Chyby opravit v nové větvi a PR, uchovat reprodukci, zajistit nezávislou revizi Sol na medium a příslušné kontejnerové kontroly i CI. Chybné případy zopakovat na opraveném Windows artefaktu; starý úspěch nepotvrzuje změněné chování. Nevyřešené/neověřené body ponechat viditelné. Sloučit jen s výslovným souhlasem uživatele.

## 7 Připravit v1.0.0

Po úspěšné přejímce a opravách sladit verzi/patičku, čtyři README odkazy, stav architektury a changelog přes PR. Zkontrolovat CI a získat souhlas ke sloučení/vydání. Označit přesný sloučený commit, získat jeho ověřený Windows ZIP/součet/zprávu z CI main a vydat poznámky s funkcemi, změnami a omezeními. Ověřit tag, součet a stažení. Nepřejmenovat binárku v0.18.1 na v1.0.0. Nejde o příslib instalátoru, EXE pro macOS, automatických aktualizací ani bezchybnosti.
