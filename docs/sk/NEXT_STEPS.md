# Ďalšie kroky · 27. novembra 2026

[English](../NEXT_STEPS.md) · [Čeština](../cs/NEXT_STEPS.md) · [Slovenčina](NEXT_STEPS.md) · [Русский](../ru/NEXT_STEPS.md)

Aktuálne vydanie: **v0.31.2**, schéma **10**.

## Od 26. novembra 2026

- **v0.27.0:** Dashboard v štýle študijného štúdia.
- **v0.28.0:** logo aplikácie.
- **v0.29.0:** redizajn s mačacou značkou ([odovzdanie](../agents/design/cat-brand/README.md)).
- **v0.30.0:** AI generovanie kartičiek a otázok z poznámok ([sprievodca](AI_NOTE_GENERATION.md)).
- **v0.30.1:** opravy z prvého hodnotenia so skutočným modelom ([záznam](../agents/design/ai-note-generation/EVALUATION.md)). Opravy sa týkajú odpovedí umiestňovaných aplikáciou, ochrany proti vloženiu pokynov do poznámok, upozornenia na návrhy, ktoré sa v poznámkach nenašli, a jazyka študijných režimov.
- **v0.31.0:** server MCP len na čítanie ([návod](MCP_SERVER.md), [plán](../agents/MCP_SERVER_PLAN.md)): vrstva dopytov z fázy 1 (PR #76) a server cez stdio z fázy 2.
- **v0.31.1:** požiadavky AI sa už nezdržia, keď by sa garbage collector spustil v ich pracovnom vlákne; nástroj s ukážkovými dátami na akceptáciu MCP.
- **v0.31.2:** opravy siedmich zistení z revízie 27. novembra ([záznam](REVIEW_FINDINGS.md)).
- Skoršie kroky 1–5 svetlého UI sú historické; ich vizuálny smer nahrádza mačacia značka.

## Odporúčané poradie

1. **Natívna vizuálna akceptácia v0.29–v0.30.1.** Dizajn a AI panely boli zatiaľ overené len na snímkach z Linuxu/Xvfb.
   - Na Macu a ideálne na počítači s Windows pri mierke 100 % a 150 % použite dočasné dáta (`--data .local-data/acceptance.sqlite3`).
   - Skontrolujte Light/Dark, štyri jazyky, 1440 × 900 a 1024 × 700, zbalenie bočného panela, banner na Dashboarde a **Generovať pomocou AI** v sade kartičiek a v banke otázok.
   - Zapíšte OS/build, mierku a zistenia do [zoznamu pre Windows](WINDOWS_ACCEPTANCE.md). Problémy riešte cez revidované PR.
2. **Širšie hodnotenie AI.** Znova spustite `tools/evaluate_ai.py` aspoň s jedným ďalším modelom (napríklad `llama3.2:3b`) a s dlhými poznámkami a 20 položkami. Porovnajte so záznamom z 26. novembra. Tutor so streamovaním/Stop/opätovným pripojením/históriou so skutočným modelom stále potrebuje ručný prechod.
3. **Ukážka vyučujúcemu a polročná správa.** Koncepty scenára ukážky, osnovy správy a 17 snímok obrazovky sú v [semester](../semester/README.md) (anglicky); nacvičte natívne a doplňte zástupné údaje.
   - Nacvičte ukážku natívne na prezentačnom počítači, prípadne nasnímajte natívne snímky obrazovky a doplňte zástupné údaje.
4. **Akceptácia MCP so skutočným hostiteľom.** Ukážkové dáta vytvorte pomocou `tools/make_mcp_acceptance_db.py` (pozri [pravidlá MCP](../agents/MCP.md)). Pripojte Claude Desktop, VS Code alebo Kiro k dočasnej databáze, vypíšte predmety, spustite Quiz me so skrytými odpoveďami, pri nečinnom hostiteľovi obnovte v aplikácii zálohu a hostiteľa, verzie a výsledky zapíšte do [plánu](../agents/MCP_SERVER_PLAN.md).
5. **Upratovanie.** Zlúčené vzdialené vetvy mažte len na výslovnú žiadosť; ponechajte `main` a značky vydania.

Pred v1.0.0 vyriešte zistenia z akceptácie cez revidované PR a zopakujte príslušné kontroly. Nová práca, zlúčenie aj vydanie potrebujú vlastné schválenie. Táto aktualizácia stavu neoznačuje žiadny ručný výsledok ako úspešný.
