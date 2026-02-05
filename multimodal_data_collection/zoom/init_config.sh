#/bin/bash

sudo usermod -aG audio,video $(whoami)
groups $(whoami)

#!/bin/bash

ASOUND_FILE="$HOME/.asoundrc"

if [ -f "$ASOUND_FILE" ]; then
  echo "[✓] ~/.asoundrc already exists. No changes made."
else
  cat <<EOF > "$ASOUND_FILE"
pcm.loopout {
  type hw
  card 0
  device 0
  subdevice 0
}

pcm.loopin {
  type hw
  card 0
  device 1
  subdevice 0
}

pcm.!default pcm.loopout
EOF

  echo "[+] ~/.asoundrc created with loopin/loopout definitions."
fi

