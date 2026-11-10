#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if [ ! -x .venv-macos/bin/python ]; then
    echo "SOSkúška: missing macOS environment. See soskuska/README.md."
    printf 'Press Enter to close… '
    read -r response
    exit 1
fi
exec .venv-macos/bin/python soskuska/app.py "$@"
