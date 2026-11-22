# Nálezy revízie hlavnej vetvy Astra 6.2

[English](../REVIEW_FINDINGS.md) · [Čeština](../cs/REVIEW_FINDINGS.md) · [Slovenčina](REVIEW_FINDINGS.md) · [Русский](../ru/REVIEW_FINDINGS.md)

Záznam revízie Astra 6.2 s nízkym úsilím pre v0.18.0, commit `252acc588700e46f0df5f76c9a31879104924fa2`. Súbor zostane záznamom riešenia; stav meň až po overení opravy. Vetva: `fix/main-review-findings`. Záznam nepovoľuje zlúčenie ani vydanie.

| ID | Priorita | Stav | Nález | Požadované správanie |
| --- | --- | --- | --- | --- |
| A62-01 | P2 | Otvorené | Starší formulár predmetu prepíše popis alebo termín zmenený v inom okne. | Porovnať pôvodný obsah pod zápisovým zámkom a zachovať odmietnutý koncept. |
| A62-02 | P2 | Otvorené | Staré potvrdenie vymazania odstráni otázku zmenenú v inom okne; témy používajú rovnaký postup. | Atomicky porovnať zobrazený obsah; zmena vyžaduje nové potvrdenie. |
| A62-03 | P2 | Otvorené | Návrat do banky otázok rovnakého predmetu stratí rozpísanú otázku. | Zachovať editor, pôvodnú identitu a koncept pri návrate k rovnakému predmetu. |
| A62-04 | P3 | Otvorené | Oznámenie zlyhania zálohy zostáva po úspechu dnešnej zálohy v inom okne. | Načítať novšie potvrdenie úspechu a odstrániť len prekonané oznámenie chyby. |
