# Testy v kontajneri

[English](../CONTAINER_TESTS.md) · [Čeština](../cs/CONTAINER_TESTS.md) · [Slovenčina](../sk/CONTAINER_TESTS.md) · [Русский](../ru/CONTAINER_TESTS.md)

Na bežné kontroly používaj kontajner, aby okná GUI nerušili prácu na ploche. Docker musí byť nainštalovaný a spustený; projekt Docker Desktop automaticky neinštaluje ani nespúšťa. Z koreňa repozitára:

```sh
docker build -f Dockerfile.tests -t soskuska-tests .
docker run --rm --init --network none --cpus 2 --memory 2g soskuska-tests
```

Zachovaj `--init`: zabezpečí správne doručenie štartovacieho signálu virtuálnemu displeju a upratanie potomkov procesu.

Zostavenie sťahuje Python, systémové knižnice a závislosti, preto vyžaduje internet. Po zmene zdrojov obraz znovu zostav; súbory sa kopírujú do obrazu, nie sú pripojené naživo. Ďalšie zostavenie využije vyrovnávaciu pamäť závislostí. Testy potrebujú len miestnu slučku pre falošnú Ollamu, takže vonkajšia sieť je vypnutá. Limity CPU/pamäte obmedzujú rušenie ostatnej práce; prípadne ich uprav. Nepripája sa displej ani dátový priečinok hostiteľa a neotvárajú sa porty. `.dockerignore` povoľuje iba testované zdroje; prostredia, databázy, tajné údaje a história Gitu zostávajú mimo kontextu zostavenia. Kontajner sa potom odstráni, obraz a vyrovnávacia pamäť zostanú.

Obraz beží ako bežný používateľ bez práv root. Xvfb vytvorí vnútornú virtuálnu obrazovku pre všetkých 15 GUI skriptov; na hostiteľovi sa neotvoria okná aplikácie. Spoločný `tools/run_checks.py` spustí kontrolu závislostí, syntaxe, 244 jednotkových testov a GUI skripty s časovým limitom pre každý proces. Celok trvá niekoľko minút; chyba vracia nenulový kód. CI používa rovnaký zoznam GUI cez `--gui-only` po samostatných jednotkových kontrolách.

Linuxový kontajner neoveruje natívny Quit na macOS, trackpad Tk 9 ani UI Windows. Natívne kontroly na Macu spúšťaj len pri relevantnej platformnej zmene a viditeľný beh najprv dohodni s používateľom. Úspešný kontajner nenahrádza dôležitú zlyhávajúcu platformnú kontrolu.
