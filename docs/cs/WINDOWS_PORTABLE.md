# Přenosná aplikace pro Windows

[English](../WINDOWS_PORTABLE.md) · [Čeština](../cs/WINDOWS_PORTABLE.md) · [Slovenčina](../sk/WINDOWS_PORTABLE.md) · [Русский](../ru/WINDOWS_PORTABLE.md)

Větev pro balení vytváří **nepodepsaný přenosný ZIP pro Windows x64**, nikoli instalátor. Uživatel nepotřebuje Python ani práva správce. Vydaná verze v0.14.0 zůstává zdrojovým vydáním; tato změna zatím není vydaná.

1. V Actions → CI otevři běh přesného PR/commitu. Ověř úspěch **Windows portable build and acceptance** a stáhni artefakt `SOSkuska-windows-x64-<commit>`. Je nutné přihlášení na GitHub a přístup k repozitáři; artefakty platí 14 dní.
2. Rozbal artefakt a potom celý `SOSkuska-windows-x64.zip` do zapisovatelné složky. Zachovej celou složku `SOSkuska` včetně `_internal` a `SOSkuska-worker.exe`.
3. Spusť `SOSkuska.exe`. Nespouštěj jej uvnitř ZIPu, nepřesouvej samotné EXE a nespouštěj pomocný program přímo. Data zůstávají nezávisle v `%LOCALAPPDATA%\SOSkuska\dashboard.sqlite3`; platí i původní náhradní cesta ExamPrep.
4. Nepodepsaný soubor může blokovat zabezpečení Windows nebo firemní pravidla. Ověř původ/commit a SHA-256, nevypínej ochranu. Při omezení pravidly se obrať na správce.

Pro oddělenou kontrolu spusť v PowerShellu z rozbalené složky `./SOSkuska.exe --data "$env:TEMP/SOSkuska-check.sqlite3"`. Zvol novou nepoužitou cestu. Běžné studium je offline; Ollama je volitelná a samostatná. Odstranění složky aplikace neodstraní datovou složku. Před aktualizací zálohuj; starší aplikace odmítá novější schéma databáze.

Součástí artefaktu je SHA-256. Před rozbalením vnitřního ZIPu jej porovnej s `Get-FileHash .\SOSkuska-windows-x64.zip -Algorithm SHA256`. Shoda ověřuje neporušenost, nikoli totožnost vydavatele. Archiv obsahuje aplikaci, konzolového pomocníka, prostředky Python/Tk/CustomTkinter, čtyři jazykové katalogy a tyto návody. Neobsahuje uživatelskou databázi ani virtuální prostředí.

## Sestavení a kontrola na Windows

Použij 64bitový Python 3.12 na Windows z kořene repozitáře. PyInstaller je samostatně připnutá závislost pouze pro sestavení. Windows aplikaci je nutné sestavit na Windows:

```powershell
py -3.12 -m venv .venv-build
.\.venv-build\Scripts\python.exe -m pip install -r soskuska/requirements.txt -r packaging/requirements-build.txt
.\.venv-build\Scripts\python.exe tools/build_windows.py
.\.venv-build\Scripts\python.exe tools/check_windows_bundle.py dist/SOSkuska-windows-x64.zip --report dist/windows-acceptance.json
```

Výstup je `dist/SOSkuska/`, ZIP, `.sha256` a protokol kontroly. Specifikace vytváří GUI bez konzole a konzolového pomocníka; skryté podprocesy zachovají JSON komunikaci přes dočasný soubor. Ze zdrojů se dál spouštějí Python skripty. Bez instalátoru, zápisu instalace do registru, podpisu a automatických aktualizací.

CI rozbalí skutečný ZIP do dočasné cesty s mezerami a Unicode a spouští jej z jiné pracovní složky bez Pythonu v PATH. Kontroluje viditelné hlavní okno a běžné zavření, prázdnou databázi, start všech čtyř jazyků, oba CSV importy, zálohu/validaci/obnovu a zachované záznamy. Automatické kontroly na hostovaném Windows **nenahrazují** [ruční přejímku](WINDOWS_ACCEPTANCE.md) na čistém Windows. Balení macOS/Linux a Windows ARM64 není součástí.

Postup vychází z [dokumentace PyInstaller](https://pyinstaller.org/en/stable/spec-files.html) a [návodu CustomTkinter](https://customtkinter.tomschimansky.com/documentation/packaging/).
