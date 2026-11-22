# Nastavení vzhledu

[English](../APPEARANCE.md) · [Čeština](../cs/APPEARANCE.md) · [Slovenčina](../sk/APPEARANCE.md) · [Русский](../ru/APPEARANCE.md)

Nastavení vzhledu vyšlo ve **v0.16.0** po potvrzení testování základu v0.15.0 a schválení sloučení PR #32 uživatelem 22. listopadu 2026. Další změny vyžadují vlastní revizi a schválení sloučení/vydání.

Otevři **Settings → Appearance (applies on Save)** a vyber Light, Dark nebo System. Uložením se vzhled hned použije a zapamatuje pro tuto databázi. Samotný výběr je koncept; navigace ho zachová, Reload potvrzuje jeho nahrazení. Chybný nebo zastaralý zápis zachová současný vzhled i koncept. Původní databáze začínají tmavým vzhledem. Uložení celého formuláře dál respektuje validaci a ochrany změn AI.

Vzhled je nezávislý na jazyku rozhraní i odpovědí AI. Mění existující widgety bez obnovy obrazovek: nezahodí koncepty editorů/Tutor, neresetuje čas soustředění/testu, nepřepisuje historii a nespouští síť. Jazyk rozhraní stále vyžaduje restart. Jiná okna převezmou nastavení přes vlastní Save/restart, nikoli živou synchronizací.

System sleduje nativní vzhled Windows/macOS a reaguje za běhu na změny OS. Na Linuxu a ostatních nepodporovaných systémech záměrně používá Light, aby připnuté závislosti opakovaně nespouštěly detekční podprocesy ve vlákně Tk. Na Linuxu lze zvolit Light/Dark přímo. Odezvu System ověřují simulovaná oznámení OS; ruční nativní/DPI kontroly jsou oddělené.

`theme.py` sdílí párové barvy pro plochy, text, ovládání, nabídky, zástupné texty, zakázaná hlavní tlačítka i mazání. `appearance.py` používá veřejné API CustomTkinter. Kontroly ověřují kontrast viditelných popisků a pozadí napříč obrazovkami; nedokládají úplnou přístupnost ani ruční platformní ověření.

Schéma **9** přidává `preferences.appearance_mode` s hodnotami Light/Dark/System a výchozí Dark. Migrace zachová obsah, konverzace, jazyky i revizi; při chybě se vrátí zpět. Volba je součástí záloh. Toto vydání obnovuje samostatné zálohy schématu 9; starší důvěryhodnou kopii lze migrovat otevřením při startu a pak znovu zálohovat. Originál zachovej: v0.15.0 používá schéma 8 a data schématu 9 neotevře.

Stav 22. listopadu 2026: uživatel potvrdil dokončení testování v0.15.0 a schválil PR #32. Tento seznam nyní cílí na v0.17.0; jednotlivé výsledky čistého počítače/DPI zde nejsou zaznamenané. Nezaškrtnuté body zůstávají neověřené; při testování nového vydání doplň důkazy pro konkrétní zařízení. Pro nové kontroly použij `--data .local-data/appearance.sqlite3`. [Další kroky · 22. listopadu 2026](NEXT_STEPS.md).

Kontroly: `tests/test_appearance.py`, `soskuska/check_appearance.py`, zachování živého streamu v `check_tutor.py`, ovládání ve čtyřech jazycích a start Windows balíčku ve všech 12 kombinacích jazyka/vzhledu. GUI standardně v [kontejneru](CONTAINER_TESTS.md). Bez nové závislosti aplikace.
