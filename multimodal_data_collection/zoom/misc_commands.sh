
# Prerequisites
sudo apt-get install -y xdotool wmctrl

sudo apt-get install -y v4l2loopback-dkms v4l2loopback-utils ffmpeg


# Create virtual camera
sudo depmod -a
sudo modprobe v4l2loopback

# Check virtual camera
ls /dev/video*

# Strem video.mp4 to virtual camera:
ffmpeg -re -stream_loop -1 -i video.mp4 -f v4l2 /dev/video0 -nostdin -nostats </dev/null >/dev/null 2>&1 &

# Remove virtual camera
# sudo modprobe -r v4l2loopback
# pkill ffmpeg


# Disable Lock Screen

sudo apt install ./zoom_amd64.deb
# https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0063458

sudo visudo # add username ALL=(ALL:ALL) NOPASSWD: /user/bin/tcpdump
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/tcpdump

