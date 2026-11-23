# Akceptačné kroky pred v1.0.0

[English](../V1_RELEASE_PLAN.md) · [Čeština](../cs/V1_RELEASE_PLAN.md) · [Slovenčina](V1_RELEASE_PLAN.md) · [Русский](../ru/V1_RELEASE_PLAN.md)

Rozhodnutie z **23. novembra 2026**. Pred prípravou v1.0.0 overiť vydanú **v0.18.1**, schéma **10**. Základná implementácia pre súčasný semestrálny rozsah je hotová; ručné Windows kontroly a skutočný model zatiaľ nemajú dôkazy. Tento plán nepotvrdzuje úspech ani neschvaľuje zlúčenie/vydanie. Počas akceptácie pozastaviť nové funkcie. Práca a prezentácia môžu pokračovať samostatne a neblokujú vydanie aplikácie.

## 1 Získať Windows verziu

Na Windows x64 bez Pythonu stiahnuť `SOSkuska-windows-x64.zip` a `.sha256` z [v0.18.1](https://github.com/turcinv/SOSkuska/releases/tag/v0.18.1); je potrebný prístup do súkromného repozitára. Overiť súčet a celý ZIP rozbaliť do zapisovateľného priečinka. Ponechať spolu `SOSkuska.exe`, `_internal` a `SOSkuska-worker.exe`. Použiť [prenosnú verziu](WINDOWS_PORTABLE.md); blokovanie bezpečnostnou politikou zaznamenať, ochranu nevypínať.

## 2 Použiť dočasné dáta

V priečinku rozbalenej aplikácie otvoriť PowerShell a spustiť:

```powershell
$acceptanceDb = Join-Path $env:TEMP ("SOSkuska-acceptance-" + [guid]::NewGuid().ToString() + ".sqlite3")
.\SOSkuska.exe --data "$acceptanceDb"
```

Zapísať hodnotu `$acceptanceDb`. Pri každom opätovnom otvorení spustiť iba druhý riadok s **rovnakou cestou**, negenerovať nový GUID. Po zatvorení PowerShellu do premennej vrátiť zapísanú cestu. Zálohu/obnovu testovať len s touto databázou a pred obnovou zatvoriť ostatné inštancie. Bežné študijné dáta nemeniť.

## 3 Dokončiť Windows akceptáciu

Prejsť celý [Windows zoznam](WINDOWS_ACCEPTANCE.md), samotný štart nestačí. Overiť prázdny začiatok, Unicode predmety/témy/otázky, CSV náhľad/import, testy a uložené výsledky, hodnotenie/históriu kartičiek a pauzu/dokončenie sústredenia. Po zatvorení znovu otvoriť rovnakú databázu a overiť uloženie. Pre obnovu sústredenia prerušiť iba dočasnú testovaciu inštanciu po kontrolnom bode; overiť pozastavenú obnovu bez započítania vypnutého času aj zahodenie. Overiť zálohu/obnovu a bezpečnostnú kópiu, zapnuté denné zálohy počas behu, jazyky/vzhľad, vnorené posúvanie, rozmery 1440×900/1024×700 a podporované mierky 100/125/150 %. Nepodporované kombinácie výslovne zapísať.

## 4 Overiť skutočný model Ollama

Ollama zostáva pre bežné štúdium voliteľná, Tutor však pred dokončením akceptácie potrebuje skutočný test. Zapísať verzie servera/modelu, identifikátor modelu, hardvér, dátum a adresu bez prihlasovacích údajov. Výslovne Connect a Send; overiť streamovanie, Stop, opätovné pripojenie a otvorenie uloženého chatu. Vypnúť server a overiť offline štúdium. Zapísať obmedzenia kvality/rýchlosti; falošný server CI nie je dôkaz skutočného modelu. Nevykonateľné kontroly ponechať NOT RUN s dôvodom, akceptáciu neoznačovať hotovú.

## 5 Zapísať výsledky

Záznam kopírovať pre každé zariadenie/beh a pripojiť dôkazy ku každému bodu. Použiť PASS / FAIL / NOT RUN; prázdne pole nie je úspech. Snímky nesmú obsahovať osobný študijný obsah ani prihlasovacie údaje.

| Pole | Hodnota |
| --- | --- |
| Dátum a testujúci | [DÁTUM / TESTUJÚCI] |
| Edícia/build Windows a architektúra CPU | [WINDOWS / ARCHITEKTÚRA] |
| Hardvér, rozlíšenie a mierka | [HARDVÉR / ROZLÍŠENIE / MIERKA] |
| Verzia aplikácie, commit artefaktu a SHA-256 ZIPu | [VERZIA / COMMIT / SHA-256] |
| Cesta dočasnej databázy | [CESTA] |
| Bod, očakávané a skutočné správanie | [BOD / OČAKÁVANIE / SKUTOČNOSŤ] |
| Výsledok a odkaz na snímku/log | NOT RUN — [DÔKAZ / DÔVOD] |
| Verzie servera/modelu Ollama a adresa | [SERVER / MODEL / ADRESA] |
| Reprodukcia chyby a opravné PR | [KROKY / PR ALEBO ŽIADNE] |

## 6 Vyriešiť nálezy

Chyby opraviť v novej vetve a PR, uchovať reprodukciu, zabezpečiť nezávislú revíziu Sol na medium a príslušné kontajnerové kontroly aj CI. Chybné prípady zopakovať na opravenom Windows artefakte; starý úspech nepotvrdzuje zmenené správanie. Nevyriešené/neoverené body ponechať viditeľné. Zlúčiť len s výslovným súhlasom používateľa.

## 7 Pripraviť v1.0.0

Po úspešnej akceptácii a opravách zosúladiť verziu/pätičku, štyri README odkazy, stav architektúry a changelog cez PR. Skontrolovať CI a získať súhlas na zlúčenie/vydanie. Označiť presný zlúčený commit, získať jeho overený Windows ZIP/súčet/správu z CI main a vydať poznámky s funkciami, zmenami a obmedzeniami. Overiť tag, súčet a stiahnutie. Nepremenovať binárku v0.18.1 na v1.0.0. Nejde o prísľub inštalátora, EXE pre macOS, automatických aktualizácií ani bezchybnosti.
