# Ďalšie kroky · 27. novembra 2026

[English](../NEXT_STEPS.md) · [Čeština](../cs/NEXT_STEPS.md) · [Slovenčina](NEXT_STEPS.md) · [Русский](../ru/NEXT_STEPS.md)

Aktuálne vydanie: **v0.30.1**, schéma **10**.

## Od 26. novembra 2026

- **v0.27.0:** Dashboard v štýle študijného štúdia.
- **v0.28.0:** logo aplikácie.
- **v0.29.0:** redizajn s mačacou značkou ([odovzdanie](../agents/design/cat-brand/README.md)).
- **v0.30.0:** AI generovanie kartičiek a otázok z poznámok ([sprievodca](AI_NOTE_GENERATION.md)).
- **v0.30.1:** opravy z prvého hodnotenia so skutočným modelom ([záznam](../agents/design/ai-note-generation/EVALUATION.md)). Opravy sa týkajú odpovedí umiestňovaných aplikáciou, ochrany proti vloženiu pokynov do poznámok, upozornenia na návrhy, ktoré sa v poznámkach nenašli, a jazyka študijných režimov.
- **Zlúčené, nevydané:** [plán](../agents/MCP_SERVER_PLAN.md) servera MCP len na čítanie a jeho fáza 1, bezokenná vrstva dopytov len na čítanie (`soskuska/study_queries.py`, PR #76). Server MCP zatiaľ neexistuje.
- Skoršie kroky 1–5 svetlého UI sú historické; ich vizuálny smer nahrádza mačacia značka.

## Odporúčané poradie

1. **Natívna vizuálna akceptácia v0.29–v0.30.1.** Dizajn a AI panely boli zatiaľ overené len na snímkach z Linuxu/Xvfb.
   - Na Macu a ideálne na počítači s Windows pri mierke 100 % a 150 % použite dočasné dáta (`--data .local-data/acceptance.sqlite3`).
   - Skontrolujte Light/Dark, štyri jazyky, 1440 × 900 a 1024 × 700, zbalenie bočného panela, banner na Dashboarde a **Generovať pomocou AI** v sade kartičiek a v banke otázok.
   - Zapíšte OS/build, mierku a zistenia do [zoznamu pre Windows](WINDOWS_ACCEPTANCE.md). Problémy riešte cez revidované PR.
2. **Širšie hodnotenie AI.** Znova spustite `tools/evaluate_ai.py` aspoň s jedným ďalším modelom (napríklad `llama3.2:3b`) a s dlhými poznámkami a 20 položkami. Porovnajte so záznamom z 26. novembra. Tutor so streamovaním/Stop/opätovným pripojením/históriou so skutočným modelom stále potrebuje ručný prechod.
3. **Ukážka vyučujúcemu a polročná správa.**
   - Pripravte krátky scenár ukážky: vytvoriť predmet, vygenerovať otázky z poznámok, precvičovať, opakovať kartičky, otvoriť Štatistiky.
   - Obnovte snímky obrazovky z dočasných dát.
   - Údaje o identite, kurze, jazyku a termíne ponechajte ako zástupné polia do dodania a skontrolujte výsledné stránkovanie.
4. **Stabilizovať štartovaciu sondu GUI v hostovanom CI.** 27. novembra `check_studio_layout.py` na strojoch GitHubu prekročil sedemsekundový limit čerstvého procesu, a to aj pri commite na `main`, ktorý menil len dokumentáciu; po zopakovaní prešiel. Obmedzte prácu pri štarte alebo ho merajte spôsobom, ktorý zaťaženie hostovaných strojov nerozbije. Limit len nezvyšujte.
5. **Fáza 2 servera MCP.** Server cez stdio s voliteľnou pripnutou závislosťou `mcp`, testy, nastavenie CI/kontajnera, používateľský návod v štyroch jazykoch a zaznamenaný beh so skutočným hostiteľom MCP. Pozri [plán](../agents/MCP_SERVER_PLAN.md).
6. **Upratovanie.** Zlúčené vzdialené vetvy mažte len na výslovnú žiadosť; ponechajte `main` a značky vydania.

Pred v1.0.0 vyriešte zistenia z akceptácie cez revidované PR a zopakujte príslušné kontroly. Nová práca, zlúčenie aj vydanie potrebujú vlastné schválenie. Táto aktualizácia stavu neoznačuje žiadny ručný výsledok ako úspešný.
