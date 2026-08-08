# raspberry5_astro

Welcome to the messy world: Raspberry Pi 5 configuration for astrophotography

## Concept

This project turns a **Raspberry Pi 5 running Pi OS Lite (headless, 64-bit)** into an
astrophotography rig that runs the standard open-source astronomy stack:

- **INDI core** — the INDI server and its client library
- **INDI 3rd-party drivers** — drivers for cameras, focusers, mounts, wheels, GPS, etc.
- **PHD2** — the autoguiding application
- **KStars / Ekos** — the main capture and sequencing front-end

The Pi runs headless (no desktop), so a **virtual desktop via RealVNC** is set up to
drive the graphical applications (KStars, PHD2) from a laptop.

The official distro packages of these astronomy tools are either absent or not fully
functional on RPi5 Bookworm, so the binaries are **cross-compiled for aarch64 and
packaged as `.deb` files under `./deb`**. Because the packages were built with
`checkinstall` they carry **no declared `Depends:` metadata**, so all runtime
libraries must be installed manually *before* installing the `.deb` files — this is
what the `cmd.list` and the per-version scripts in this repo are for.

Two KStars builds are provided, and they need different dependency sets:

| | KStars 3.7.1 | KStars 3.8.3 |
|---|---|---|
| `./deb` packages | `indi_20260421`, `indi-3rdparty-2.0.8`, `indi-3rdparty-driver_2.0.8`, `kstars_3.7.1`, `phd2_2.6.14` | `indi-core-rpi5_2.2.1`, `indi-3rdparty-rpi5_2.2.1`, `kstars-custom_3.8.3`, `phd2_2.6.14` |
| dependencies | `cmd.list` (verified) | `cmd.list` + `install_deps_383.sh` (extra libs for 3.8.3) |
| broken-link fix | `fixindilink.sh` | not needed (correct SONAMEs) |

> The 3.7.1 dependency list was the original, verified one. The 3.8.3 debs link a few
> libraries that `cmd.list` does **not** cover (`libopencv_calib3d`, the GnuTLS flavour
> of curl, `libzmq5`, `libgps28`, `libdc1394`), so 3.8.3 needs `install_deps_383.sh` on
> top of `cmd.list`.

## Requirements

**Hardware**
- Raspberry Pi 5, 4 GB RAM or higher (8 GB recommended for best performance)
- SD card 32 GB or higher (class 10 / A2 recommended)
- **5V/5A USB-C power adapter OR alternative powerbox** (See Warning 2 below)
- Ubuntu desktop PC (or laptop) to flash the SD card and to drive KStars/PHD2 over VNC

