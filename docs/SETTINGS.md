# Nastavení

Nastavení se ukládá do stejné databáze jako studijní data.

V **Settings** nastav délku příštího focus sezení (1–180 minut, výchozí 15), denní cíl (1–1 440 minut, výchozí 60), URL Ollamy, preferovaný model a jazyk AI odpovědi. **Save settings** uloží a použije všechny hodnoty; rozepsané změny přežijí přepnutí obrazovky, ale ne zavření aplikace. Probíhající i pozastavené sezení si zachová původní délku. Cíl se změní hned, historický čas se nepřepočítává.

**Use Tutor choices** jen zkopíruje do formuláře aktuální volby AI Tutor; potom použij Save settings. Přímé změny v AI Tutor jsou dočasné. Uložení, spuštění ani návrat na obrazovku nevytváří síťové spojení. Připoj se výslovně přes Connect / refresh. Nedostupný preferovaný model se nenahradí jiným bez výběru uživatele. Jazyk platí pro AI odpovědi, nikoli rozhraní aplikace.

Při aktivním AI požadavku nejprve počkej nebo použij Stop, než změníš AI preference. Studijní hodnoty lze uložit dál. Pokud chat patří jinému serveru, nejprve jej vymaž přes New chat a potvrzení. Zapamatování právě připojeného serveru jeho chat zachová. Chat se při zavření stále ztratí.

Chyba zápisu ani konflikt s jiným oknem neodstraní rozepsané hodnoty. Před Reload si je zkopíruj; u změněného formuláře je nutné potvrdit nahrazení druhým kliknutím. Změny jiného okna se nepoužijí živě: v tomto okně je použije Save nebo restart. Save použije všechny načtené hodnoty, včetně AI nastavení z druhého okna, proto mohou platit výše uvedené ochrany. Neplatná uložená nastavení zobrazí bezpečné výchozí hodnoty; opraví se až výslovným Save.

Nastavení je místní pro vybranou databázi (`--data`), bez synchronizace a šifrování. Chybí volba vzhledu, překlady UI, zálohy a ukládání AI konverzací.
