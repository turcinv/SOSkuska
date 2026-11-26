# Jazyk rozhraní

[English](../UI_LANGUAGES.md) · [Čeština](UI_LANGUAGES.md) · [Slovenčina](../sk/UI_LANGUAGES.md) · [Русский](../ru/UI_LANGUAGES.md)

Vyber **Settings → Interface language (applies after restart)**: English, Čeština, Slovenčina nebo Русский. Ulož nastavení, dokonči či ulož práci, běžně zavři SOSkúška a spusť ji znovu. Jazyk se použije při startu. Uložení nepřestaví obrazovky, nezahodí formuláře a nepřeruší studium ani AI. Bez uložení zůstává volba rozepsanou změnou; ostatní otevřená okna se nepřepínají.

Jazyk rozhraní a odpovědí AI jsou nezávislé. Můžeš mít české rozhraní a ruské odpovědi Ollamy. Uložení se nepřipojuje k Ollamě. Starší instalace začnou anglicky. Volba patří vybrané místní databázi a je součástí záloh.

Navigace, formuláře, tlačítka, stavové zprávy, potvrzení, hlavičky náhledů a výběry mají anglický, český, slovenský a ruský katalog. Výběry ukazují přeložené popisky, ale zachovávají původní hodnoty pro filtrování, skórování, plánování, modely a databázi. Názvy jazyků jsou vlastními jmény. Neznámé chyby systému/serveru zůstávají v původním znění. Systémová tlačítka dialogů souborů používají jazyk systému; názvy dialogů a typů souborů z aplikace jsou přeložené.

Názvy předmětů/témat/balíčků, otázky, odpovědi, vysvětlení, obsah chatů, identifikátory modelů, URL, cesty, CSV hlavičky a uložená ISO data se nepřekládají. Přehled používá mimo angličtinu číselné datum. Jazyk procesu se globálně nemění. Tlačítka se rozšíří podle textu; minimum zůstává 1024 × 700 a spodní obsah je dostupný posouváním.

Schéma **8** přidává `preferences.ui_language` s anglickou výchozí hodnotou. Migrace zachová obsah, historii chatů, jazyk AI a revize nastavení. Uložení zůstává výslovné, atomické a chráněné před starým formulářem. Obnova přijímá samostatné zálohy schématu 10; starší originál uchovej, samostatnou kopii otevři novou aplikací přes `--data` pro migraci a vyexportuj novou zálohu. Viz [Záloha a obnova](BACKUP_RESTORE.md).

Průvodci používají anglické UI popisky jako společný odkaz. Aplikace při jiném jazyce ukazuje odpovídající překlady.
