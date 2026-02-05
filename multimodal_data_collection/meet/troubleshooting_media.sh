pulseaudio --start
pactl info | grep -E 'Server Name|Server String'
pactl load-module module-alsa-source device=hw:Loopback,0,0 source_name=virtmic
pactl list short sources | grep virtmic
