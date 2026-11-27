# Server MCP jen pro čtení

[English](../MCP_SERVER.md) · [Čeština](MCP_SERVER.md) · [Slovenčina](../sk/MCP_SERVER.md) · [Русский](../ru/MCP_SERVER.md)

SOSkúška obsahuje volitelný server [Model Context Protocol](https://modelcontextprotocol.io). Díky němu může AI asistent, kterého už používáte (Claude Desktop, VS Code, Kiro nebo jiný hostitel MCP), **číst** vaše studijní data: zkoušet vás z vašich vlastních otázek, vidět, které kartičky jsou na řadě, a plánovat opakování podle skutečných výsledků. Nemůže nic změnit.

## Co umí a co ne

- **Jen čtení.** Předměty, témata, otázky, balíčky a kartičky na řadě, čas soustředění, výsledky testů a termíny zkoušek. Žádný nástroj nezapisuje, nemaže ani neimportuje.
- **Odpovědi jsou ve výchozím stavu skryté.** Správné možnosti, vysvětlení a rubové strany kartiček se vrátí jen tehdy, když o ně asistent výslovně požádá (například aby zkontroloval vaši odpověď). Se spuštěním `--no-answers` je zakážete úplně.
- **Žádná síť.** Asistent spustí server jako místní program a komunikuje s ním přes standardní vstup/výstup. SOSkúška neotevírá žádný port a nikam se nepřipojuje.
- **Bezpečné vedle aplikace.** Každý požadavek otevře databázi na okamžik jen pro čtení a hned ji zavře. Aplikace může zůstat otevřená a nečinný asistent nikdy neblokuje obnovu ze zálohy; požadavek během obnovy dostane zprávu „busy, retry“.

**Soukromí:** vše, co server vrátí, jde k modelu, který stojí za vaším asistentem. Pokud je to cloudová služba, vaše studijní data se k ní dostanou. Připojujte jen asistenty, se kterými jste ochotni svá studijní data sdílet.

## Instalace

Server potřebuje zdrojový kód (viz [Vývoj](DEVELOPMENT.md)); přenosný ZIP pro Windows ho neobsahuje. Volitelnou závislost nainstalujte do stejného prostředí, které používáte pro aplikaci:

```sh
# macOS
.venv-macos/bin/python -m pip install -r soskuska/requirements-mcp.txt
# Windows
.venv\Scripts\python -m pip install -r soskuska\requirements-mcp.txt
```

Ověřte, že se spustí (ukončíte Ctrl+C; potichu čeká na asistenta):

```sh
.venv-macos/bin/python soskuska/mcp_server.py --data .local-data/dev.sqlite3
```

Bez `--data` čte běžnou databázi aplikace. Nikdy databázi nevytváří: nejdřív aplikaci jednou otevřete.

## Připojení asistenta

Používejte **absolutní cesty** k Pythonu prostředí a k `soskuska/mcp_server.py`. Příklady používají cesty z macOS; ve Windows použijte cesty jako `C:\\Users\\you\\SOSkuska\\.venv\\Scripts\\python.exe`.

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

**VS Code** (`.vscode/mcp.json` nebo uživatelský `mcp.json`):

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

Pro jinou databázi přidejte do `args` hodnoty `"--data", "/path/to/file.sqlite3"`. Umístění konfiguračních souborů se mezi verzemi hostitelů mění; pokud soubor výše neexistuje, podívejte se do dokumentace svého hostitele.

## Nástroje a prompty

| Nástroj | Vrací |
| --- | --- |
| `list_subjects` | Předměty, termíny zkoušek, zbývající dny, počty témat/otázek, čas soustředění |
| `get_subject` | Témata jednoho předmětu s počty otázek podle obtížnosti |
| `search_questions` | Otázky předmětu, volitelně podle textu, tématu, obtížnosti nebo jednoho přesného `question_id` (s `version` pro hodnocení); odpovědi jen s `include_answers` |
| `list_decks` / `due_flashcards` | Balíčky s počtem karet na řadě; karty na řadě, rubové strany jen s `include_backs` |
| `study_statistics` | Čas soustředění, vážená úspěšnost testů a vlastní hodnocení kartiček za Last 7 days, Last 30 days nebo All time |
| `practice_history` | Dokončené testy se skóre podle témat, pod názvem předmětu, se kterým byly psány |
| `upcoming_exams` | Zkoušky od dneška |

Prompty: **Quiz me** (jedna otázka po druhé, odpověď až po vaší odpovědi) a **Weak topics study plan**. Prostředek `soskuska://subjects` dává krátký přehled v Markdownu.

Výsledky jsou pro model malé: seznamy končí na 50 položkách (zkoušky na 20) a zhruba na 20 KB a dlouhé popisy se zkrátí; obojí se označí jako `truncated`. Otázky a kartičky se vždy vracejí celé.

## Řešení problémů

- **„needs the optional 'mcp' package“** — nainstalujte `requirements-mcp.txt` do Pythonu uvedeného v konfiguraci hostitele.
- **„no SOSkúška database“** — jednou otevřete aplikaci nebo předejte správnou cestu `--data`.
- **„busy“** — běží obnova nebo jiná výhradní operace; za chvíli to zkuste znovu.
- **„Open SOSkúška once to update it“** — databáze patří jiné verzi aplikace; otevřete aplikaci, aby ji mohla aktualizovat.

Odebrání: smažte položku `soskuska` z konfigurace hostitele. Volitelně balíček odinstalujte příkazem `python -m pip uninstall mcp`.

## Stav ověření

Automatické testy (klient v procesu v aktuálním bezstavovém protokolu i ve starším handshaku a skutečný podproces přes stdio) pokrývají každý nástroj, skryté odpovědi, `--no-answers`, limity, chyby busy/schéma/chybějící databáze a nezměněný soubor databáze. Zaznamenaný běh se skutečným asistentem zatím chybí.
