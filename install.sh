#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p ~/.local/bin
chmod +x "$DIR/familiarterm.py"
ln -sf "$DIR/familiarterm.py" ~/.local/bin/familiarterm

# icon
cp "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/assets/icon.svg" "$HOME/.local/share/icons/hicolor/scalable/apps/familiargoof.svg" 2>/dev/null || true
gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true

echo "installed -> ~/.local/bin/familiarterm"
