# Uložené konverzace AI Tutor

[English](../TUTOR_HISTORY.md) · [Čeština](TUTOR_HISTORY.md) · [Slovenčina](../sk/TUTOR_HISTORY.md) · [Русский](../ru/TUTOR_HISTORY.md)

AI Tutor nyní ukládá konverzace lokálně včetně původního serveru/modelu a stavu odpovědi. Historii lze otevřít bez sítě, výslovně se připojit pro pokračování nebo vybranou konverzaci po potvrzení smazat. Vydáno ve v0.12.0 se schématem 7, které transakčně migruje původní studijní data.

## Použití historie

Připoj se, vyber model/jazyk, napiš otázku a zvol Send. Otázka se uloží před síťovým požadavkem. Název vzniká z první otázky. Odpověď se ukládá po dokončení, zastavení nebo chybě. New chat odpojí aktuální konverzaci; potvrzení vymaže rozepsanou otázku, ale zachová historii.

Výběr ukazuje 20 konverzací na stránku podle poslední změny. Použij Previous chats / Next chats a Refresh, vyber název a Open. Otevření nic neodesílá a nepřipojuje se. Obnoví původní server/model a text; pokračování vyžaduje Connect / refresh. Konverzace zůstává svázaná s původním serverem a modelem. Pro jiný použij New chat; chybějící model se nenahradí automaticky. Jazyk odpovědi lze měnit po otázkách.

Delete vyžaduje druhé potvrzení a odstraní vybranou konverzaci i její otázky/odpovědi. Kontrola revize odmítne zastaralou změnu či smazání z jiného okna. Přechod na jinou konverzaci se s rozepsanou otázkou odmítne; nejprve ji výslovně vymaž. Znovuotevření stejné konverzace otázku zachová.

## Přerušení a chyby

Stop uchová přijatý text jako stopped. Failed, stopped, pending a interrupted nevstupují do kontextu modelu. Běžné zavření/Quit uloží viditelnou část jako interrupted a zruší síť bez čekání na vlákno. Chyba uložení ponechá text, zakáže odesílání/přepínání a nabídne Retry save reply. Quit ponechá okno otevřené a ukáže AI Tutor, dokud odpověď neuložíš či výslovně nezahodíš. Discard unsaved vyžaduje potvrzení, zachová další rozepsanou otázku a nemaže historii.

Pád procesu/systému může ponechat uloženou pending otázku; části streamu se průběžně neukládají, proto se rozpracovaná odpověď může ztratit. Otevři ji a dvakrát potvrď Mark interrupted před další otázkou. Jde o výslovnou akci, protože jiné okno může stále generovat. Obnova/smazání zneplatní jeho pozdní zápis; před zahozením či novým načtením zkopíruj neuložený text.

## Data, soukromí a limity

`tutor_conversations` obsahuje název, endpoint, model, revizi a časy UTC; `tutor_turns` pořadí, otázku/odpověď/jazyk/stav a časy. Revize se kontroluje ve stejné transakci jako zápis; opakované uložení stejné dokončené odpovědi nic neduplikuje. Síťová vlákna nevolají Tk ani SQLite. Spuštění, historie, navigace a Settings Save nic neodesílají; Send posílá omezený dokončený kontext vybraného chatu.

Konverzace jsou prostý text ve vybrané databázi a patří do záloh. Nejsou šifrované ani synchronizované. Limit: 12 otázek na konverzaci, otázka 4 000 znaků, odpověď 16 000; kontext nejvýše šest dokončených dvojic / 24 000 znaků. Částečné či chybné odpovědi nejsou dokončeným kontextem. AI odpovědi nadále ověřuj.

Obnova přijímá pouze samostatné zálohy schématu 7. Starší originál uchovej. Vlastní zálohu schématu 6 převedeš tak, že vytvoříš samostatnou kopii, otevřeš ji v nové aplikaci přes --data pro migraci při startu a vyexportuješ novou zálohu přes Create backup. Kvůli převodu nenahrazuj pracovní databázi. Migrace neobnoví chaty ze starých verzí bez ukládání.
