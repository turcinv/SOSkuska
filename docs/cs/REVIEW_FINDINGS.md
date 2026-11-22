# Nálezy revize hlavní větve Astra 6.2

[English](../REVIEW_FINDINGS.md) · [Čeština](REVIEW_FINDINGS.md) · [Slovenčina](../sk/REVIEW_FINDINGS.md) · [Русский](../ru/REVIEW_FINDINGS.md)

Záznam revize Astra 6.2 s nízkým úsilím pro v0.18.0, commit `252acc588700e46f0df5f76c9a31879104924fa2`. Soubor zůstane záznamem řešení; stav měň až po ověření opravy. Větev: `fix/main-review-findings`. Záznam nepovoluje sloučení ani vydání.

| ID | Priorita | Stav | Nález | Požadované chování |
| --- | --- | --- | --- | --- |
| A62-01 | P2 | Otevřené | Starší formulář předmětu přepíše popis nebo termín změněný v jiném okně. | Porovnat původní obsah pod zápisovým zámkem a zachovat odmítnutý koncept. |
| A62-02 | P2 | Otevřené | Staré potvrzení smazání odstraní otázku změněnou v jiném okně; témata používají stejný postup. | Atomicky porovnat zobrazený obsah; změna vyžaduje nové potvrzení. |
| A62-03 | P2 | Otevřené | Návrat do banky otázek stejného předmětu ztratí rozpísanou otázku. | Zachovat editor, původní identitu a koncept při návratu ke stejnému předmětu. |
| A62-04 | P3 | Otevřené | Oznámení selhání zálohy zůstává po úspěchu dnešní zálohy v jiném okně. | Načíst novější potvrzení úspěchu a odstranit jen překonané oznámení chyby. |
