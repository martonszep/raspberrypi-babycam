# Raspberry Pi Baby Monitor (Flask + MediaMTX)

This project turns a Raspberry Pi Zero 2 W into a simple baby monitor with:
- **Video + audio streaming** (via [MediaMTX](https://github.com/bluenviron/mediamtx))
- **Web interface** (Flask) to toggle video/audio
- **Temperature monitoring**
- **Shutdown/Reboot controls** (with Font Awesome sidebar)
- **Systemd service for auto-start on boot**

---

## 📦 Prerequisites

- Raspberry Pi OS Lite 64-bit (recommended for performance)
- Raspberry Pi camera module (or USB webcam)
- USB microphone (for audio)
- Python 3.9+ (included in Raspberry Pi OS)

---

## 🛠️ Setup

### 1. Install dependencies and python venv

```bash
# First, install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install python3-venv python3-pip git -y

# For audio-only streaming install (default config for icecast is fine):
sudo apt install libportaudio2 libportaudiocpp0 portaudio19-dev icecast2 ffmpeg -y
sudo systemctl enable icecast2
sudo systemctl restart icecast2

# Gstreamer will take a while to install (supposedly faster than ffmpeg in the long run):
sudo apt-get install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio gstreamer1.0-rtsp

# Create and activate venv
python3 -m venv babycam_venv
source babycam_venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Install MediaMTX
WebRTC is the fastest way to stream to a browser. Get latestTo install it, download the latest version from the [releases](https://github.com/bluenviron/mediamtx/releases) page. Raspberry Pi OS 64-bit users will want the "arm64" compressed tar file (ending .tar.gz). Unpack it and you will get a mediamtx executable and a configuration file called `mediamtx.yml`. Note that we already provide a `custom_mediamtx.yml` for optimized performance.

```bash
cd mediamtx
wget https://github.com/bluenviron/mediamtx/releases/latest/download/mediamtx_linux_arm64v8.tar.gz
tar -xvzf mediamtx_linux_arm64v8.tar.gz
```
If you do not want to use the `custom_mediamtx.yml`, the main part you'll need to configure at the end of the config file is:
```yaml
paths:
  # mic:
  #   source: alsa://hw:0,0
  cam:
    source: rpiCamera
    sourceOnDemand: yes
    runOnReady: >
      gst-launch-1.0
      rtspclientsink name=s location=rtsp://localhost:8554/cam_with_audio
      rtspsrc location=rtsp://127.0.0.1:8554/cam latency=0 ! rtph264depay ! s.
      alsasrc device=hw:0,0 ! opusenc bitrate=16000 ! s.
    runOnReadyRestart: yes
  cam_with_audio:
    sourceOnDemand: yes
```

### 3. (Optional) Access your router and set the IP of the Raspberry Pi device to static
Otherwise you need to find out the IP every time it changes in order to access the app.

### 4. (Optional) Permissions for shutdown/reboot
Allow the Flask app to call shutdown/reboot without password:
```bash
sudo visudo
```
Scroll down to the bottom and add:
```bash
<your_username> ALL=(ALL) NOPASSWD: /sbin/shutdown, /sbin/reboot
```

## 🚀 Launch the app
```bash
./start_babymonitor.sh
```
Run the command above and access the app on your phone/PC:
```html
http://<raspberrypi-ip>:5000
```
- Toggle video/audio stream.
- View CPU temperature.
- Shutdown/reboot the Pi from the sidebar.

## 🔄 Autostart on boot
Create `systemd` service:
```bash
sudo nano /etc/systemd/system/babymonitor.service
```

Content:
```ini
[Unit]
Description=Baby Monitor Flask App
After=network.target

[Service]
User=<your_username>
WorkingDirectory=/path/to/raspberrypi-babycam
ExecStart=/path/to/raspberrypi-babycam/start_babymonitor.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable babymonitor.service
sudo systemctl start babymonitor.service
```

Check logs:
```bash
sudo systemctl status babymonitor.service
```

## 🐛 Debugging
If `systemd` has been service has been set up, you can find the logs here:
```bash
journalctl -u babymonitor.service -f
```