**Software**
- rpi-imager (https://www.raspberrypi.com/software/)
- Raspberry Pi OS Lite 64-bit **Legacy (bookworm)** image (https://downloads.raspberrypi.com/raspios_arm64/images/raspios_arm64-2025-05-13/)
- RealVNC Viewer on the desktop machine

## Warning 1

You must be an experienced Linux user, otherwise you will be stumble for some uncertain points in my instruction which I overlooked. AI may helps you...

## Warning 2 — about the power adapter (IMPORTANT !!!)

Raspberry Pi 5 needs **5V/5A** power. If you use a standard 5V/3A (15W) or underrated adapter you will get troubles running anything attached via USB ports. However, it is really hard to get a 5V/5A USB-C adapter in outdoor environment and no mobile battery supports this type because **5V/5A IS NON-STANDARD**.
If you want to use 5V/3A standard adapter, I recommend you to get an external power adapter for astronomers like this:

[SVBONY SV241 Astronomy Telescope Power Adapter]
(https://www.amazon.com/dp/B0F24HSX8D?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1)

In my case, I use this product to avoid the low voltage issue on Raspberry Pi 5 with a standard adapter.

**ONE MORE TIME, MOST OF ISSUE OCCURED IN THE FIELD IS DUE TO POWER!**

## Installation

### Prepare the SD card

   1. Get rpi-imager from https://www.raspberrypi.com/software/
   2. Run rpi-imager
   3. Select **raspberry pi OS Lite 64bit Legacy (bookworm)**
   4. Customize your installation option

      **Network and SSH option must be enabled and configured !**

   5. Install the image to SD card
   6. Insert the SD card to your Raspberry Pi 5
   7. Connect to pi via SSH

### Search the IP address of your Pi system and connect via SSH

Because you installed Lite version which doesn't have Desktop environment so you need
to connect it to monitor or you should connect it via SSH. If you don't know which IP
address the pi will get from dhcp of your router, then here's **nmap** for you:

```
#in your debian/ubuntu desktop
sudo apt install nmap
nmap -p 22 -open your.local.network/24
```

Then you might be able to get:

```
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-04-24 15:00 PDT
Nmap scan report for 10.X.X.X6
Host is up (0.0082s latency).

PORT   STATE SERVICE
22/tcp open  ssh

Nmap scan report for 10.X.X.1X2
Host is up (0.0048s latency).

PORT   STATE SERVICE
22/tcp open  ssh

Nmap done: 256 IP addresses (5 hosts up) scanned in 3.44 seconds
```

In my network there are 2 systems running with port 22 (SSH) opened. One is my laptop
the other is my Raspberry Pi system. Log on to the pi system now!

### Setup X11 + openbox + VNC for display

Run this script:

```
./vnc_setup.sh
```

Let's check if the virtual VNC is working well or not. Download RealVNC on your desktop
and open it. You should use port 5901. Enter **your.ip.address:5901** and connect.

### Install required packages (common base)

Run these commands to install the shared runtime libraries used by all builds:

```
sudo apt install -y libc6 libstdc++6 libusb-1.0-0 libcfitsio10 libnova-0.16-0 zlib1g libgphoto2-6 libraw20 libhidapi-libusb0 libcurl4 libftdi1-2 gpiod libusb-1.0-0 libev4 libfftw3-double3 libtheora0 libogg0 libvorbis0a libvorbisenc2 libcairo2 libpixman-1-0 libdfu1 liblimesuite22.09-1 librtlsdr0 liburjtag0 limesuite-udev libwxgtk3.2-1 libwxbase3.2-1 libwxgtk-gl3.2-1 libwxgtk-media3.2-1 libwxgtk-webview3.2-1 libopencv-core406 libopencv-imgproc406 libopencv-videoio406

sudo apt install -y liberfa1 libgsl27 libgslcblas0 liblcms2-2 libwcs7 libstellarsolver2 libqt5core5a libqt5dbus5 libqt5gui5 libqt5network5 libqt5widgets5 libqt5svg5 libqt5sql5 libqt5sql5-sqlite libqt5websockets5 libqt5printsupport5 libqt5concurrent5 libqt5xml5 libqt5qml5 libqt5qmlmodels5 libqt5quick5 libqt5datavisualization5 libqt5x11extras5 libqt5texttospeech5 libqt5waylandclient5 libkf5attica5 libkf5auth5 libkf5bookmarks5 libkf5codecs5 libkf5completion5 libkf5configcore5 libkf5configgui5 libkf5configwidgets5 libkf5coreaddons5 libkf5crash5 libkf5i18n5 libkf5itemviews5 libkf5jobwidgets5 libkf5kiocore5 libkf5kiogui5 libkf5kiowidgets5 libkf5newstuff5 libkf5newstuffcore5 libkf5notifications5 libkf5notifyconfig5 libkf5plotting5 libkf5service5 libkf5solid5 libkf5widgetsaddons5 libkf5windowsystem5 libkf5xmlgui5 libkf5globalaccel5 libkf5guiaddons5 libkf5iconthemes5 libkf5dbusaddons5 libkf5archive5 libkf5package5 zlib1g xplanet

sudo apt install -y breeze-icon-theme oxygen-icon-theme hicolor-icon-theme libkf5iconthemes5

sudo gtk-update-icon-cache /usr/share/icons/hicolor/

sudo kbuildsycoca5 --noincremental
```

## Install KStars 3.7.1

### Install additional dependencies

The 3.7.1 dependency set is fully covered by the **common base** above — no extra
packages needed.

### Install the custom build deb packages

```
cd deb
sudo apt install ./indi_20260421-1_arm64.deb ./indi-3rdparty-2.0.8_2.0.8-1_arm64.deb ./indi-3rdparty-driver_2.0.8-1_arm64.deb ./phd2_2.6.14-1_arm64.deb ./kstars_3.7.1-1_arm64.deb
```

Ignore the last message that looks like an error. Those are not errors actually.

When I built these packages I didn't put the package dependencies so it doesn't check
any dynamic links and install dependent packages. So you have another step to fix the
broken links:

```
./fixindilink.sh
sudo reboot
```

Now you are ready to run KStars and PHD2!

## Install KStars 3.8.3

### Install additional dependencies

The 3.8.3 debs link a few libraries that the common base does not cover. Install them:

```
./install_deps_383.sh
```

This installs `libopencv-calib3d406` (required by kstars itself), `libcurl3-gnutls`,
`libzmq5`, `libgps28`, and `libdc1394-25`. For details see the script header.

### Install the custom build deb packages

```
cd deb
sudo apt install ./indi-core-rpi5_2.2.1_arm64.deb ./indi-3rdparty-rpi5_2.2.1_arm64.deb ./phd2_2.6.14-1_arm64.deb ./kstars-custom_3.8.3_arm64.deb
```

The 3.8.3 packages ship the vendor camera SDKs bundled and use correct SONAMEs, so
**no symlink fix step is needed**. Reboot, then run KStars and PHD2.

```
sudo reboot
```

# Troubleshooting

## gpsd and time sync configuration issue

### What was the problem with gpsd ?

A mount system using CP210X chipset for serial communication can interfere with the
GPS dongle that uses the same chipset. In my case GPS dongle uses a different chipset
so didn't suffer such issue but encountered another issue on gpsd.

```
/lib/systemd/system

/lib/udev/rules.d/60-gpsd.rules - when device is detected, trigger the systemd to run gpsdctl@.service with parameters (/dev/ttyACM0)
gpsdctl@.service -- activate the gpsdctl and run gpsd, arguments and variables are defined at /etc/default/gpsd

gpsd.service -- activate gpsd with arguments
gpsd.socket  -- TCP socket listening on 2947
```

### So how to fix it ?

You just need to change the value of this DEVICES variable in the `/etc/default/gpsd`:

```
# Devices gpsd should collect to at boot time.
# They need to be read/writeable, either by user gpsd or the group dialout.
#DEVICES="/dev/ttyACM0"           // before
DEVICES="/dev/serial/by-id/usb-u-blox_AG_-_www.u-blox.com_u-blox_7_-_GPS_GNSS_Receiver-if00"

# Other options you want to pass to gpsd
GPSD_OPTIONS="-n"

# Automatically hot add/remove USB GPS devices via gpsdctl
USBAUTO="true"
```

then systemctl status gpsd output will be like:

```
● gpsd.service - GPS (Global Positioning System) Daemon
     Loaded: loaded (/lib/systemd/system/gpsd.service; enabled; preset: enabled)
     Active: active (running) since Fri 2025-09-05 22:37:25 PDT; 3s ago
TriggeredBy: ● gpsd.socket
    Process: 27484 ExecStart=/usr/sbin/gpsd $GPSD_OPTIONS $OPTIONS $DEVICES (code=exited, status=0/SUCCESS)
   Main PID: 27485 (gpsd)
      Tasks: 2 (limit: 4762)
        CPU: 25ms
     CGroup: /system.slice/gpsd.service
             └─27485 /usr/sbin/gpsd -n /dev/serial/by-id/usb-u-blox_AG_-_www.u-blox.com_u-blox_7_-_GPS_GNSS_Receiver-if00
```
