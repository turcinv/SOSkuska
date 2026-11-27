# Další kroky · 27. listopadu 2026

[English](../NEXT_STEPS.md) · [Čeština](NEXT_STEPS.md) · [Slovenčina](../sk/NEXT_STEPS.md) · [Русский](../ru/NEXT_STEPS.md)

Aktuální vydání: **v0.30.1**, schéma **10**.

## Od 26. listopadu 2026

- **v0.27.0:** Dashboard ve stylu studijního studia.
- **v0.28.0:** logo aplikace.
- **v0.29.0:** redesign s kočičí značkou ([předání](../agents/design/cat-brand/README.md)).
- **v0.30.0:** AI generování kartiček a otázek z poznámek ([průvodce](AI_NOTE_GENERATION.md)).
- **v0.30.1:** opravy z prvního hodnocení se skutečným modelem ([záznam](../agents/design/ai-note-generation/EVALUATION.md)). Opravy se týkají odpovědí umísťovaných aplikací, ochrany proti vložení pokynů do poznámek, upozornění na návrhy, které se v poznámkách nenašly, a jazyka studijních režimů.
- **Sloučeno, nevydáno:** [plán](../agents/MCP_SERVER_PLAN.md) serveru MCP jen pro čtení a jeho fáze 1, bezokenní vrstva dotazů jen pro čtení (`soskuska/study_queries.py`, PR #76). Server MCP zatím neexistuje.
- Dřívější kroky 1–5 světlého UI jsou historické; jejich vizuální směr nahrazuje kočičí značka.

## Doporučené pořadí

1. **Nativní vizuální přejímka v0.29–v0.30.1.** Design a AI panely byly zatím ověřeny jen na snímcích z Linuxu/Xvfb.
   - Na Macu a ideálně na počítači s Windows při měřítku 100 % a 150 % použijte dočasná data (`--data .local-data/acceptance.sqlite3`).
   - Zkontrolujte Light/Dark, čtyři jazyky, 1440 × 900 a 1024 × 700, sbalení postranního panelu, banner na Dashboardu a **Generovat pomocí AI** v sadě kartiček a v bance otázek.
   - Zapište OS/build, měřítko a zjištění do [seznamu pro Windows](WINDOWS_ACCEPTANCE.md). Problémy řešte přes revidovaná PR.
2. **Širší hodnocení AI.** Znovu spusťte `tools/evaluate_ai.py` alespoň s jedním dalším modelem (například `llama3.2:3b`) a s dlouhými poznámkami a 20 položkami. Porovnejte se záznamem z 26. listopadu. Tutor se streamováním/Stop/opětovným připojením/historií se skutečným modelem stále potřebuje ruční průchod.
3. **Ukázka vyučujícímu a pololetní zpráva.**
   - Připravte krátký scénář ukázky: vytvořit předmět, vygenerovat otázky z poznámek, procvičovat, opakovat kartičky, otevřít Statistiky.
   - Obnovte snímky obrazovky z dočasných dat.
   - Údaje o identitě, kurzu, jazyku a termínu ponechte jako zástupná pole do dodání a zkontrolujte výsledné stránkování.
4. **Stabilizovat startovní sondu GUI v hostovaném CI.** 27. listopadu `check_studio_layout.py` na strojích GitHubu překročil sedmisekundový limit čerstvého procesu, a to i u commitu na `main`, který měnil jen dokumentaci; po opakování prošel. Omezte práci při startu, nebo ho měřte způsobem, který zatížení hostovaných strojů nerozbije. Limit jen nezvyšujte.
5. **Fáze 2 serveru MCP.** Server přes stdio s volitelnou připnutou závislostí `mcp`, testy, nastavení CI/kontejneru, uživatelský návod ve čtyřech jazycích a zaznamenaný běh se skutečným hostitelem MCP. Viz [plán](../agents/MCP_SERVER_PLAN.md).
6. **Úklid.** Sloučené vzdálené větve mažte jen na výslovnou žádost; ponechte `main` a značky vydání.

Před v1.0.0 vyřešte zjištění z přejímky přes revidovaná PR a zopakujte příslušné kontroly. Nová práce, sloučení i vydání potřebují vlastní schválení. Tato aktualizace stavu neoznačuje žádný ruční výsledek jako úspěšný.
