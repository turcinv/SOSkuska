# Nastavení

[English](../SETTINGS.md) · [Čeština](SETTINGS.md) · [Slovenčina](../sk/SETTINGS.md) · [Русский](../ru/SETTINGS.md)

Nastavení se ukládá do stejné databáze jako studijní data.

V **Settings** nastav délku příštího focus sezení (1–180 minut, výchozí 15), denní cíl (1–1 440 minut, výchozí 60), URL Ollamy, preferovaný model a jazyk AI odpovědi. **Save settings** uloží a použije všechny hodnoty; rozepsané změny přežijí přepnutí obrazovky, ale ne zavření aplikace. Probíhající i pozastavené sezení si zachová původní délku. Cíl se změní hned, historický čas se nepřepočítává.

**Use Tutor choices** jen zkopíruje do formuláře aktuální volby AI Tutor; potom použij Save settings. Přímé změny v AI Tutor jsou dočasné. Uložení, spuštění ani návrat na obrazovku nevytváří síťové spojení. Připoj se výslovně přes Connect / refresh. Nedostupný preferovaný model se nenahradí jiným bez výběru uživatele. Jazyk platí pro AI odpovědi, nikoli rozhraní aplikace.

Při aktivním AI požadavku nejprve počkej nebo použij Stop, než změníš AI preference. Studijní hodnoty lze uložit dál. Pokud chat patří jinému serveru, nejprve jej odpoj přes New chat a potvrzení; uložená historie zůstane. Zapamatování právě připojeného serveru jeho chat zachová. Konverzace zůstává uložená po zavření aplikace.

Chyba zápisu ani konflikt s jiným oknem neodstraní rozepsané hodnoty. Před Reload si je zkopíruj; u změněného formuláře je nutné potvrdit nahrazení druhým kliknutím. Změny jiného okna se nepoužijí živě: v tomto okně je použije Save nebo restart. Save použije všechny načtené hodnoty, včetně AI nastavení z druhého okna, proto mohou platit výše uvedené ochrany. Neplatná uložená nastavení zobrazí bezpečné výchozí hodnoty; opraví se až výslovným Save.

Nastavení je místní pro vybranou databázi (`--data`), bez synchronizace a šifrování. Chybí volba vzhledu a překlady UI.

Při připojení k jinému serveru se model vybere znovu podle uložené preference. Obnova stejného serveru zachová ručně vybraný dostupný model.

## Záloha a obnova

Settings nyní nabízí ruční místní zálohu a ověřenou obnovu s bezpečnostní kopií před nahrazením. Aktuální schéma je 7. Obnova zavře aplikaci; potom ji spusť znovu. Viz [Záloha a obnova](BACKUP_RESTORE.md).

## Uložené konverzace AI Tutor

AI Tutor nyní ukládá konverzace lokálně včetně původního serveru/modelu a stavu odpovědi. Historii lze otevřít bez sítě, výslovně se připojit pro pokračování nebo vybranou konverzaci po potvrzení smazat. Vydáno ve v0.12.0 se schématem 7, které transakčně migruje původní studijní data. [Uložené konverzace AI Tutor](TUTOR_HISTORY.md).
