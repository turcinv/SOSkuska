# Generovanie kartičiek a otázok z poznámok

[English](../AI_NOTE_GENERATION.md) · [Čeština](../cs/AI_NOTE_GENERATION.md) · [Slovenčina](AI_NOTE_GENERATION.md) · [Русский](../ru/AI_NOTE_GENERATION.md)

SOSkúška vie z vložených študijných poznámok vytvoriť návrhy kartičiek alebo otázok s výberom z odpovedí pomocou vášho voliteľného miestneho servera Ollama. Každý návrh pred uložením skontrolujete vy. Bežné štúdium AI nikdy nevyžaduje.

## Skôr než začnete

1. Nainštalujte a spustite [Ollamu](https://ollama.com) a stiahnite model, napríklad `ollama pull llama3.2:3b`. Štruktúrovaný výstup vyžaduje Ollamu verzie 0.5 alebo novšiu.
2. V **AI Tutor** sa pripojte a vyberte model, potom v Nastaveniach zvoľte **Použiť voľby Tutor** a **Uložiť nastavenia**. Adresu servera a preferovaný model môžete zadať aj priamo v **Nastavenia → AI**.

Generátor vždy používa **uložený** server a preferovaný model zobrazené vo svojom paneli. Nikdy sa nepripája sám od seba a nikdy nepoužíva záložný cloud.

## Ako na to

- **Kartičky:** otvorte balíček a zvoľte **Generovať pomocou AI**.
- **Otázky:** otvorte banku otázok predmetu a zvoľte **Generovať pomocou AI**.

Vložte poznámky (najviac 12 000 znakov), zvoľte, koľko položiek chcete (3, 5, 10, 15 alebo 20), a stlačte **Generovať**. Až potom sa vaše poznámky odošlú na server zobrazený v paneli. Kedykoľvek môžete stlačiť **Zastaviť**, alebo sa počas generovania venovať štúdiu na iných stránkach.

Po dokončení sa každý návrh zobrazí s políčkom. Pri otázkach vidíte všetky štyri možnosti so zvýraznenou správnou odpoveďou, náročnosť, prípadnú tému a vysvetlenie; model dodá správnu odpoveď ako text a písmeno jej pridelí SOSkúška, takže označená odpoveď vždy zodpovedá vysvetleniu. Zrušte začiarknutie pri všetkom, čo je chybné alebo nechcené, a stlačte **Uložiť vybrané**. Položky, ktoré porušujú obvyklé pravidlá (prázdny text, duplicitné možnosti, príliš dlhý text), a opakované kópie sa vypíšu a automaticky preskočia. Návrh, ktorého odpoveď sa v poznámkach jasne nenašla, je označený **⚠** a nie je začiarknutý; začiarknite ho až po kontrole.

## Čo sa ukladá

- Vybrané položky sa uložia naraz v jednom kroku podľa rovnakých pravidiel ako import CSV. Ak niektorá vybraná položka už v balíčku alebo predmete existuje, alebo bol balíček či predmet premenovaný alebo zmazaný, neuloží sa nič a problém sa vypíše. Zrušte začiarknutie vypísaných položiek, alebo cieľ znova otvorte, a uložte znova.
- Nové kartičky sú na opakovanie hneď. Témy otázok sa vytvoria podľa potreby. Existujúce kartičky, otázky, plány opakovania ani história sa nikdy nemenia.
- Vaše poznámky sa neukladajú do databázy. Zostávajú v paneli, kým je otvorený pre ten istý balíček alebo predmet, aj po uložení. Otvorením iného balíčka alebo predmetu sa neuložené návrhy zahodia; zahodia sa aj po **Zastaviť**, **Zavrieť** alebo novom **Generovať**.

## Obmedzenia a presnosť

Návrhy od AI môžu byť chybné, neúplné alebo nepodložené vašimi poznámkami, hoci model dostane pokyn použiť len ich. Pred uložením si prečítajte každú položku. Menšie modely dodržiavajú štruktúru menej spoľahlivo; ak sa zobrazí „did not return valid JSON", skúste to znova alebo zvoľte iný model. Požiadavky vypršia po 5 minútach; dlhé poznámky alebo 20 otázok trvajú na pomalých počítačoch dlhšie. Zmena nastavení AI a obnovenie zálohy počkajú, kým generovanie neskončí alebo sa nezastaví.

Automatické kontroly používajú miestny testovací server. Prvé vyhodnotenie so skutočným modelom prebehlo 26. novembra 2026 s modelom `qwen3:4b-instruct-2507-q4_K_M` a krátkymi poznámkami v angličtine, češtine, slovenčine a ruštine. Vo všetkých prípadoch vytvoril platné návrhy a na počítači Mac s Apple Silicon trvala jedna požiadavka asi 8–35 sekúnd. Slabé nesprávne možnosti sa stále vyskytujú, preto je kontrola každého návrhu nutná. Iné modely, dlhé poznámky a pomalší hardvér vyhodnotené neboli.
