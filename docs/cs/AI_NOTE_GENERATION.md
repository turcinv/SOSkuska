# Generování kartiček a otázek z poznámek

[English](../AI_NOTE_GENERATION.md) · [Čeština](AI_NOTE_GENERATION.md) · [Slovenčina](../sk/AI_NOTE_GENERATION.md) · [Русский](../ru/AI_NOTE_GENERATION.md)

SOSkúška umí z vložených studijních poznámek vytvořit návrhy kartiček nebo otázek s výběrem z odpovědí pomocí vašeho volitelného místního serveru Ollama. Každý návrh před uložením zkontrolujete vy. Běžné studium AI nikdy nevyžaduje.

## Než začnete

1. Nainstalujte a spusťte [Ollamu](https://ollama.com) a stáhněte model, například `ollama pull llama3.2:3b`. Strukturovaný výstup vyžaduje Ollamu verze 0.5 nebo novější.
2. V **AI Tutor** se připojte a vyberte model, poté v Nastavení zvolte **Použít volby Tutor** a **Uložit nastavení**. Adresu serveru a preferovaný model můžete zadat i přímo v **Nastavení → AI**.

Generátor vždy používá **uložený** server a preferovaný model zobrazené ve svém panelu. Nikdy se nepřipojuje sám od sebe a nikdy nepoužívá záložní cloud.

## Jak na to

- **Kartičky:** otevřete balíček a zvolte **Generovat pomocí AI**.
- **Otázky:** otevřete banku otázek předmětu a zvolte **Generovat pomocí AI**.

Vložte poznámky (nejvýše 12 000 znaků), zvolte, kolik položek chcete (3, 5, 10, 15 nebo 20), a stiskněte **Generovat**. Teprve potom se vaše poznámky odešlou na server zobrazený v panelu. Kdykoli můžete stisknout **Zastavit**, nebo se během generování věnovat studiu na jiných stránkách.

Po dokončení se každý návrh zobrazí s políčkem. U otázek vidíte všechny čtyři možnosti se zvýrazněnou správnou odpovědí, obtížnost, případné téma a vysvětlení; model dodá správnou odpověď jako text a písmeno jí přidělí SOSkúška, takže označená odpověď vždy odpovídá vysvětlení. Zrušte zaškrtnutí u všeho, co je chybné nebo nechtěné, a stiskněte **Uložit vybrané**. Položky, které porušují obvyklá pravidla (prázdný text, duplicitní možnosti, příliš dlouhý text), a opakované kopie se vypíší a automaticky přeskočí. Návrh, jehož odpověď nebyla v poznámkách jasně nalezena, je označen **⚠** a není zaškrtnutý; zaškrtněte ho až po kontrole.

## Co se ukládá

- Vybrané položky se uloží najednou v jednom kroku podle stejných pravidel jako import CSV. Pokud některá vybraná položka už v balíčku nebo předmětu existuje, nebo byl balíček či předmět přejmenován nebo smazán, neuloží se nic a problém se vypíše. Zrušte zaškrtnutí vypsaných položek, nebo cíl znovu otevřete, a uložte znovu.
- Nové kartičky jsou k opakování hned. Témata otázek se vytvoří podle potřeby. Stávající kartičky, otázky, plány opakování ani historie se nikdy nemění.
- Vaše poznámky se neukládají do databáze. Zůstávají v panelu, dokud je otevřený pro stejný balíček nebo předmět, i po uložení. Otevřením jiného balíčku nebo předmětu se neuložené návrhy zahodí; zahodí se také po **Zastavit**, **Zavřít** nebo novém **Generovat**.

## Omezení a přesnost

Návrhy od AI mohou být chybné, neúplné nebo nepodložené vašimi poznámkami, přestože model dostane pokyn použít jen je. Před uložením si přečtěte každou položku. Menší modely dodržují strukturu méně spolehlivě; pokud se zobrazí „did not return valid JSON", zkuste to znovu nebo zvolte jiný model. Požadavky vyprší po 5 minutách; dlouhé poznámky nebo 20 otázek trvají na pomalých počítačích déle. Změna nastavení AI a obnovení zálohy počkají, dokud generování neskončí nebo se nezastaví.

Automatické kontroly používají místní testovací server. První vyhodnocení se skutečným modelem proběhlo 26. listopadu 2026 s modelem `qwen3:4b-instruct-2507-q4_K_M` a krátkými poznámkami v angličtině, češtině, slovenštině a ruštině. Ve všech případech vytvořil platné návrhy a na počítači Mac s Apple Silicon trval jeden požadavek asi 8–35 sekund. Slabé nesprávné možnosti se stále vyskytují, proto je kontrola každého návrhu nutná. Jiné modely, dlouhé poznámky a pomalejší hardware vyhodnoceny nebyly.
