# Obnova sústredenia po páde

[English](../FOCUS_RECOVERY.md) · [Čeština](../cs/FOCUS_RECOVERY.md) · [Slovenčina](FOCUS_RECOVERY.md) · [Русский](../ru/FOCUS_RECOVERY.md)

v0.17.0 pridáva obnovu sústredenia po páde so schémou **10**. Pred otvorením pôvodných dát vytvor zálohu: migrácia je transakčná, ale v0.16.0 databázu schémy 10 neotvorí.

Start Studying najprv vytvorí rozpracovaný záznam. Aplikácia ukladá celé uplynuté sekundy približne každých päť sekúnd a ihneď pri Pause. Zachová pôvodný názov predmetu, cieľ a overený čas; hodnotu monotónnych hodín medzi procesmi neprenáša.

Po páde alebo vynútenom ukončení Dashboard ponúkne Recover paused, Discard checkpoint a Refresh (popisky sa prekladajú podľa jazyka rozhrania). Obnova začína pozastavená, zachová pôvodný cieľ aj po zmene Settings a nepočíta čas zatvorenia ako štúdium. Resume pokračuje; Finish uloží čas. Rozpracovaný čas nie je v Statistics. Zahodenie vyžaduje druhé potvrdenie a nepridáva históriu. Navigácia, Escape, Refresh a Recover potvrdenie rušia. Chyba čítania vypne zastarané akcie do úspešného Refresh.

Trvalý súbor `.focus.lock` dovolí vlastníctvo jedinému oknu. Iné okno môže kontrolný bod zobraziť, ale počas behu vlastníka ho neobnoví ani nezahodí. Po zatvorení vlastníka použi Refresh. Zámky nemaž ručne; ukončenie procesu uvoľní zámok operačného systému.

Zápis čaká na SQLite približne najviac 200 ms. Neúspešný kontrolný bod alebo Finish pozastaví čas, vypne Resume a ponechá čas v pamäti. Opakuj uloženie cez Finish. Pokyn je pri časovači a v bočnom paneli sa na ostatných stránkach ukáže Focus needs saving; otvorí Dashboard. Neúspešné zatvorenie ponechá Dashboard otvorený. Bežné zatvorenie čas uloží; pri chybe ukladania aplikáciu neukončuj násilne.

Dokončenie vloží študijnú reláciu a označí kontrolný bod v jednej transakcii; opakovanie nevytvorí druhú reláciu. Nula sekúnd nepridá štatistiku. Čas patrí miestnemu dňu dokončenia, aj po obnove; cez polnoc sa nedelí. Premenovanie/vymazanie predmetu zachová pôvodný historický názov; vymazanie odstráni len živý odkaz.

Záloha obsahuje uložené rozpracované, dokončené aj zahodené záznamy, nie čas od posledného zápisu a neuložené koncepty. Pred obnovou vyrieš rozpracované sústredenie cieľovej databázy. Záloha schémy 10 s rozpracovaným záznamom ponúkne obnovenie po spustení. Obnova prijíma len samostatné zálohy schémy 10; staré zálohy nemigruje. Staršiu databázu najprv otvor ako samostatnú kópiu v tejto verzii a vytvor novú zálohu.

Násilné ukončenie môže stratiť približne posledných päť sekúnd a zlomok sekundy; oneskorená slučka alebo chyba zápisu môžu stratu zväčšiť. Nejde o záruku pri výpadku prúdu, synchronizáciu ani priebežnú zálohu.

Použi [vývojové prostredie](DEVELOPMENT.md), oddelené dáta `--data .local-data/dev.sqlite3` a [kontajnerové kontroly](CONTAINER_TESTS.md). `tests/test_focus.py` overuje migráciu, návrat pri chybe, vlastníctvo, smrť procesu, atomické dokončenie a zálohy. `check_focus_recovery.py` ukončí testovacie GUI a v nových procesoch overí obnovu, chyby, potvrdenia a zatvorenie. Windows CI otvára prenosný program s kontrolným bodom. Linux/Xvfb nenahrádza natívny macOS ani ručnú kontrolu hardvéru Windows.
