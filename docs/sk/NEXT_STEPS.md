# Ďalšie kroky · 25. novembra 2026

[English](../NEXT_STEPS.md) · [Čeština](../cs/NEXT_STEPS.md) · [Slovenčina](NEXT_STEPS.md) · [Русский](../ru/NEXT_STEPS.md)

Aktuálne vydanie: **v0.19.0**, schéma **10**. Kroky dizajnu 1–2 sú implementované cez PR #43 a #44: spoločný vzhľad a Dashboard/sidebar. Štyri staršie nálezy Astra zostávajú vyriešené. Toto vydanie nepotvrdzuje akceptáciu v1.0.0.

1. **Ďalšia implementácia: krok 3, Practice Tests.** Použiť [plán dizajnu](../agents/BRIGHT_UI_REDESIGN.md) a [odovzdanie kroku 2](../agents/design/bright-ui-step2/README.md). Nová vetva, zachovať odpovede/termíny/históriu, príslušné kontroly v kontajneri a nezávislá revízia Sol na medium. Nerobiť všetky zostávajúce kroky naraz. Nová práca, zlúčenie aj vydanie potrebujú vlastné schválenie.
2. **Po redizajne zopakovať skutočnú akceptáciu.** Použiť aktuálny [Windows balíček](WINDOWS_PORTABLE.md) a [ručný zoznam](WINDOWS_ACCEPTANCE.md), dočasné dáta a zapísať OS/build, hardvér, rozlíšenie/mierku, verziu/súčet a výsledky. Kontroly počiatočnej mierky 100/150 % v kontajneri nie sú natívny Windows ani zmena DPI počas behu. Obmedzenie živého škálovania CTk zostáva v odovzdaní.
3. **Overiť skutočný model Ollama.** Zapísať verzie modelu/servera, hardvér, adresu bez prihlasovacích údajov, dátum a výsledky Connect/stream/Stop/opätovného pripojenia/uloženého chatu. So zastaveným serverom overiť offline štúdium. Falošný server CI nepreukazuje kvalitu ani výkon skutočného modelu.
4. **Samostatne dokončiť prácu a prezentáciu.** Osobné údaje, predmet, jazyk a termín ponechať ako zástupné polia do dodania. Doplniť skutočné snímky, zdroje a výsledky; aktualizovať generované polia a prezrieť konečné stránkovanie. Riadiť sa zadaním; úspech testov aplikácie neurčuje termín ani splnenie odovzdania.

Pred v1.0.0 dokončiť akceptáciu, opraviť nálezy cez revidované PR, zopakovať kontroly a vydať len so súhlasom používateľa. Táto aktualizácia neoznačuje ručné položky ako úspešné. Historické potvrdenie v0.15.0 neoveruje redizajn.
