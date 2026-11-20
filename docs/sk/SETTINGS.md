# Nastavenia

[English](../SETTINGS.md) · [Čeština](../cs/SETTINGS.md) · [Slovenčina](SETTINGS.md) · [Русский](../ru/SETTINGS.md)

Nastavenia sa ukladajú do rovnakej databázy ako študijné údaje.

V **Settings** nastav dĺžku nasledujúcej focus relácie (1–180 minút, predvolene 15), denný cieľ (1–1 440 minút, predvolene 60), URL Ollamy, preferovaný model a jazyk AI odpovede. **Save settings** uloží a použije všetky hodnoty; rozpísané zmeny prežijú prepnutie obrazovky, ale nie zatvorenie aplikácie. Prebiehajúca aj pozastavená relácia si zachová pôvodnú dĺžku. Cieľ sa zmení hneď, historický čas sa neprepočítava.

**Use Tutor choices** iba skopíruje do formulára aktuálne voľby AI Tutor; potom použi Save settings. Priame zmeny v AI Tutor sú dočasné. Uloženie, spustenie ani návrat na obrazovku nevytvára sieťové spojenie. Pripoj sa výslovne cez Connect / refresh. Nedostupný preferovaný model sa nenahradí iným bez výberu používateľa. Jazyk platí pre AI odpovede, nie rozhranie aplikácie.

Pri aktívnej AI požiadavke najprv počkaj alebo použi Stop, kým zmeníš AI preferencie. Študijné hodnoty možno ukladať ďalej. Ak chat patrí inému serveru, najprv ho odpoj cez New chat a potvrdenie; uložená história zostane. Zapamätanie práve pripojeného servera jeho chat zachová. Konverzácia zostáva uložená po zatvorení aplikácie.

Chyba zápisu ani konflikt s iným oknom neodstráni rozpísané hodnoty. Pred Reload si ich skopíruj; pri zmenenom formulári treba potvrdiť nahradenie druhým kliknutím. Zmeny iného okna sa nepoužijú priebežne: v tomto okne ich použije Save alebo reštart. Save použije všetky načítané hodnoty vrátane AI nastavení z druhého okna, preto môžu platiť uvedené ochrany. Neplatné uložené nastavenia zobrazia bezpečné predvolené hodnoty; opravia sa až výslovným Save.

Nastavenia sú miestne pre vybranú databázu (`--data`), bez synchronizácie a šifrovania. Chýba voľba vzhľadu a preklady UI.

Pri pripojení k inému serveru sa model vyberie znovu podľa uloženej preferencie. Obnovenie rovnakého servera zachová ručne vybraný dostupný model.

## Záloha a obnova

Settings teraz ponúka ručnú miestnu zálohu a overenú obnovu s bezpečnostnou kópiou pred nahradením. Aktuálna schéma je 7. Obnova zatvorí aplikáciu; potom ju spusti znovu. Pozri [Záloha a obnova](BACKUP_RESTORE.md).

## Uložené konverzácie AI Tutor

AI Tutor teraz ukladá konverzácie lokálne vrátane pôvodného servera/modelu a stavu odpovede. Históriu možno otvoriť bez siete, výslovne sa pripojiť na pokračovanie alebo vybranú konverzáciu po potvrdení zmazať. Schéma 7 migruje pôvodné študijné údaje transakčne; vydanou verziou zostáva v0.11.1 do schválenia ďalšieho vydania. [Uložené konverzácie AI Tutor](TUTOR_HISTORY.md).
