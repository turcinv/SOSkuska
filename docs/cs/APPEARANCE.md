# Nastavení vzhledu

[English](../APPEARANCE.md) · [Čeština](../cs/APPEARANCE.md) · [Slovenčina](../sk/APPEARANCE.md) · [Русский](../ru/APPEARANCE.md)

Funkce je implementovaná ve větvi vzhledu a **není součástí vydané v0.15.0**. PR neslučovat, dokud uživatel nepotvrdí dokončení testování v0.15.0 a výslovně neschválí sloučení. Chyby základního vydání řešit samostatnými PR.

Otevři **Settings → Appearance (applies on Save)** a vyber Light, Dark nebo System. Uložením se vzhled hned použije a zapamatuje pro tuto databázi. Samotný výběr je koncept; navigace ho zachová, Reload potvrzuje jeho nahrazení. Chybný nebo zastaralý zápis zachová současný vzhled i koncept. Původní databáze začínají tmavým vzhledem. Uložení celého formuláře dál respektuje validaci a ochrany změn AI.

Vzhled je nezávislý na jazyku rozhraní i odpovědí AI. Mění existující widgety bez obnovy obrazovek: nezahodí koncepty editorů/Tutor, neresetuje čas soustředění/testu, nepřepisuje historii a nespouští síť. Jazyk rozhraní stále vyžaduje restart. Jiná okna převezmou nastavení přes vlastní Save/restart, nikoli živou synchronizací.

System sleduje nativní vzhled Windows/macOS a reaguje za běhu na změny OS. Na Linuxu a ostatních nepodporovaných systémech záměrně používá Light, aby připnuté závislosti opakovaně nespouštěly detekční podprocesy ve vlákně Tk. Na Linuxu lze zvolit Light/Dark přímo. Odezvu System ověřují simulovaná oznámení OS; ruční nativní/DPI kontroly jsou oddělené.

`theme.py` sdílí párové barvy pro plochy, text, ovládání, nabídky, zástupné texty, zakázaná hlavní tlačítka i mazání. `appearance.py` používá veřejné API CustomTkinter. Kontroly ověřují kontrast viditelných popisků a pozadí napříč obrazovkami; nedokládají úplnou přístupnost ani ruční platformní ověření.

Schéma **9** přidává `preferences.appearance_mode` s hodnotami Light/Dark/System a výchozí Dark. Migrace zachová obsah, konverzace, jazyky i revizi; při chybě se vrátí zpět. Volba je součástí záloh. Tato větev obnovuje samostatné zálohy schématu 9; starší důvěryhodnou kopii lze migrovat otevřením při startu a pak znovu zálohovat. Originál zachovej: v0.15.0 používá schéma 8 a data schématu 9 neotevře.

Při souběžném testování použij novou dočasnou databázi `--data .local-data/appearance.sqlite3` nebo samostatnou kopii. Databázi přejímky v0.15.0 funkcí nemigruj. [Přejímka Windows](WINDOWS_ACCEPTANCE.md) se dál týká vydaného základu.

Kontroly: `tests/test_appearance.py`, `soskuska/check_appearance.py`, zachování živého streamu v `check_tutor.py`, ovládání ve čtyřech jazycích a start Windows balíčku ve všech 12 kombinacích jazyka/vzhledu. GUI standardně v [kontejneru](CONTAINER_TESTS.md). Bez nové závislosti aplikace.
