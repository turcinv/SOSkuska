# Nastavenie vzhľadu

[English](../APPEARANCE.md) · [Čeština](../cs/APPEARANCE.md) · [Slovenčina](../sk/APPEARANCE.md) · [Русский](../ru/APPEARANCE.md)

**v0.29.0 — značka s mačkou:** Light používa krémové pracovné pole s bielymi kartami; Dark používa charcoalové plochy. Obe varianty zdieľajú levanduľové tlačidlá v tvare pilulky, fialové akcenty a vždy charcoalový bočný panel s levanduľovo zvýraznenou vybranou položkou. Uložené správanie Light/Dark/System zostáva rovnaké. [Interné snímky a odovzdanie](../agents/design/cat-brand/README.md).

**v0.19.0 — redizajn, krok 1:** spoločný vzhľad používa modré akcie/výber, mätový priebeh, teplé svetlé pozadie v Light a párové tmavé plochy. Vedľajšie tlačidlá majú samostatné pozadie pri prejdení kurzorom; lišty Statistics používajú rovnaké pozadie ako Dashboard. Rozloženie, uložený/predvolený režim, navigácia, dáta aj správanie nastavení zostávajú rovnaké. [Interné snímky, skice a odovzdanie](../agents/design/bright-ui-step1/README.md).

Nastavenie vzhľadu vyšlo vo **v0.16.0** po potvrdení testovania základu v0.15.0 a schválení zlúčenia PR #32 používateľom 22. novembra 2026. Ďalšie zmeny vyžadujú vlastnú revíziu a schválenie zlúčenia/vydania.

Otvor **Settings → Appearance (applies on Save)** a vyber Light, Dark alebo System. Uložením sa vzhľad hneď použije a zapamätá pre túto databázu. Samotný výber je koncept; navigácia ho zachová, Reload potvrdzuje jeho nahradenie. Chybný alebo zastaraný zápis zachová súčasný vzhľad aj koncept. Pôvodné databázy začínajú tmavým vzhľadom. Uloženie celého formulára naďalej rešpektuje validáciu a ochrany zmien AI.

Vzhľad je nezávislý od jazyka rozhrania aj odpovedí AI. Mení existujúce widgety bez obnovy obrazoviek: nezahodí koncepty editorov/Tutor, neresetuje čas sústredenia/testu, neprepisuje históriu a nespúšťa sieť. Jazyk rozhrania stále vyžaduje reštart. Iné okná prevezmú nastavenia cez vlastné Save/reštart, nie živou synchronizáciou.

System sleduje natívny vzhľad Windows/macOS a reaguje za behu na zmeny OS. Na Linuxe a ostatných nepodporovaných systémoch zámerne používa Light, aby pripnuté závislosti opakovane nespúšťali detekčné podprocesy vo vlákne Tk. Na Linuxe možno zvoliť Light/Dark priamo. Odozvu System overujú simulované oznámenia OS; ručné natívne/DPI kontroly sú oddelené.

`theme.py` zdieľa párové farby pre plochy, text, ovládanie, ponuky, zástupné texty, zakázané hlavné tlačidlá aj mazanie. `appearance.py` používa verejné API CustomTkinter. Kontroly overujú kontrast viditeľných popisov a pozadia naprieč obrazovkami; nedokladajú úplnú prístupnosť ani ručné platformné overenie.

Schéma **9** pridáva `preferences.appearance_mode` s hodnotami Light/Dark/System a predvolenou Dark. Migrácia zachová obsah, konverzácie, jazyky aj revíziu; pri chybe sa vráti späť. Voľba je súčasťou záloh. Toto vydanie obnovuje samostatné zálohy schémy 9; staršiu dôveryhodnú kópiu možno migrovať otvorením pri štarte a potom znovu zálohovať. Originál zachovaj: v0.15.0 používa schému 8 a dáta schémy 9 neotvorí.

Stav 22. novembra 2026: používateľ potvrdil dokončenie testovania v0.15.0 a schválil PR #32. Tento zoznam teraz cieli na v0.30.0; jednotlivé výsledky čistého počítača/DPI tu nie sú zaznamenané. Nezaškrtnuté body zostávajú neoverené; pri testovaní nového vydania doplň dôkazy pre konkrétne zariadenie. Pre nové kontroly použi `--data .local-data/appearance.sqlite3`. [Ďalšie kroky · 22. novembra 2026](NEXT_STEPS.md).

Kontroly: `tests/test_appearance.py`, `soskuska/check_appearance.py`, zachovanie živého streamu v `check_tutor.py`, ovládanie v štyroch jazykoch a štart Windows balíčka vo všetkých 12 kombináciách jazyka/vzhľadu. GUI štandardne v [kontajneri](CONTAINER_TESTS.md). Bez novej závislosti aplikácie.
