# Štatistiky (v0.6.0)

[English](../STATISTICS.md) · [Čeština](../cs/STATISTICS.md) · [Slovenčina](STATISTICS.md) · [Русский](../ru/STATISTICS.md)

V ponuke **Statistics** zvoľ Last 7 days, Last 30 days alebo All time. Prehľad ukazuje uložený čas a relácie, úspešnosť dokončených testov váženú otázkami, počty vlastných hodnotení kartičiek, čas podľa predmetu a dennú aktivitu. Refresh alebo návrat na obrazovku načíta novú snímku. Nejde o meranie zvládnutia učiva.

## Význam čísel

- Focus: iba uložené nenulové relácie; bežiaci a neuložený čas sa nezahŕňa. Dni s učením znamenajú dni s uloženým časom.
- Practice Tests: len dokončené pokusy, podľa dátumu dokončenia. Úspešnosť = správne odpovede / všetky otázky; každá otázka má rovnakú váhu a nezodpovedaná je nesprávna. Rozpracované a zahodené pokusy sa nezapočítajú. Bez dokončeného testu sa nezobrazuje vymyslené percento.
- Flashcards: počet uložených hodnotení Again / Hard / Good / Easy vrátane opakovaní tej istej kartičky. Ide o vlastné hodnotenie, nie presnosť či zvládnutie učiva. Testy ani kartičky nepridávajú čas do Focus.

## Obdobia a história

Obdobie zahŕňa dnešok a predchádzajúcich 6 alebo 29 miestnych kalendárnych dní. All time zahŕňa všetko až do dneška, denný graf však iba posledných 30 dní. Budúce kalendárne dni sa nezapočítajú. Relácie používajú uložený miestny dátum; testy a hodnotenia prevádzajú UTC čas do aktuálneho systémového pásma. Zmena pásma môže presunúť historickú udalosť medzi dňami. Relácia cez polnoc zostáva celá v dni uloženia.

História sa neobmedzuje na posledných 20 položiek z ostatných obrazoviek. Zmazanie predmetu, kartičky či balíčka neodstráni uložené historické výsledky. Živé predmety sa zoskupujú podľa ID a aktuálneho názvu; záznamy bez dostupného predmetu podľa uloženého názvu, pôvodné bez názvu ako Unassigned sessions. Po zmazaní môžu rovnako pomenované predmety splynúť do jedného riadka. Zobrazuje sa najviac 50 skupín podľa času, celkové súčty zahŕňajú všetky. Pruhy porovnávajú hodnoty medzi riadkami, nie pokrok voči cieľu.

## Implementácia a obmedzenia

`statistics_page.py` zobrazuje prehľad; `study_statistics.py` obsahuje dotazy a zostavenie reportu cez `Store.statistics()`. Štyri agregácie bežia v jednej čítacej transakcii. Aktuálna schéma je 8; štatistiky nepridávajú závislosti ani zápisy do údajov. Aktualizácia je ručná alebo pri návrate, bez časovača na pozadí. Pri chybe načítania zostane predchádzajúci prehľad a možno skúsiť Refresh; nemusí byť aktuálny.

Export, vlastný rozsah dátumov, filter predmetu a pokročilé grafy zatiaľ nie sú súčasťou funkcie. AI Tutor má voliteľný chat s miestnou históriou cez Ollamu.
