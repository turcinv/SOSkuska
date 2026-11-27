# Server MCP len na čítanie

[English](../MCP_SERVER.md) · [Čeština](../cs/MCP_SERVER.md) · [Slovenčina](MCP_SERVER.md) · [Русский](../ru/MCP_SERVER.md)

SOSkúška obsahuje voliteľný server [Model Context Protocol](https://modelcontextprotocol.io). Vďaka nemu môže AI asistent, ktorého už používate (Claude Desktop, VS Code, Kiro alebo iný hostiteľ MCP), **čítať** vaše študijné dáta: skúšať vás z vašich vlastných otázok, vidieť, ktoré kartičky sú na rade, a plánovať opakovanie podľa skutočných výsledkov. Nemôže nič zmeniť.

## Čo dokáže a čo nie

- **Len čítanie.** Predmety, témy, otázky, balíčky a kartičky na rade, čas sústredenia, výsledky testov a termíny skúšok. Žiadny nástroj nezapisuje, nemaže ani neimportuje.
- **Odpovede sú predvolene skryté.** Správne možnosti, vysvetlenia a zadné strany kartičiek sa vrátia len vtedy, keď o ne asistent výslovne požiada (napríklad aby skontroloval vašu odpoveď). Spustením s `--no-answers` ich zakážete úplne.
- **Žiadna sieť.** Asistent spustí server ako miestny program a komunikuje s ním cez štandardný vstup/výstup. SOSkúška neotvára žiadny port a nikam sa nepripája.
- **Bezpečné vedľa aplikácie.** Každá požiadavka otvorí databázu na okamih len na čítanie a hneď ju zatvorí. Aplikácia môže zostať otvorená a nečinný asistent nikdy neblokuje obnovu zo zálohy; požiadavka počas obnovy dostane správu „busy, retry“.

**Súkromie:** všetko, čo server vráti, ide k modelu, ktorý stojí za vaším asistentom. Ak je to cloudová služba, vaše študijné dáta sa k nej dostanú. Pripájajte len asistentov, s ktorými ste ochotní zdieľať svoje študijné dáta.

## Inštalácia

Server potrebuje zdrojový kód (pozri [Vývoj](DEVELOPMENT.md)); prenosný ZIP pre Windows ho neobsahuje. Voliteľnú závislosť nainštalujte do rovnakého prostredia, ktoré používate pre aplikáciu:

```sh
# macOS
.venv-macos/bin/python -m pip install -r soskuska/requirements-mcp.txt
# Windows
.venv\Scripts\python -m pip install -r soskuska\requirements-mcp.txt
```

Overte, že sa spustí (ukončíte Ctrl+C; potichu čaká na asistenta):

```sh
.venv-macos/bin/python soskuska/mcp_server.py --data .local-data/dev.sqlite3
```

Bez `--data` číta bežnú databázu aplikácie. Nikdy databázu nevytvára: najprv aplikáciu raz otvorte.

## Pripojenie asistenta

Používajte **absolútne cesty** k Pythonu prostredia a k `soskuska/mcp_server.py`. Príklady používajú cesty z macOS; vo Windows použite cesty ako `C:\\Users\\you\\SOSkuska\\.venv\\Scripts\\python.exe`.

**Claude Desktop** (`claude_desktop_config.json`) a **Kiro** (`~/.kiro/settings/mcp.json`):

```json
{
  "mcpServers": {
    "soskuska": {
      "command": "/Users/you/SOSkuska/.venv-macos/bin/python",
      "args": ["/Users/you/SOSkuska/soskuska/mcp_server.py"]
    }
  }
}
```

**VS Code** (`.vscode/mcp.json` alebo používateľský `mcp.json`):

```json
{
  "servers": {
    "soskuska": {
      "type": "stdio",
      "command": "/Users/you/SOSkuska/.venv-macos/bin/python",
      "args": ["/Users/you/SOSkuska/soskuska/mcp_server.py", "--no-answers"]
    }
  }
}
```

Pre inú databázu pridajte do `args` hodnoty `"--data", "/path/to/file.sqlite3"`. Umiestnenie konfiguračných súborov sa medzi verziami hostiteľov mení; ak súbor vyššie neexistuje, pozrite si dokumentáciu svojho hostiteľa.

## Nástroje a prompty

| Nástroj | Vracia |
| --- | --- |
| `list_subjects` | Predmety, termíny skúšok, zostávajúce dni, počty tém/otázok, čas sústredenia |
| `get_subject` | Témy jedného predmetu s počtami otázok podľa náročnosti |
| `search_questions` | Otázky predmetu, voliteľne podľa textu, témy, náročnosti alebo jedného presného `question_id`; odpovede len s `include_answers` |
| `list_decks` / `due_flashcards` | Balíčky s počtom kariet na rade; karty na rade, zadné strany len s `include_backs` |
| `study_statistics` | Čas sústredenia, vážená úspešnosť testov a vlastné hodnotenie kartičiek za Last 7 days, Last 30 days alebo All time |
| `practice_history` | Dokončené testy so skóre podľa tém, pod názvom predmetu, s ktorým boli písané |
| `upcoming_exams` | Skúšky odo dneška |

Prompty: **Quiz me** (jedna otázka po druhej, odpoveď až po vašej odpovedi) a **Weak topics study plan**. Prostriedok `soskuska://subjects` dáva krátky prehľad v Markdowne.

Výsledky sú pre model malé: zoznamy končia na 50 položkách (skúšky na 20) a zhruba na 20 KB a dlhé popisy sa skrátia; oboje sa označí ako `truncated`. Otázky a kartičky sa vždy vracajú celé.

## Riešenie problémov

- **„needs the optional 'mcp' package“** — nainštalujte `requirements-mcp.txt` do Pythonu uvedeného v konfigurácii hostiteľa.
- **„no SOSkúška database“** — raz otvorte aplikáciu alebo odovzdajte správnu cestu `--data`.
- **„busy“** — beží obnova alebo iná výhradná operácia; o chvíľu to skúste znova.
- **„Open SOSkúška once to update it“** — databáza patrí inej verzii aplikácie; otvorte aplikáciu, aby ju mohla aktualizovať.

Odstránenie: zmažte položku `soskuska` z konfigurácie hostiteľa. Voliteľne balík odinštalujte príkazom `python -m pip uninstall mcp`.

## Stav overenia

Automatické testy (klient v procese v aktuálnom bezstavovom protokole aj v staršom handshaku a skutočný podproces cez stdio) pokrývajú každý nástroj, skryté odpovede, `--no-answers`, limity, chyby busy/schéma/chýbajúca databáza a nezmenený súbor databázy. Zaznamenaný beh so skutočným asistentom zatiaľ chýba.
