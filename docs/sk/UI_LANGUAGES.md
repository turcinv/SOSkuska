# Jazyk rozhrania

[English](../UI_LANGUAGES.md) · [Čeština](../cs/UI_LANGUAGES.md) · [Slovenčina](UI_LANGUAGES.md) · [Русский](../ru/UI_LANGUAGES.md)

Vyber **Settings → Interface language (applies after restart)**: English, Čeština, Slovenčina alebo Русский. Ulož nastavenia, dokonči či ulož prácu, bežne zatvor SOSkúška a spusti ju znova. Jazyk sa použije pri štarte. Uloženie neprestaví obrazovky, nezahodí formuláre a nepreruší štúdium ani AI. Bez uloženia zostáva voľba rozpísanou zmenou; ostatné otvorené okná sa neprepínajú.

Jazyk rozhrania a odpovedí AI sú nezávislé. Môžeš mať slovenské rozhranie a ruské odpovede Ollamy. Uloženie sa nepripája k Ollame. Staršie inštalácie začnú anglicky. Voľba patrí vybranej miestnej databáze a je súčasťou záloh.

Navigácia, formuláre, tlačidlá, stavové správy, potvrdenia, hlavičky náhľadov a výbery majú anglický, český, slovenský a ruský katalóg. Výbery ukazujú preložené popisy, ale zachovávajú pôvodné hodnoty na filtrovanie, skórovanie, plánovanie, modely a databázu. Názvy jazykov sú vlastnými menami. Neznáme chyby systému/servera zostávajú v pôvodnom znení. Systémové tlačidlá dialógov súborov používajú jazyk systému; názvy dialógov a typov súborov z aplikácie sú preložené.

Názvy predmetov/tém/balíčkov, otázky, odpovede, vysvetlenia, obsah chatov, identifikátory modelov, URL, cesty, CSV hlavičky a uložené ISO dátumy sa neprekladajú. Prehľad používa mimo angličtiny číselný dátum. Jazyk procesu sa globálne nemení. Tlačidlá sa rozšíria podľa textu; minimum zostáva 1024 × 700 a spodný obsah je dostupný posúvaním.

Schéma **8** pridáva `preferences.ui_language` s anglickou predvolenou hodnotou. Migrácia zachová obsah, históriu chatov, jazyk AI a revízie nastavení. Uloženie zostáva výslovné, atomické a chránené pred starým formulárom. Obnova prijíma samostatné zálohy schémy 10; starší originál uchovaj, samostatnú kópiu otvor novou aplikáciou cez `--data` na migráciu a vyexportuj novú zálohu. Pozri [Záloha a obnova](BACKUP_RESTORE.md).

Sprievodcovia používajú anglické UI popisy ako spoločný odkaz. Aplikácia pri inom jazyku ukazuje zodpovedajúce preklady.
