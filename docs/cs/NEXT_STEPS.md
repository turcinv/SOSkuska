# Další kroky · 27. listopadu 2026

[English](../NEXT_STEPS.md) · [Čeština](NEXT_STEPS.md) · [Slovenčina](../sk/NEXT_STEPS.md) · [Русский](../ru/NEXT_STEPS.md)

Aktuální vydání: **v0.31.1**, schéma **10**.

## Od 26. listopadu 2026

- **v0.27.0:** Dashboard ve stylu studijního studia.
- **v0.28.0:** logo aplikace.
- **v0.29.0:** redesign s kočičí značkou ([předání](../agents/design/cat-brand/README.md)).
- **v0.30.0:** AI generování kartiček a otázek z poznámek ([průvodce](AI_NOTE_GENERATION.md)).
- **v0.30.1:** opravy z prvního hodnocení se skutečným modelem ([záznam](../agents/design/ai-note-generation/EVALUATION.md)). Opravy se týkají odpovědí umísťovaných aplikací, ochrany proti vložení pokynů do poznámek, upozornění na návrhy, které se v poznámkách nenašly, a jazyka studijních režimů.
- **v0.31.0:** server MCP jen pro čtení ([návod](MCP_SERVER.md), [plán](../agents/MCP_SERVER_PLAN.md)): vrstva dotazů z fáze 1 (PR #76) a server přes stdio z fáze 2.
- **v0.31.1:** požadavky AI se už nezdrží, když by se garbage collector spustil v jejich pracovním vlákně; nástroj s ukázkovými daty pro přejímku MCP.
- Dřívější kroky 1–5 světlého UI jsou historické; jejich vizuální směr nahrazuje kočičí značka.

## Doporučené pořadí

1. **Opravit zjištění z revize 27. listopadu.** Sedm otevřených zjištění (tři P2 mezery v zastaralém stavu/souhlasu, čtyři P3) z revize repozitáře jiným modelem je zapsáno v [Zjištěních revize](REVIEW_FINDINGS.md). Opravte je na jedné větvi s regresními testy, počínaje S27-01 až S27-03.
2. **Nativní vizuální přejímka v0.29–v0.30.1.** Design a AI panely byly zatím ověřeny jen na snímcích z Linuxu/Xvfb.
   - Na Macu a ideálně na počítači s Windows při měřítku 100 % a 150 % použijte dočasná data (`--data .local-data/acceptance.sqlite3`).
   - Zkontrolujte Light/Dark, čtyři jazyky, 1440 × 900 a 1024 × 700, sbalení postranního panelu, banner na Dashboardu a **Generovat pomocí AI** v sadě kartiček a v bance otázek.
   - Zapište OS/build, měřítko a zjištění do [seznamu pro Windows](WINDOWS_ACCEPTANCE.md). Problémy řešte přes revidovaná PR.
3. **Širší hodnocení AI.** Znovu spusťte `tools/evaluate_ai.py` alespoň s jedním dalším modelem (například `llama3.2:3b`) a s dlouhými poznámkami a 20 položkami. Porovnejte se záznamem z 26. listopadu. Tutor se streamováním/Stop/opětovným připojením/historií se skutečným modelem stále potřebuje ruční průchod.
4. **Ukázka vyučujícímu a pololetní zpráva.** Koncepty scénáře ukázky, osnovy zprávy a 17 snímků obrazovky jsou v [semester](../semester/README.md) (anglicky); nacvičte nativně a doplňte zástupné údaje.
   - Nacvičte ukázku nativně na prezentačním počítači, případně pořiďte nativní snímky obrazovky a doplňte zástupné údaje.
5. **Přejímka MCP se skutečným hostitelem.** Ukázková data vytvořte pomocí `tools/make_mcp_acceptance_db.py` (viz [pravidla MCP](../agents/MCP.md)). Připojte Claude Desktop, VS Code nebo Kiro k dočasné databázi, vypište předměty, spusťte Quiz me se skrytými odpověďmi, při nečinném hostiteli obnovte v aplikaci zálohu a hostitele, verze a výsledky zapište do [plánu](../agents/MCP_SERVER_PLAN.md).
6. **Úklid.** Sloučené vzdálené větve mažte jen na výslovnou žádost; ponechte `main` a značky vydání.

Před v1.0.0 vyřešte zjištění z přejímky přes revidovaná PR a zopakujte příslušné kontroly. Nová práce, sloučení i vydání potřebují vlastní schválení. Tato aktualizace stavu neoznačuje žádný ruční výsledek jako úspěšný.
