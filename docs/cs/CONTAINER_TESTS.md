# Testy v kontejneru

[English](../CONTAINER_TESTS.md) · [Čeština](../cs/CONTAINER_TESTS.md) · [Slovenčina](../sk/CONTAINER_TESTS.md) · [Русский](../ru/CONTAINER_TESTS.md)

Pro běžné kontroly používej kontejner, aby okna GUI nerušila práci na ploše. Docker musí být nainstalovaný a spuštěný; projekt Docker Desktop automaticky neinstaluje ani nespouští. Z kořene repozitáře:

```sh
docker build -f Dockerfile.tests -t soskuska-tests .
docker run --rm --init --network none --cpus 2 --memory 2g soskuska-tests
```

Zachovej `--init`: zajistí správné doručení startovacího signálu virtuálnímu displeji a úklid potomků procesu.

Sestavení stahuje Python, systémové knihovny a závislosti, proto vyžaduje internet. Po změně zdrojů obraz znovu sestav; soubory se kopírují do obrazu, nejsou připojené živě. Další sestavení využije mezipaměť závislostí. Testy potřebují jen místní smyčku pro falešnou Ollamu, takže vnější síť je vypnutá. Limity CPU/paměti omezují rušení ostatní práce; případně je uprav. Nepřipojuje se displej ani datová složka hostitele a neotevírají se porty. `.dockerignore` povoluje pouze testované zdroje; prostředí, databáze, tajné údaje a historie Gitu zůstávají mimo kontext sestavení. Kontejner se potom odstraní, obraz a mezipaměť zůstanou.

Obraz běží jako běžný uživatel bez práv root. Xvfb vytvoří vnitřní virtuální obrazovku pro každý GUI skript; na hostiteli se neotevřou okna aplikace. Společný `tools/run_checks.py` spustí kontrolu závislostí, syntaxe, jednotkové testy a GUI skripty (351 jednotkových testů a 26 GUI skriptů ve v0.30.1) s časovým limitem pro každý proces. Celek trvá zhruba pět minut; chyba vrací nenulový kód. CI používá stejný seznam GUI přes `--gui-only` po samostatných jednotkových kontrolách.

Chceš-li spustit jediný skript, přepiš příkaz; ponech `--init` a pevný časový limit:

```sh
docker run --rm --init --network none soskuska-tests timeout 150 xvfb-run -a -s '-screen 0 1920x1080x24' python -X faulthandler -u soskuska/check_note_generation.py
```

Linuxový kontejner neověřuje nativní Quit na macOS, trackpad Tk 9 ani UI Windows. Nativní kontroly na Macu spouštěj jen při relevantní platformní změně a viditelný běh nejprve domluv s uživatelem. Úspěšný kontejner nenahrazuje důležitou selhávající platformní kontrolu.
