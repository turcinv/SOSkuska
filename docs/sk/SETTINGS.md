# Nastavenia

[English](../SETTINGS.md) · [Čeština](../cs/SETTINGS.md) · [Slovenčina](SETTINGS.md) · [Русский](../ru/SETTINGS.md)

## v0.24.0 — nastavenia a spoločné dátové panely

Nastavenia zoskupujú študijné predvoľby a rozhranie vedľa seba v širokom okne a pod sebou v kompaktnom; AI má vlastnú kartu cez celú šírku. Správa pre Uložiť/Načítať sa zobrazuje pri ovládaní aj v záhlaví. Zmena veľkosti zachová rovnaké prvky, koncepty a uložené snímky; ukladanie zostáva výslovné a aktívne časovače zachovajú pôvodnú dĺžku.

Nastavenia sa ukladajú do rovnakej databázy ako študijné údaje.

V **Settings** nastav dĺžku nasledujúcej focus relácie (1–180 minút, predvolene 15), denný cieľ (1–1 440 minút, predvolene 60), URL Ollamy, preferovaný model a jazyk AI odpovede. **Save settings** uloží a použije všetky hodnoty; rozpísané zmeny prežijú prepnutie obrazovky, ale nie zatvorenie aplikácie. Prebiehajúca aj pozastavená relácia si zachová pôvodnú dĺžku. Cieľ sa zmení hneď, historický čas sa neprepočítava.

**Use Tutor choices** iba skopíruje do formulára aktuálne voľby AI Tutor; potom použi Save settings. Priame zmeny v AI Tutor sú dočasné. Uloženie, spustenie ani návrat na obrazovku nevytvára sieťové spojenie. Pripoj sa výslovne cez Connect / refresh. Nedostupný preferovaný model sa nenahradí iným bez výberu používateľa. Jazyk AI odpovedí a jazyk rozhrania sú samostatné voľby.

Pri aktívnej AI požiadavke najprv počkaj alebo použi Stop, kým zmeníš AI preferencie. Študijné hodnoty možno ukladať ďalej. Ak chat patrí inému serveru, najprv ho odpoj cez New chat a potvrdenie; uložená história zostane. Zapamätanie práve pripojeného servera jeho chat zachová. Konverzácia zostáva uložená po zatvorení aplikácie.

Chyba zápisu ani konflikt s iným oknom neodstráni rozpísané hodnoty. Pred Reload si ich skopíruj; pri zmenenom formulári treba potvrdiť nahradenie druhým kliknutím. Zmeny iného okna sa nepoužijú priebežne: v tomto okne ich použije Save alebo reštart. Save použije všetky načítané hodnoty vrátane AI nastavení z druhého okna, preto môžu platiť uvedené ochrany. Neplatné uložené nastavenia zobrazia bezpečné predvolené hodnoty; opravia sa až výslovným Save.

Nastavenia sú miestne pre vybranú databázu (`--data`), bez synchronizácie a šifrovania. Chýba voľba vzhľadu.

Pri pripojení k inému serveru sa model vyberie znovu podľa uloženej preferencie. Obnovenie rovnakého servera zachová ručne vybraný dostupný model.

## Záloha a obnova

Settings teraz ponúka ručnú miestnu zálohu a overenú obnovu s bezpečnostnou kópiou pred nahradením. Aktuálna schéma je 10. Obnova zatvorí aplikáciu; potom ju spusti znovu. Pozri [Záloha a obnova](BACKUP_RESTORE.md).

## Uložené konverzácie AI Tutor

AI Tutor teraz ukladá konverzácie lokálne vrátane pôvodného servera/modelu a stavu odpovede. Históriu možno otvoriť bez siete, výslovne sa pripojiť na pokračovanie alebo vybranú konverzáciu po potvrdení zmazať. Vydané vo v0.12.0 so schémou 7, ktorá transakčne migruje pôvodné študijné údaje. [Uložené konverzácie AI Tutor](TUTOR_HISTORY.md).

## Jazyk rozhrania

Výber jazyka rozhrania je dostupný vo v0.13.0: angličtina, čeština, slovenčina a ruština. Ukladá sa osobitne od jazyka AI a použije sa po reštarte. Aktuálna schéma je 10. [Jazyk rozhrania](UI_LANGUAGES.md).

## Nastavenie vzhľadu

v0.16.0 pridáva uložené Light/Dark/System, použité po Save bez obnovy obrazoviek a straty aktívnej práce. System sleduje Windows/macOS, na Linuxe používa Light. Aktuálna schéma je 10. Používateľ 22. novembra 2026 potvrdil dokončenie testovania základu a schválil zlúčenie PR #32. [Nastavenie vzhľadu](APPEARANCE.md).

## Obnova sústredenia po páde

v0.17.0 pridáva obnovu sústredenia po páde so schémou **10**. Pred otvorením pôvodných dát vytvor zálohu: migrácia je transakčná, ale v0.16.0 databázu schémy 10 neotvorí. [Obnova sústredenia po páde](FOCUS_RECOVERY.md).

## Plánované miestne zálohy

Plánované miestne zálohy sú dostupné vo **v0.18.0**. Schéma SQLite zostáva **10**. Ručná záloha a obnova fungujú samostatne. [Plánované miestne zálohy](SCHEDULED_BACKUPS.md).
