# Přejímací kontrola Windows

[English](../WINDOWS_ACCEPTANCE.md) · [Čeština](../cs/WINDOWS_ACCEPTANCE.md) · [Slovenčina](../sk/WINDOWS_ACCEPTANCE.md) · [Русский](../ru/WINDOWS_ACCEPTANCE.md)

Viz [Přejímací kroky před v1.0.0](V1_RELEASE_PLAN.md): pořadí kontrol, spuštění s oddělenými daty, šablona výsledků a podmínky vydání.

Stav 22. listopadu 2026: uživatel potvrdil dokončení testování v0.15.0 a schválil PR #32. Tento seznam nyní cílí na v0.18.1; jednotlivé výsledky čistého počítače/DPI zde nejsou zaznamenané. Nezaškrtnuté body zůstávají neověřené; při testování nového vydání doplň důkazy pro konkrétní zařízení.

Zaznamenej edici/build Windows, architekturu CPU, rozlišení/měřítko, commit artefaktu, SHA-256, datum, testujícího a výsledky. Přilož snímky a postup reprodukce chyb. Každý bod označ PASS/FAIL s důkazem; nezaškrtnutý není ověřený.

- [ ] Stáhnout, ověřit kontrolní součet, rozbalit oba ZIPy a spustit bez Pythonu/práv správce.
- [ ] Prázdný start bez vzorových předmětů, skóre a času; ověřit cestu k datům a restart.
- [ ] Vytvořit/upravit Unicode předmět, téma a otázku se čtyřmi možnostmi; hledat/filtrovat a restartovat.
- [ ] Importovat CSV otázek/kartiček, odmítnout chybný soubor, zrušit náhled a bezpečně zopakovat chybný zápis.
- [ ] Vytvořit/odhalit/ohodnotit kartičky a ověřit uložené termíny/historii.
- [ ] Časovaný/nečasovaný test: uložit odpovědi, zavřít a pokračovat, dokončit a prohlédnout výsledek. Projít více než 20 pokusů a filtrovat historii.
- [ ] Spustit/pozastavit/dokončit soustředění; ověřit skutečný uložený čas a Statistics.
- [ ] Uložit/restartovat všechny čtyři jazyky; ověřit dlouhé popisky/azbuku, původní obsah a samostatný jazyk AI.
- [ ] V 1440×900 a 1024×700 ověřit změnu velikosti, vnořené posouvání, klávesnici, dialogy a podporovaná měřítka 100/125/150 %.
- [ ] Bez Ollamy/offline musí fungovat studium. Je-li dostupná, výslovně připojit reálný model, stream/Stop/opětovné připojení a uložený chat; zapsat model a hardware zvlášť.
- [ ] Záloha/validace/obnova dočasných dat, bezpečnostní kopie, zavření a kontrola po restartu; ostatní instance při obnově zavřít.
- [ ] Zavřít přes titulní lištu i hlavní panel a otevřít znovu; přesunout/aktualizovat aplikaci bez ztráty dat. Vyzkoušet druhou instanci/zamčená data a užitečnou chybu.

Použij [přenosnou verzi](WINDOWS_PORTABLE.md) nebo [spuštění ze zdrojů](https://github.com/turcinv/SOSkuska/blob/main/docs/cs/WINDOWS_FIRST_RUN.md). Hostované CI ověřuje start/pomocníky; neoznačuje tento ruční seznam za dokončený.
