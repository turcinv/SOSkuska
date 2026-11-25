# Переносимое приложение для Windows

[English](../WINDOWS_PORTABLE.md) · [Čeština](../cs/WINDOWS_PORTABLE.md) · [Slovenčina](../sk/WINDOWS_PORTABLE.md) · [Русский](../ru/WINDOWS_PORTABLE.md)

v0.19.0 включает **неподписанный переносимый ZIP для Windows x64**, а не установщик. Пользователю не нужны Python или права администратора.

1. Скачай `SOSkuska-windows-x64.zip` и файл `.sha256` из [v0.19.0](https://github.com/turcinv/SOSkuska/releases/tag/v0.19.0). Частный репозиторий требует входа на GitHub и доступа. Выбирай именованный Windows ZIP, а не архив исходников GitHub.
2. Полностью распакуй ZIP в папку с правом записи. Сохрани всю папку `SOSkuska`, включая `_internal` и `SOSkuska-worker.exe`.
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
