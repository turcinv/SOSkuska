# Prenosná aplikácia pre Windows

[English](../WINDOWS_PORTABLE.md) · [Čeština](../cs/WINDOWS_PORTABLE.md) · [Slovenčina](../sk/WINDOWS_PORTABLE.md) · [Русский](../ru/WINDOWS_PORTABLE.md)

v0.32.0 obsahuje **nepodpísaný prenosný ZIP pre Windows x64**, nie inštalátor. Používateľ nepotrebuje Python ani práva správcu.

1. Stiahni `SOSkuska-windows-x64.zip` a súbor `.sha256` z [v0.32.0](https://github.com/turcinv/SOSkuska/releases/tag/v0.32.0). Súkromný repozitár vyžaduje prihlásenie na GitHub a prístup. Vyber pomenovaný Windows ZIP, nie archív zdrojového kódu GitHubu.
2. Rozbaľ celý ZIP do zapisovateľného priečinka. Zachovaj celý priečinok `SOSkuska` vrátane `_internal` a `SOSkuska-worker.exe`.
3. Spusti `SOSkuska.exe`. Nespúšťaj ho vo vnútri ZIPu, nepresúvaj samotné EXE a nespúšťaj pomocníka priamo. Dáta zostávajú nezávisle v `%LOCALAPPDATA%\SOSkuska\dashboard.sqlite3`; platí aj pôvodná náhradná cesta ExamPrep.
4. Nepodpísaný súbor môže blokovať zabezpečenie Windows alebo firemné pravidlá. Over pôvod/commit a SHA-256, nevypínaj ochranu. Pri obmedzení pravidlami sa obráť na správcu.

Na oddelenú kontrolu spusti v PowerShelli z rozbaleného priečinka `./SOSkuska.exe --data "$env:TEMP/SOSkuska-check.sqlite3"`. Zvoľ novú nepoužitú cestu. Bežné štúdium je offline; Ollama je voliteľná a samostatná. Odstránenie priečinka aplikácie neodstráni dátový priečinok. Pred aktualizáciou zálohuj; staršia aplikácia odmieta novšiu schému databázy.

Artefakt obsahuje SHA-256. Pred rozbalením vnútorného ZIPu ho porovnaj s `Get-FileHash .\SOSkuska-windows-x64.zip -Algorithm SHA256`. Zhoda overuje neporušenosť, nie totožnosť vydavateľa. Archív obsahuje aplikáciu, konzolového pomocníka, prostriedky Python/Tk/CustomTkinter, štyri jazykové katalógy a tieto návody. Neobsahuje používateľskú databázu ani virtuálne prostredie.

## Zostavenie a kontrola na Windows

Použi 64-bitový Python 3.12 na Windows z koreňa repozitára. PyInstaller je samostatne pripnutá závislosť iba na zostavenie. Windows aplikáciu treba zostaviť na Windows:

```powershell
py -3.12 -m venv .venv-build
.\.venv-build\Scripts\python.exe -m pip install -r soskuska/requirements.txt -r packaging/requirements-build.txt
.\.venv-build\Scripts\python.exe tools/build_windows.py
.\.venv-build\Scripts\python.exe tools/check_windows_bundle.py dist/SOSkuska-windows-x64.zip --report dist/windows-acceptance.json
```

Výstup je `dist/SOSkuska/`, ZIP, `.sha256` a protokol kontroly. Špecifikácia vytvára GUI bez konzoly a konzolového pomocníka; skryté podprocesy zachovajú JSON komunikáciu cez dočasný súbor. Zo zdrojov sa naďalej spúšťajú Python skripty. Bez inštalátora, zápisu inštalácie do registra, podpisu a automatických aktualizácií.

CI rozbalí skutočný ZIP do dočasnej cesty s medzerami a Unicode a spúšťa ho z iného pracovného priečinka bez Pythonu v PATH. Kontroluje viditeľné hlavné okno a bežné zatvorenie, prázdnu databázu, štart všetkých štyroch jazykov, oba CSV importy, zálohu/validáciu/obnovu a zachované záznamy. Automatické kontroly na hostovanom Windows **nenahrádzajú** [ručnú preberaciu kontrolu](WINDOWS_ACCEPTANCE.md) na čistom Windows. Balenie macOS/Linux a Windows ARM64 nie je súčasťou.

Postup vychádza z [dokumentácie PyInstaller](https://pyinstaller.org/en/stable/spec-files.html) a [návodu CustomTkinter](https://customtkinter.tomschimansky.com/documentation/packaging/).
