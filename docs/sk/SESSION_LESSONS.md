# Poznatky zo sedenia a odovzdanie projektu

[English](../SESSION_LESSONS.md) · [Čeština](../cs/SESSION_LESSONS.md) · [Slovenčina](SESSION_LESSONS.md) · [Русский](../ru/SESSION_LESSONS.md)

Zapísané **20. novembra 2026**, po vydaní **v0.11.0 — Flashcard CSV import**. Ide o datované odovzdanie, nie živý stav. Pred novým tvrdením over Git, vydania, kód a CI.

## Projekt a pracovné preferencie

SOSkúška je natívny semestrálny projekt v Pythone/CustomTkinter/SQLite. Dodávaj zvládnuteľné týždenné funkcie a ponechaj čas na semestrálnu dokumentáciu. Aplikácia funguje offline; Ollama je voliteľná. Používateľ zvolil miestny vývoj kvôli platenému generovaniu návrhov. HTML v `soskuska-local/` je vizuálna referencia.

Konverzácia môže striedať češtinu, slovenčinu, angličtinu a ruštinu; odpovedaj v poslednom jazyku. UI zostáva anglické. Hlavná dokumentácia je anglicky a preklady sú oddelené. Interné pokyny pre agentov zostávajú anglicky.

## Postup vývoja a vydania

1. Nová vetva z aktuálneho main; implementuj požadovaný krok plánu. Nikdy necommituj ani nepushuj priamo do main.
2. Používaj dočasné údaje, vykonaj príslušné kontroly a pre implementáciu funkcií vyžiadaj nezávislú kontrolu **Sol so stredným úsilím**. Nálezy oprav v rovnakej vetve a opravy nechaj znovu skontrolovať.
3. Otvor PR, opíš skutočné overenie a skontroluj CI. Chyby oprav bez oslabovania kontrol. Zelené CI samo nepovoľuje zlúčenie.
4. Zlučuj až po súhlase používateľa. Požiadavka zlúčiť a vydať zahŕňa potrebné PR na označenie verzie a publikovanie. Pred označením presného zlúčeného commitu zjednoť pätu, štyri README, nadpisy changelogov a stav architektúry.
5. Over vydanie a čistý main synchronizovaný s GitHubom. Ďalšia funkcia, zlúčenie, vydanie či čistenie vetiev nie sú automaticky povolené predchádzajúcou prácou.

## Poznatky na zachovanie

- **Oddeľ zápis od opakovania čítania.** Po úspešnom uložení zneplatni dávku pred načítaním súčtov. Chyba obnovy nesmie opakovať import. Neznámy výsledok procesu už mohol byť uložený; najprv over údaje.
- **Náhľad musí byť stabilný.** Uchovaj súkromnú dávku; zmeny CSV vyžadujú nový výber. Cieľ/názov a duplicity over znovu pod zámkom zápisu a ulož všetko jednou transakciou.
- **Pre CSV/zálohy používaj procesy.** Uvoľňovanie objektov vo vlákne Pythonu predtým zrušilo objekty Tk a zhodilo macOS aplikáciu. Tk patrí do hlavného vlákna. Výstup procesu smeruj do dočasného súboru; nečítané rúry sa na Windows môžu zablokovať.
- **Náhľad iba na čítanie.** Existujúcu databázu neotváraj s vytváraním či migráciou. Použi už zobrazený cieľ; synchrónny dotaz pri výbere súboru môže pod databázovým zámkom zablokovať Tk.
- **Zachovaj rozpísaný text.** Prekreslenie môže stratiť nepotvrdené hľadanie či formulár. Uchovaj ho oddelene od použitého filtra a over navigáciu aj obnovu po uložení.
- **Kontroluj aj drobnosti UI.** Čakacia správa patrí aktívnemu importu. Test duplicity za limitom zoznamu musí naozaj vytvoriť dosť záznamov.
- **Presne opisuj platformové overenie.** macOS a Linux/Xvfb neoverujú ručné UI na Windows ani fyzický trackpad. Na pripravenom Macu používaj `.venv-macos`; Apple Tk 8.5 v `.venv-desktop` vykreslil prázdne okno.

## Overený stav pri odovzdaní

- Vydanie **v0.11.0**, commit `b5acbdcc47310b1fab0ba9fb4b24dbac0db041ce`; implementácia **#19**, zjednotenie verzie **#20**.
- **202 jednotkových testov** a **12 natívnych GUI skriptov** prešlo lokálne na macOS. Štyri CI úlohy funkcie prešli: testy Linux/Windows/macOS a GUI Ubuntu/Xvfb. Označenie vydania malo cielenú kontrolu verzií, syntaxe a dokumentácie.
- Schéma **6**. Import otázok aj kartičiek z CSV existuje. Kartičky: UTF-8/BOM, čiarky, presne `front,back`, najviac **2 MiB / 500 záznamov**, odmietnutie presných duplicít a atomické uloženie do existujúceho balíčka. Nové kartičky sú ihneď splatné; pôvodné termíny a história sa nemenia.

## Úsporný kontext pre ďalšie sedenia

Koreňový `AGENTS.md` slúži ako stručný rozcestník. Pred úpravou oblasti načítaj požadované súbory `@docs/agents/...`; ostatné pravidlá načítaj podľa potreby. Ide o výslovné pokyny na čítanie súborov, nie prísľub automatického vloženia. Oficiálny [návod Codex k AGENTS.md](https://developers.openai.com/codex/guides/agents-md) opisuje hierarchické načítanie pokynov; projekt preto výslovne požaduje otvorenie odkazovaných súborov.

Trvalé pravidlá patria do príslušného súboru pokynov, nové datované overenie sem a história vydaní do changelogu. Zmeny správania premietni do pravidiel a všetkých jazykov používateľskej dokumentácie.

## Ďalšie kroky · 22. novembra 2026

Stav 22. novembra 2026: používateľ potvrdil dokončenie testovania v0.15.0 a schválil PR #32. Tento zoznam teraz cieli na v0.18.0; jednotlivé výsledky čistého počítača/DPI tu nie sú zaznamenané. Nezaškrtnuté body zostávajú neoverené; pri testovaní nového vydania doplň dôkazy pre konkrétne zariadenie. [Ďalšie kroky · 22. novembra 2026](NEXT_STEPS.md).
