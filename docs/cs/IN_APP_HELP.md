# Nápověda v aplikaci

[English](../IN_APP_HELP.md) · [Čeština](IN_APP_HELP.md) · [Slovenčina](../sk/IN_APP_HELP.md) · [Русский](../ru/IN_APP_HELP.md)

SOSkúška má vestavěnou stránku Nápověda s krátkými návody ke všem částem aplikace. Funguje offline, nic neodesílá a nikdy nemění vaše data.

## Otevření nápovědy

- Zvolte tlačítko **?** vedle **Nastavení** dole na postranním panelu. Ve sbaleném panelu je pod ikonou Nastavení.
- Na libovolné stránce stiskněte **F1**. Na Macu funguje také **Cmd+?**.

Nápověda se otevře na tématu stránky, kterou jste právě používali: například z Kartiček ukáže *Kartičky a opakování*, z banky otázek *Banka otázek*. Když nápovědu otevřete znovu, zatímco ji čtete, zůstanete na stejném místě.

## Používání

- Vyberte téma ze seznamu. V širokém okně je seznam vedle článku, v menším okně nad ním.
- Psaním do **Hledat v nápovědě…** seznam zúžíte. Hledání nerozlišuje velká písmena ani diakritiku (`nastaveni` najde *Nastavení*) a v tématu se musí objevit každé zadané slovo. **Ctrl+K** (na Macu Cmd+K) přejde do pole hledání a **Esc** jej vymaže.
- Názvy tlačítek a polí jsou v uvozovkách přesně tak, jak se jmenují ve zvoleném jazyce rozhraní.
- **Otevřít: …** na konci tématu přejde na popisovanou stránku; **Viz také** odkazuje na související témata.

**← Zpět: …** nahoře vás vrátí na stránku, odkud jste přišli, přesně tak, jak jste ji opustili, na stejném místě posuvníku. Neuložené rozpracované texty zůstanou zachovány a při návratu touto cestou také náhled importu CSV a vybraná záloha; přechod z Nápovědy na jinou stránku je jako obvykle zruší.

## Témata

Začínáme · Přehled a soustředění · Předměty a data zkoušek · Banka otázek · Cvičné testy · Kartičky a opakování · Statistiky · AI Tutor · Návrhy AI z poznámek · Import z CSV · Nastavení a jazyk · Zálohy a obnova · Vaše data a soukromí · Klávesové zkratky · Řešení potíží.

Nápověda se po restartu řídí jazykem rozhraní zvoleným v Nastavení (angličtina, čeština, slovenština nebo ruština). Podrobnou referencí zůstávají návody ve složce `docs/`.

## Pro vývojáře

Témata jsou v `soskuska/i18n/help-<en|cs|sk|ru>.json`. `help_content.py` je ověřuje, připravuje text pro hledání a přiřazuje stránkám témata; `help_page.py` je vykresluje a vytváří se až při prvním použití, aby nezpomaloval start. Každé téma má `id`, `title`, `summary`, volitelnou `page` k otevření, `blocks` (`heading`, `text`, `steps` nebo `bullets`) a `related` s id souvisejících témat. Doslovné popisky rozhraní označte jako `**Popisek**`.

`tests/test_help.py` vyžaduje stejnou strukturu všech čtyř souborů, aby každý `**Popisek**` byl skutečným popiskem v katalogu rozhraní daného jazyka, a ověřuje hledání; `check_help.py` testuje stránku ve čtyřech jazycích a při 150 %. Při změně funkce nebo popisku upravte všechny čtyři soubory společně.
