# Ďalšie kroky · 26. novembra 2026

[English](../NEXT_STEPS.md) · [Čeština](../cs/NEXT_STEPS.md) · [Slovenčina](NEXT_STEPS.md) · [Русский](../ru/NEXT_STEPS.md)

Aktuálne vydanie: **v0.26.0**, schéma **10**. Implementácia krokov dizajnu 1–5 je hotová cez PR #43, #44, #46, #48, #50, #52 a #54. Zostáva krok 6: akceptácia a príprava ukážky.

## Plán na dnes · 26. novembra 2026

Vykonať **úplnú revíziu aktuálnej vetvy main pomocou Astra**, s vydaním v0.26.0 ako východiskovým stavom. Ide o plán, nie dokončenú revíziu alebo pokyn na jej automatické spustenie.

- Zaznamenať presný kontrolovaný commit. Pokryť správanie aplikácie a architektúru, migrácie SQLite a integritu dát, návrhy a súbežné stavy, rozhranie/navigáciu/posúvanie, AI Tutor a študijné režimy, zálohy/importy, CI/balenie pre Windows a súlad dokumentácie.
- Použiť dočasné dáta a kontajnerové kontroly rozhrania; zachovať plochu používateľa aj bežnú databázu. Test skutočného LLM zostáva odložený a nie je súčasťou tejto plánovanej revízie.
- Uložiť riešiteľné nálezy do repozitára so závažnosťou, súborom/riadkom, reprodukciou či dôkazom a stavom riešenia. Opravy vykonať cez samostatnú vetvu/PR; zlúčenie a vydanie vyžadujú vlastné schválenie.

1. **Ďalej: krok 6, regresné kontroly a ukážka vyučujúcemu.** Použiť [plán](../agents/BRIGHT_UI_REDESIGN.md) a [odovzdanie nastavení/dát](../agents/design/bright-ui-step5-settings/README.md). Na dočasných dátach overiť celý študijný postup, Light/Dark/System, štyri jazyky a kompaktné/široké okno; obnoviť finálne snímky a dôkazy pre ukážku. Prípadné opravy riešiť samostatnou revidovanou vetvou/PR. Z automatických kontrol nevyvodzovať ručnú akceptáciu hardvéru.
2. **Po redizajne dokončiť akceptáciu.** Použiť [Windows zoznam](WINDOWS_ACCEPTANCE.md), dočasné dáta a zapísať OS/build, hardvér, mierku, verziu/súčet a výsledky. Počiatočná mierka neoveruje natívne/živé DPI. Samostatne otestovať skutočnú Ollamu: verzie servera/modelu, hardvér, stream/Stop/opätovné pripojenie/história a offline štúdium.
3. **Samostatne dokončiť prácu a prezentáciu.** Osobné údaje/predmet/jazyk/termín ponechať ako zástupné polia do dodania; doplniť skutočné snímky, zdroje a dôkazy. Riadiť sa zadaním, aktualizovať polia dokumentu a prezrieť stránkovanie.

Pred v1.0.0 vyriešiť nálezy cez revidované PR a zopakovať kontroly. Nová práca, zlúčenie aj vydanie potrebujú vlastné schválenie. Táto aktualizácia nepotvrdzuje ručné výsledky.
