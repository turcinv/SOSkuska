# Historie změn

[Slovenčina](docs/sk/CHANGELOG.md) · [Русский](docs/ru/CHANGELOG.md)

## Unreleased

- Správa předmětů a termínů zkoušek, prázdný stav, validace Unicode a historie při smazání.
- Skutečné metriky Dashboardu a propojení časovače s předmětem; odstranění ukázkových statistik.
- Transakční migrace SQLite na verzi 2 se zachováním původních dat; 16 testů a rozšířená nativní kontrola.

- Návod ke klonování, autentizaci, větvím, commitům, aktualizacím a pull requestům.
- Pokyny k přispívání, šablony chyb/návrhů a pull requestu, nastavení editoru.

## 0.1.0 — 2026-11-10

Počáteční prototyp; označení verze, nikoli oznámení vydaného instalátoru nebo GitHub release.

- Dashboard SOSkúška v Pythonu/CustomTkinteru, resizable okno a sbalitelná navigace.
- Vyhledávání předmětů, denní checklist a 15minutový časovač; ukládání do SQLite.
- Posouvání včetně Tk 9 trackpadu a kompatibilita s databází původní aplikace ExamPrep.
- Automatické kontroly úložiště a nativní kontrolní skript; prověřeno na macOS, Windows/Linux zatím neověřené.
- Česká, slovenská a ruská dokumentace včetně návodu Windows od nuly; anglický AGENTS.md.
- Soukromý repozitář `turcinv/SOSkuska`. Vzorové metriky a ostatní obrazovky zůstávají ve stavu popsaném v dokumentaci.
