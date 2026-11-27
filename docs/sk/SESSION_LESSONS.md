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

Stav 22. novembra 2026: používateľ potvrdil dokončenie testovania v0.15.0 a schválil PR #32. Tento zoznam teraz cieli na v0.18.1; jednotlivé výsledky čistého počítača/DPI tu nie sú zaznamenané. Nezaškrtnuté body zostávajú neoverené; pri testovaní nového vydania doplň dôkazy pre konkrétne zariadenie. [Ďalšie kroky · 22. novembra 2026](NEXT_STEPS.md).

## Revízia Dashboardu · 25. novembra 2026

Dashboard, krok 2, združuje študijné akcie, pod nimi predmety/hľadanie, kompaktný súhrn a výber sidebaru. Rozmery plochy a zalamovanie prevádzať z natívnych pixelov na logické CTk jednotky v adaptéri posúvania; medze overovať oproti skutočnej ploche. Simulované DPI nastaviť pred konštrukciou widgetov v nových procesoch: živá zmena CTk 5.2.2 môže znovu zobraziť skryté stránky. Revízia bez blokujúcich nálezov; 308 unit testov (dva preskočené), všetkých 18 GUI skriptov v kontajneri vrátane štyroch jazykov a obnovy/opakovania pri počiatočnej mierke 100/150 %. Natívne/živé DPI overenie je oddelené.

## Revízia redizajnu testov · 25. novembra 2026

CTkFrame.bind odovzdáva Configure na canvas: lokálnu zmenu veľkosti neodmietať porovnaním event.widget s obalom. Pred zalamovaním previesť pixely na logické jednotky. Výber odpovede kresliť z uloženého snímku, po chybe obnoviť; riadok/text/radio chrániť aktuálnou stránkou aj viditeľnosťou testu. Kontrast radia overiť oproti vybranému pozadiu. Testovať skutočné kresliace/textové ciele udalostí, nielen priame volania. Priebeh počíta uložené odpovede, nie správnosť.

## 2026-11-25 · Flashcard retry

Rozlišuj chybu zápisu hodnotenia od chyby následného čítania. Pri chybe zápisu zachovaj odhalenú odpoveď; po úspešnom zápise vypni staré hodnotenia a opakuj iba čítanie ďalšej kartičky. Správu o opakovaní zobraz pri hodnotení dlhej odpovede a použi preložené názvy akcií.

## 2026-11-25 · Responzívne prehľady a Tutor

Popisy v rovnako širokých stĺpcoch zalamuj podľa stabilnej šírky spoločného kontajnera. Šírka jednotlivých zaokrúhlených kariet môže pri zmene veľkosti spôsobiť slučku o jeden pixel. Rozloženie meň len pri prepnutí počtu stĺpcov a varovania zobraz pri potvrdzovacích tlačidlách.

## 2026-11-26 · Mačacia značka, AI generovanie a hodnotenie so skutočným modelom (v0.29.0–v0.30.1)

- **Paleta značky a kontrast.** Značková levanduľová `#9884D6` dáva bielemu textu len asi 3,2:1. Tlačidlá používajú tmavšiu `#6E5ABF`, značková farba zostáva pre obrysy. Každý dekoratívny obrázkový štítok potrebuje čitateľné `text_color`, pretože živý audit kontroluje všetky namapované štítky.
- **Kompaktné rozloženie má málo zvislej rezervy.** Kontrola viditeľnosti Finish v 1024 × 700 zlyhala po pridaní obrázka bannera. Dekoratívne scény sa zobrazujú len v širokom rozložení a obrázok bočného panela sa umiestni do mriežky, len keď sa jeho vážený riadok zmestí celý.
- **Náklady na štart sú testované obmedzenie.** Rozloženia v čerstvom procese majú v CI limit 7 sekúnd. Dva ďalšie panely vytvárané pri štarte tento limit prekročili. Voliteľné panely, napríklad panely AI generovania, vytváraj až pri prvom použití.
- **Test so skutočným modelom odhalí, čo fixtúry nezachytia.** Model so 4 miliardami parametrov označil zlé písmeno odpovede pri 3 z 22 otázok a riadil sa pokynmi vloženými do poznámok. Nikdy nenechaj model vyberať písmeno odpovede. Poznámky ohraničuj ako dáta a úlohu zopakuj až za nimi. Návrhy so slabou oporou zobraz nezaškrtnuté, neodmietaj ich. Po každej zmene promptu alebo schémy znova spusti `tools/evaluate_ai.py`.
- **Behy v kontajneri potrebujú `--init`.** Bez neho sa `xvfb-run` zasekne skôr, než kontrola začne. Spustenie jedného skriptu ohraničuj pomocou `timeout`.
- **Súbežné volania nástrojov.** Volania v jednom kroku bežia v nezaručenom poradí, preto nikdy nevykonávaj zostavenie a úpravu v jednom kroku a nespoliehaj sa na výsledok. Po vykonaní úpravy kontrolu zopakuj.
