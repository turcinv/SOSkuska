# Переносимое приложение для Windows

[English](../WINDOWS_PORTABLE.md) · [Čeština](../cs/WINDOWS_PORTABLE.md) · [Slovenčina](../sk/WINDOWS_PORTABLE.md) · [Русский](../ru/WINDOWS_PORTABLE.md)

Ветка упаковки создаёт **неподписанный переносимый ZIP для Windows x64**, а не установщик. Пользователю не нужны Python или права администратора. Опубликованная v0.14.0 остаётся выпуском исходников; эта работа пока не выпущена.

1. В Actions → CI открой запуск точного PR/коммита. Убедись в успехе **Windows portable build and acceptance**, скачай артефакт `SOSkuska-windows-x64-<commit>`. Нужны вход на GitHub и доступ к репозиторию; артефакты хранятся 14 дней.
2. Распакуй артефакт, затем полностью распакуй `SOSkuska-windows-x64.zip` в папку с правом записи. Сохрани всю папку `SOSkuska`, включая `_internal` и `SOSkuska-worker.exe`.
3. Открой `SOSkuska.exe`. Не запускай его внутри ZIP, не переноси только EXE и не запускай помощник напрямую. Данные остаются отдельно в `%LOCALAPPDATA%\SOSkuska\dashboard.sqlite3`; прежний резервный путь ExamPrep также действует.
4. Неподписанный файл могут блокировать защита Windows или правила организации. Проверь источник/коммит и SHA-256; не отключай защиту. При запрете политикой обратись к администратору.

Для отдельной проверки запусти в PowerShell из распакованной папки `./SOSkuska.exe --data "$env:TEMP/SOSkuska-check.sqlite3"`. Выбери новый неиспользуемый путь. Обычное обучение автономно; Ollama необязательна и устанавливается отдельно. Удаление папки приложения не удаляет папку данных. Перед обновлением сделай резервную копию; старая программа отклоняет новую схему базы.

Артефакт содержит SHA-256. До распаковки внутреннего ZIP сравни его с `Get-FileHash .\SOSkuska-windows-x64.zip -Algorithm SHA256`. Совпадение проверяет целостность, а не личность издателя. Архив содержит приложение, консольный помощник, ресурсы Python/Tk/CustomTkinter, четыре языковых каталога и эти инструкции. Пользовательской базы и виртуального окружения в нём нет.

## Сборка и проверка на Windows

Используй 64-битный Python 3.12 на Windows из корня репозитория. PyInstaller закреплён отдельно как зависимость только для сборки. Windows-приложение нужно собирать на Windows:

```powershell
py -3.12 -m venv .venv-build
.\.venv-build\Scripts\python.exe -m pip install -r soskuska/requirements.txt -r packaging/requirements-build.txt
.\.venv-build\Scripts\python.exe tools/build_windows.py
.\.venv-build\Scripts\python.exe tools/check_windows_bundle.py dist/SOSkuska-windows-x64.zip --report dist/windows-acceptance.json
```

Результат: `dist/SOSkuska/`, ZIP, `.sha256` и отчёт. Спецификация создаёт GUI без консоли и консольный помощник; скрытые дочерние процессы сохраняют JSON-протокол через временный файл. При запуске исходников по-прежнему используются Python-скрипты. Без установщика, установки через реестр, подписи и автообновления.

CI распаковывает реальный ZIP во временный путь с пробелами и Unicode и запускает его из другой рабочей папки без Python в PATH. Проверяются видимое главное окно и обычное закрытие, пустая база, запуск всех четырёх языков, оба CSV-импорта, резервное копирование/проверка/восстановление и сохранность записей. Автоматические проверки на размещённом Windows **не заменяют** [ручную приёмку](WINDOWS_ACCEPTANCE.md) на чистом Windows. Упаковка macOS/Linux и Windows ARM64 не входят в работу.

Подход основан на [документации PyInstaller](https://pyinstaller.org/en/stable/spec-files.html) и [руководстве CustomTkinter](https://customtkinter.tomschimansky.com/documentation/packaging/).
