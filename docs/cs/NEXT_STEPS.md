# Další kroky · 22. listopadu 2026

[English](../NEXT_STEPS.md) · [Čeština](../cs/NEXT_STEPS.md) · [Slovenčina](../sk/NEXT_STEPS.md) · [Русский](../ru/NEXT_STEPS.md)

Aktuální vydání: **v0.18.0**, schéma **10**, s uloženým Light/Dark/System. Uživatel 22. listopadu potvrdil dokončení testování v0.15.0 a schválil sloučení vzhledu; podmínka je splněná. Potvrzení nenahrazuje výsledky pro jednotlivá zařízení: podrobnosti čistého počítače, DPI a hardwaru nebyly dodané. V důkazech projektu je rozlišuj.

1. **Ověřit nové vydání.** Použít dočasná data nebo kopii zálohy. Na Windows ověřit živé Light/Dark, koncepty, čtyři jazyky, kompaktní okno a měřítko. System ověřit skutečnou změnou OS na Windows/macOS; Linux záměrně používá Light. Exportovat a otevřít zálohu schématu 10. Zachovat originály schématu 9, protože v0.16.0 migrovaná data neotevře. Zaznamenat [přejímku Windows](WINDOWS_ACCEPTANCE.md).
2. **Otestovat reálný model Ollama.** Zapsat OS, hardware, model/verzi, adresu serveru a výsledky připojení, streamu, Stop, opětovného připojení a uloženého chatu. Studijní funkce musí fungovat i bez běžícího serveru. CI s falešným serverem nedokládá kvalitu modelu ani výkon hardwaru. Reálná kontrola zatím není zaznamenaná.
3. **Souběžně připravit semestrální odevzdání.** Popis implementace, diagramy architektury, snímky, důkazy testů, omezení a scénář ukázky. Rozlišit vydané chování, potvrzení uživatele, automatizaci a neověřené ruční body. Před odevzdáním vycházet ze skutečných pokynů zadání; tento seznam nedokládá jejich splnění.
4. **Obnova soustředění po pádu** — v0.17.0 přidává obnovu soustředění po pádu se schématem **10**. Před otevřením původních dat vytvoř zálohu: migrace je transakční, ale v0.16.0 databázi schématu 10 neotevře. [Obnova soustředění po pádu](FOCUS_RECOVERY.md).

Chyby základu patří do samostatných opravných PR, případně opravného vydání. Funkce mají vlastní větev, kontejnerové GUI kontroly a nezávislou revizi Sol se středním úsilím. Zachovat čtyři jazyky dokumentace. Sloučení a vydání jen se souhlasem uživatele. Pro budoucí práci se automaticky nezavádí další trvalá podmínka testování základu.

5. **Plánované místní zálohy** — Plánované místní zálohy jsou dostupné ve **v0.18.0**. Schéma SQLite zůstává **10**. Ruční záloha a obnova fungují samostatně. [Plánované místní zálohy](SCHEDULED_BACKUPS.md).
