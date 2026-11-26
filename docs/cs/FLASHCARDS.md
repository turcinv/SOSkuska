# Kartičky a opakování (v0.5.0)

[English](../FLASHCARDS.md) · [Čeština](FLASHCARDS.md) · [Slovenčina](../sk/FLASHCARDS.md) · [Русский](../ru/FLASHCARDS.md)

## v0.21.0 — nový vzhled opakování kartiček

Opakování kartiček nyní odděluje otázku a odhalenou odpověď do čtecích ploch. Hlavní akcí je odhalení odpovědi; poté ji na stejném místě nahradí hodnocení Again / Hard / Good / Easy, ve čtyřech sloupcích v širokém okně nebo ve dvou v kompaktním. Dlouhý text se zalamuje a k hodnocení lze posunout stránku. Akce balíčku a prázdné stavy používají společné rozvržení. Selhání zápisu zachová odhalenou odpověď pro opakování. Když se hodnocení uloží, ale načtení další kartičky selže, stará hodnocení se vypnou a Obnovit kartičku pouze znovu načte další kartičku; uložené hodnocení se neopakuje. Plánování, historie, rozepsané úpravy a náhled CSV zůstávají zachovány. Vydaná verze zůstává v0.30.0, schéma 10.

V postranní nabídce otevři **Flashcards**. New deck vytvoří balíček pro existující předmět; název musí být jedinečný mezi všemi balíčky. Předmět balíčku se potom nemění, název a popis ano. Open deck umožní přidat a upravovat kartičky. Přední strana má 1–2000 znaků, zadní 1–4000; Search hledá v obou stranách. Seznam zobrazuje nejvýše 100 výsledků, další najdeš užším hledáním.

**Study due** otevře nejvýše 100 právě splatných kartiček, od nejstaršího termínu. Nejprve se zobrazí přední strana. Reveal answer ukáže odpověď a zpřístupní Again / Hard / Good / Easy. Hodnocení je vlastní posouzení vybavení odpovědi, nikoli měření správnosti nebo zvládnutí učiva. Po každém hodnocení se současně uloží historický záznam a další termín. Neohodnocená kartička zůstane splatná; po restartu můžeš začít další dávku. Refresh obnoví počty a splatnost; seznam se na pozadí sám nepřestavuje.

## Pravidla termínů

Jde o jednoduchá vlastní pravidla, nikoli implementaci SM-2 nebo FSRS.

| Hodnocení | Nová / učící se kartička (interval 0) | Kartička s intervalem alespoň 1 den |
| --- | --- | --- |
| Again | Za 10 minut, interval se nastaví na 0 | Za 10 minut, interval se nastaví na 0 |
| Hard | Za 1 hodinu, interval zůstává 0 | Předchozí počet dní × 1,2, zaokrouhleno nahoru |
| Good | Za 1 den | Předchozí počet dní × 2,5, zaokrouhleno nahoru |
| Easy | Za 4 dny | Předchozí počet dní × 3,5, zaokrouhleno nahoru |

Maximum je 365 dní. Termíny jsou UTC; v aplikaci se zobrazují v místním čase. Změna systémových hodin může ovlivnit splatnost. Úprava obsahu kartičky obnoví splatnost na teď a interval na 0; minulá hodnocení zůstanou zachovaná.

## Historie a mazání

Review history zobrazuje posledních 20 hodnocení s kopiemi obou stran, názvu balíčku, předmětu a termínů. Starší řádky zůstávají uložené. Smazání předmětu ponechá jeho balíčky a kartičky s původním názvem předmětu. Smazání kartičky nebo balíčku vyžaduje potvrzení a ponechá historii hodnocení. Změněný počet kartiček nebo název balíčku vyžaduje nové potvrzení smazání. Zastaralá úprava nebo hodnocení kartičky se odmítne místo přepsání novější verze. Při chybě zápisu se obsah formuláře a odhalená odpověď zachovají pro opakování.

Funkce je dostupná od v0.5.0. Převod z otázek, propojení materiálů s AI zůstává plánované; souhrnný přehled je ve Statistics.

## Import kartiček z CSV

Flashcards nyní podporuje import UTF-8 CSV do existujícího balíčku: šablonu s hlavičkou, stránkovaný náhled, odmítnutí přesných duplicit a jedno atomické uložení. Maximum 2 MiB / 500 záznamů. Nové kartičky jsou ihned splatné; původní termíny a historie hodnocení zůstávají zachované. Aktuální schéma je 10. [Import kartiček z CSV](FLASHCARD_CSV_IMPORT.md).
