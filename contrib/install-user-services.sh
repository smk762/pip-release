#!/bin/sh
# Install user services so the watcher and review UI start at login, and at
# boot when lingering is enabled.
set -eu

root=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
bin="$root/.venv/bin/pip-release"
if [ ! -x "$bin" ]; then
  echo "Missing $bin. From $root: python -m venv .venv && .venv/bin/pip install -e ." >&2
  exit 1
fi

dest="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
mkdir -p "$dest"
for name in pip-release-watch pip-release-ui; do
  sed -e "s|@ROOT@|$root|g" -e "s|@BIN@|$bin|g" \
    "$root/contrib/systemd/$name.service" > "$dest/$name.service"
done

systemctl --user daemon-reload
systemctl --user enable --now pip-release-watch.service pip-release-ui.service

if loginctl show-user "$USER" -p Linger --value 2>/dev/null | grep -qx yes; then
  echo "Lingering is already enabled, so these start at boot."
else
  if loginctl enable-linger "$USER"; then
    echo "Lingering enabled. The watcher and review UI start at boot."
  else
    echo "Could not enable lingering. The services start when you log in." >&2
  fi
fi

systemctl --user --no-pager --full status pip-release-watch.service pip-release-ui.service
