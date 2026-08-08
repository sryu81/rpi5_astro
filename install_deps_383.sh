#!/bin/bash
# =============================================================================
# Install missing runtime dependencies for kstars_3.8.3 / indi-rpi5_2.2.1 debs
# Verified against deb/kstars_3.8.3/*.deb via readelf NEEDED scan.
#
# cmd.list was verified for kstars 3.7.1 only. This script installs the delta
# that 3.8.3 additionally links:
#   - libopencv-calib3d406  (kstars 3.8.3 REQUIRED — not in cmd.list)
#   - libcurl3-gnutls       (GnuTLS flavour — cmd.list's libcurl4 is OpenSSL)
#   - libzmq5               (Avalon UltraDome drivers)
#   - libgps28              (indi_gpsd)
#   - libdc1394-25          (indi_ffmv_ccd FLIR)
# =============================================================================
set -e

if [ "$(uname -m)" != "aarch64" ]; then
    echo "ERROR: run on the Raspberry Pi 5 (aarch64), not on this machine."
    exit 1
fi

sudo apt update

sudo apt install -y \
    libopencv-calib3d406 \
    libcurl3-gnutls \
    libzmq5 \
    libgps28 \
    libdc1394-25 \
    libjpeg62-turbo

echo "Done. Verify with: ldd /usr/bin/kstars | grep 'not found'"
