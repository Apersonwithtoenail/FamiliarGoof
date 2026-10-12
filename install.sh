#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p ~/.local/bin
chmod +x "$DIR/familiarterm.py"
ln -sf "$DIR/familiarterm.py" ~/.local/bin/familiarterm
echo "installed -> ~/.local/bin/familiarterm"
