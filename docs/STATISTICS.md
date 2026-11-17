# Statistiky (v0.6.0)

V nabídce **Statistics** zvol Last 7 days, Last 30 days nebo All time. Přehled ukazuje uložený čas a sezení, otázkami váženou úspěšnost dokončených testů, počty vlastních hodnocení kartiček, čas podle předmětu a denní aktivitu. Refresh nebo návrat na obrazovku načte nový snímek. Nejde o měření zvládnutí učiva.

## Význam čísel

- Focus: pouze uložená nenulová sezení; běžící a neuložený čas se nezahrnuje. Dny s učením znamenají dny s uloženým časem.
- Practice Tests: jen dokončené pokusy, podle data dokončení. Úspěšnost = správné odpovědi / všechny otázky; každá otázka má stejnou váhu a nezodpovězená je nesprávná. Rozpracované a zahozené pokusy se nezapočítají. Bez dokončeného testu se nezobrazuje vymyšlené procento.
- Flashcards: počet uložených hodnocení Again / Hard / Good / Easy, včetně opakování téže kartičky. Jde o vlastní hodnocení, nikoli přesnost nebo zvládnutí učiva. Testy ani kartičky nepřidávají čas do Focus.

## Období a historie

Období zahrnuje dnešek a předchozích 6 nebo 29 místních kalendářních dní. All time zahrnuje vše až do dneška, denní graf však pouze posledních 30 dní. Budoucí kalendářní dny se nezapočítají. Sezení používají uložené místní datum; testy a hodnocení převádějí UTC čas do aktuálního systémového pásma. Změna pásma může přesunout historickou událost mezi dny. Sezení přes půlnoc zůstává celé ve dni uložení.

Historie se neomezuje na posledních 20 položek z ostatních obrazovek. Smazání předmětu, kartičky či balíčku neodstraní uložené historické výsledky. Živé předměty se seskupují podle ID a aktuálního názvu; záznamy bez dostupného předmětu podle uloženého názvu, původní bez názvu jako Unassigned sessions. Po smazání mohou stejně pojmenované předměty splynout do jednoho řádku. Zobrazuje se nejvýše 50 skupin podle času, celkové součty zahrnují všechny. Pruhy porovnávají hodnoty mezi řádky, nikoli pokrok vůči cíli.

## Implementace a omezení

`statistics_page.py` zobrazuje přehled; `study_statistics.py` obsahuje dotazy a sestavení reportu přes `Store.statistics()`. Čtyři agregace běží v jedné čtecí transakci. Schéma zůstává 5, bez nových závislostí a zápisů do dat. Aktualizace je ruční nebo při návratu, bez časovače na pozadí. Při chybě načtení zůstane předchozí přehled a lze zkusit Refresh; nemusí být aktuální.

Export, vlastní rozsah dat, filtr předmětu a pokročilé grafy zatím nejsou součástí funkce. AI Tutor zůstává plánovaný.
