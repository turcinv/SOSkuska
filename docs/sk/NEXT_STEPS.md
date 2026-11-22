# Ďalšie kroky · 22. novembra 2026

[English](../NEXT_STEPS.md) · [Čeština](../cs/NEXT_STEPS.md) · [Slovenčina](../sk/NEXT_STEPS.md) · [Русский](../ru/NEXT_STEPS.md)

Aktuálne vydanie: **v0.16.0**, schéma **9**, s uloženým Light/Dark/System. Používateľ 22. novembra potvrdil dokončenie testovania v0.15.0 a schválil zlúčenie vzhľadu; podmienka je splnená. Potvrdenie nenahrádza výsledky jednotlivých zariadení: podrobnosti čistého počítača, DPI a hardvéru neboli dodané. V dôkazoch projektu ich rozlišuj.

1. **Overiť nové vydanie.** Použiť dočasné dáta alebo kópiu zálohy. Na Windows overiť živé Light/Dark, koncepty, štyri jazyky, kompaktné okno a mierku. System overiť skutočnou zmenou OS na Windows/macOS; Linux zámerne používa Light. Exportovať a otvoriť zálohu schémy 9. Zachovať originály schémy 8, pretože v0.15.0 migrované dáta neotvorí. Zaznamenať [kontrolu Windows](WINDOWS_ACCEPTANCE.md).
2. **Otestovať reálny model Ollama.** Zapísať OS, hardvér, model/verziu, adresu servera a výsledky pripojenia, streamu, Stop, opätovného pripojenia a uloženého chatu. Študijné funkcie musia fungovať aj bez bežiaceho servera. CI s falošným serverom nedokladá kvalitu modelu ani výkon hardvéru. Reálna kontrola zatiaľ nie je zaznamenaná.
3. **Súbežne pripraviť semestrálne odovzdanie.** Popis implementácie, diagramy architektúry, snímky, dôkazy testov, obmedzenia a scenár ukážky. Rozlíšiť vydané správanie, potvrdenie používateľa, automatizáciu a neoverené ručné body. Pred odovzdaním vychádzať zo skutočných pokynov zadania; tento zoznam nedokladá ich splnenie.
4. **Navrhnutá ďalšia funkcia: obnova sústredenia po páde.** Navrhnúť trvalé kontrolné body a výslovnú voľbu pokračovať/zahodiť po prerušení procesu. Zachovať len overený uplynulý študijný čas; nepočítať zatvorenú aplikáciu ako štúdium. Uchovať bežné ukladanie/opakovanie pri zatvorení, dátumy aj históriu predmetu. Pred implementáciou určiť transakcie, súbežné okná a testy prerušenia. Ide o návrh čakajúci na súhlas, nie začatú implementáciu.

Chyby základu patria do samostatných opravných PR, prípadne opravného vydania. Funkcie majú vlastnú vetvu, kontajnerové GUI kontroly a nezávislú revíziu Sol so stredným úsilím. Zachovať štyri jazyky dokumentácie. Zlúčenie a vydanie len so súhlasom používateľa. Pre budúcu prácu sa automaticky nezavádza ďalšia trvalá podmienka testovania základu.
