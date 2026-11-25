# Další kroky · 25. listopadu 2026

[English](../NEXT_STEPS.md) · [Čeština](NEXT_STEPS.md) · [Slovenčina](../sk/NEXT_STEPS.md) · [Русский](../ru/NEXT_STEPS.md)

Aktuální vydání: **v0.19.0**, schéma **10**. Kroky designu 1–2 jsou implementované přes PR #43 a #44: společný vzhled a Dashboard/sidebar. Čtyři dřívější nálezy Astra zůstávají vyřešené. Toto vydání nepotvrzuje přejímku v1.0.0.

1. **Další implementace: krok 3, Practice Tests.** Použít [plán designu](../agents/BRIGHT_UI_REDESIGN.md) a [předání kroku 2](../agents/design/bright-ui-step2/README.md). Nová větev, zachovat odpovědi/termíny/historii, příslušné kontroly v kontejneru a nezávislá revize Sol na medium. Nedělat všechny zbývající kroky najednou. Nová práce, sloučení i vydání potřebují vlastní schválení.
2. **Po redesignu zopakovat skutečnou přejímku.** Použít aktuální [Windows balíček](WINDOWS_PORTABLE.md) a [ruční seznam](WINDOWS_ACCEPTANCE.md), dočasná data a zapsat OS/build, hardware, rozlišení/měřítko, verzi/součet a výsledky. Kontroly počátečního měřítka 100/150 % v kontejneru nejsou nativní Windows ani změna DPI za běhu. Omezení živého škálování CTk zůstává v předání.
3. **Ověřit skutečný model Ollama.** Zapsat verze modelu/serveru, hardware, adresu bez přihlašovacích údajů, datum a výsledky Connect/stream/Stop/opětovného připojení/uloženého chatu. Se zastaveným serverem ověřit offline studium. Falešný server CI neprokazuje kvalitu ani výkon skutečného modelu.
4. **Samostatně dokončit práci a prezentaci.** Osobní údaje, předmět, jazyk a termín ponechat jako zástupná pole do dodání. Doplnit skutečné snímky, zdroje a výsledky; aktualizovat generovaná pole a prohlédnout konečné stránkování. Řídit se zadáním; úspěch testů aplikace neurčuje termín ani splnění odevzdání.

Před v1.0.0 dokončit přejímku, opravit nálezy přes revidované PR, zopakovat kontroly a vydat jen se souhlasem uživatele. Tato aktualizace neoznačuje ruční položky jako úspěšné. Historické potvrzení v0.15.0 neověřuje redesign.
