# Další kroky · 26. listopadu 2026

[English](../NEXT_STEPS.md) · [Čeština](NEXT_STEPS.md) · [Slovenčina](../sk/NEXT_STEPS.md) · [Русский](../ru/NEXT_STEPS.md)

Aktuální vydání: **v0.26.0**, schéma **10**. Implementace kroků designu 1–5 je hotová přes PR #43, #44, #46, #48, #50, #52 a #54. Zbývá krok 6: přejímka a příprava ukázky.

## Úplná revize Astra dokončena · 26. listopadu 2026

Požadovaná úplná revize main/v0.26.0 pomocí **Astra 6.2 medium** je hotová. Kontrolovaný commit: `db38e08802058480bbed250c16eeffc23bad143b`. **Všech pět nálezů je opraveno na `fix/astra-main-findings` (nevydáno)** v [nálezech revize](REVIEW_FINDINGS.md), ID A62-05–A62-09. Opravy řešit samostatnou větví/PR; sloučení a vydání vyžadují vlastní schválení. Automatické kontroly prošly; cílené kontroly použily dočasná data a Docker/Xvfb. Test skutečného LLM zůstává odložený.

1. **Dále: krok 6, regresní kontroly a ukázka vyučujícímu.** Použít [plán](../agents/BRIGHT_UI_REDESIGN.md) a [předání nastavení/dat](../agents/design/bright-ui-step5-settings/README.md). Na dočasných datech ověřit celý studijní postup, Light/Dark/System, čtyři jazyky a kompaktní/široké okno; obnovit finální snímky a důkazy pro ukázku. Případné opravy řešit samostatnou revidovanou větví/PR. Z automatických kontrol nevyvozovat ruční přejímku hardwaru.
2. **Po redesignu dokončit přejímku.** Použít [Windows seznam](WINDOWS_ACCEPTANCE.md), dočasná data a zapsat OS/build, hardware, měřítko, verzi/součet a výsledky. Počáteční měřítko neověřuje nativní/živé DPI. Samostatně otestovat skutečnou Ollamu: verze serveru/modelu, hardware, stream/Stop/opětovné připojení/historie a offline studium.
3. **Samostatně dokončit práci a prezentaci.** Osobní údaje/předmět/jazyk/termín ponechat jako zástupná pole do dodání; doplnit skutečné snímky, zdroje a důkazy. Řídit se zadáním, aktualizovat pole dokumentu a prohlédnout stránkování.

Před v1.0.0 vyřešit nálezy přes revidované PR a zopakovat kontroly. Nová práce, sloučení i vydání potřebují vlastní schválení. Tato aktualizace nepotvrzuje ruční výsledky.
