lsmod | egrep 'snd_aloop|snd_dummy' || echo "no snd_aloop/snd_dummy"
cat /proc/asound/cards || echo "no /proc/asound/cards"
ls -l /dev/snd || echo "no /dev/snd"
sudo dmesg | tail -n 100 | egrep -i 'ALSA|snd|loopback' || true

systemctl --user stop pipewire.service pipewire.socket pulseaudio.service pulseaudio.socket >/dev/null 2>&1 || true
pulseaudio -k >/dev/null 2>&1 || true

sudo modprobe -r snd_aloop snd_dummy 2>/dev/null || true

sudo modprobe snd-aloop index=0 id=Loopback
sudo modprobe snd-dummy index=1 id=Dummy

sudo udevadm trigger --subsystem-match=sound
sudo udevadm settle
sleep 0.5

echo "[INFO] /proc/asound/cards:"
cat /proc/asound/cards
echo "[INFO] aplay -l:"
aplay -l 2>&1

sudo apt update
sudo apt install -y linux-modules-extra-$(uname -r)

sudo modprobe -r snd_aloop snd_dummy 2>/dev/null || true
sudo modprobe snd-aloop index=0 id=Loopback
sudo modprobe snd-dummy index=1 id=Dummy
sudo udevadm trigger --subsystem-match=sound; sudo udevadm settle; sleep 0.5
cat /proc/asound/cards; aplay -l

