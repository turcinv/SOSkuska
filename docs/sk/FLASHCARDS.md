# Kartičky a opakovanie (nevydané)

V bočnej ponuke otvor **Flashcards**. New deck vytvorí balíček pre existujúci predmet; názov musí byť jedinečný medzi všetkými balíčkami. Predmet balíčka sa potom nemení, názov a popis áno. Open deck umožní pridať a upravovať kartičky. Predná strana má 1–2000 znakov, zadná 1–4000; Search hľadá v oboch stranách. Zoznam zobrazuje najviac 100 výsledkov, ďalšie nájdeš užším hľadaním.

**Study due** otvorí najviac 100 práve splatných kartičiek, od najstaršieho termínu. Najprv sa zobrazí predná strana. Reveal answer ukáže odpoveď a sprístupní Again / Hard / Good / Easy. Hodnotenie je vlastné posúdenie vybavenia odpovede, nie meranie správnosti alebo zvládnutia učiva. Po každom hodnotení sa súčasne uloží historický záznam a ďalší termín. Neohodnotená kartička zostane splatná; po reštarte môžeš začať ďalšiu dávku. Refresh obnoví počty a splatnosť; zoznam sa na pozadí sám neprestavuje.

## Pravidlá termínov

Ide o jednoduché vlastné pravidlá, nie implementáciu SM-2 alebo FSRS.

| Hodnotenie | Nová / učiaca sa kartička (interval 0) | Kartička s intervalom aspoň 1 deň |
| --- | --- | --- |
| Again | O 10 minút, interval sa nastaví na 0 | O 10 minút, interval sa nastaví na 0 |
| Hard | O 1 hodinu, interval zostáva 0 | Predchádzajúci počet dní × 1,2, zaokrúhlené nahor |
| Good | O 1 deň | Predchádzajúci počet dní × 2,5, zaokrúhlené nahor |
| Easy | O 4 dni | Predchádzajúci počet dní × 3,5, zaokrúhlené nahor |

Maximum je 365 dní. Termíny sú UTC; v aplikácii sa zobrazujú v miestnom čase. Zmena systémových hodín môže ovplyvniť splatnosť. Úprava obsahu kartičky obnoví splatnosť na teraz a interval na 0; minulé hodnotenia zostanú zachované.

## História a mazanie

Review history zobrazuje posledných 20 hodnotení s kópiami oboch strán, názvu balíčka, predmetu a termínov. Staršie riadky zostávajú uložené. Vymazanie predmetu ponechá jeho balíčky a kartičky s pôvodným názvom predmetu. Vymazanie kartičky alebo balíčka vyžaduje potvrdenie a ponechá históriu hodnotení. Zmenený počet kartičiek alebo názov balíčka vyžaduje nové potvrdenie vymazania. Zastaraná úprava alebo hodnotenie kartičky sa odmietne namiesto prepísania novšej verzie. Pri chybe zápisu sa obsah formulára a odhalená odpoveď zachovajú na opakovanie.

Táto funkcia je zatiaľ nevydaná a nie je súčasťou vydanej v0.4.1. Import, prevod z otázok, AI a súhrnná štatistická obrazovka zostávajú plánované.
