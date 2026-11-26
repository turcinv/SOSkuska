# Ďalšie kroky · 26. novembra 2026

[English](../NEXT_STEPS.md) · [Čeština](../cs/NEXT_STEPS.md) · [Slovenčina](NEXT_STEPS.md) · [Русский](../ru/NEXT_STEPS.md)

Aktuálne vydanie: **v0.28.0**, schéma **10**. Implementácia krokov dizajnu 1–5 je hotová cez PR #43, #44, #46, #48, #50, #52 a #54. Zostáva krok 6: akceptácia a príprava ukážky.

## Úplná revízia Astra dokončená · 26. novembra 2026

Požadovaná úplná revízia main/v0.26.0 pomocou **Astra 6.2 medium** je hotová. Kontrolovaný commit: `db38e08802058480bbed250c16eeffc23bad143b`. **Všetkých päť nálezov je vydaných vo v0.26.1** v [nálezoch revízie](REVIEW_FINDINGS.md), ID A62-05–A62-09. Opravy riešiť samostatnou vetvou/PR; zlúčenie a vydanie vyžadujú vlastné schválenie. Automatické kontroly prešli; cielené kontroly použili dočasné dáta a Docker/Xvfb. Test skutočného LLM zostáva odložený.

1. **Ďalej: krok 6, regresné kontroly a ukážka vyučujúcemu.** Použiť [plán](../agents/BRIGHT_UI_REDESIGN.md) a [odovzdanie nastavení/dát](../agents/design/bright-ui-step5-settings/README.md). Na dočasných dátach overiť celý študijný postup, Light/Dark/System, štyri jazyky a kompaktné/široké okno; obnoviť finálne snímky a dôkazy pre ukážku. Prípadné opravy riešiť samostatnou revidovanou vetvou/PR. Z automatických kontrol nevyvodzovať ručnú akceptáciu hardvéru.
2. **Po redizajne dokončiť akceptáciu.** Použiť [Windows zoznam](WINDOWS_ACCEPTANCE.md), dočasné dáta a zapísať OS/build, hardvér, mierku, verziu/súčet a výsledky. Počiatočná mierka neoveruje natívne/živé DPI. Samostatne otestovať skutočnú Ollamu: verzie servera/modelu, hardvér, stream/Stop/opätovné pripojenie/história a offline štúdium.
3. **Samostatne dokončiť prácu a prezentáciu.** Osobné údaje/predmet/jazyk/termín ponechať ako zástupné polia do dodania; doplniť skutočné snímky, zdroje a dôkazy. Riadiť sa zadaním, aktualizovať polia dokumentu a prezrieť stránkovanie.

Pred v1.0.0 vyriešiť nálezy cez revidované PR a zopakovať kontroly. Nová práca, zlúčenie aj vydanie potrebujú vlastné schválenie. Táto aktualizácia nepotvrdzuje ručné výsledky.
