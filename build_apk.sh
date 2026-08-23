#!/bin/bash
# Exit on any error
set -e

echo "============================================================"
echo "  Tflow Android APK Build Script (WSL Linux Environment)"
echo "============================================================"

# ─── 1. Install Ubuntu build dependencies ───────────────────────────────────
echo "[1/6] Installing Linux build tools..."
apt-get update -y
apt-get install -y --no-install-recommends \
    git zip unzip openjdk-17-jdk \
    python3-pip autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev \
    libtinfo6 cmake libffi-dev libssl-dev \
    build-essential ccache python3-setuptools

# ─── 2. Setup user environment ──────────────────────────────────────────────
echo "[2/6] Configuring user python environment..."
# Upgrade pip and install buildozer + cython globally or for tarun
pip3 install --upgrade pip
pip3 install buildozer cython==0.29.37

# ─── 3. Copy project to Linux filesystem to avoid Windows mount permission errors ──
echo "[3/6] Transferring project to Linux native filesystem..."
LINUX_DIR="/home/tarun/DigitalNotebook"
rm -rf "$LINUX_DIR"
mkdir -p "$LINUX_DIR"

# Copy files while excluding large cache and binary dirs
rsync -av --exclude='.git/' --exclude='__pycache__/' --exclude='.buildozer/' --exclude='bin/' \
    "/mnt/c/Users/TARUN/OneDrive/Desktop/note taking/DigitalNotebook/" "$LINUX_DIR/"

chown -R tarun:tarun "$LINUX_DIR"

# ─── 4. Run Buildozer build as normal user 'tarun' ──────────────────────────
echo "[4/6] Commencing APK compilation via Buildozer..."
cd "$LINUX_DIR"
# Ensure the path contains user pip bin directory where buildozer is installed
export PATH=$PATH:/home/tarun/.local/bin

# Run buildozer as user tarun
su - tarun -c "cd $LINUX_DIR && export PATH=\$PATH:/home/tarun/.local/bin && buildozer android debug"

# ─── 5. Export APK back to Windows filesystem ──────────────────────────────
echo "[5/6] Exporting compiled APK back to Windows..."
WINDOWS_BIN_DIR="/mnt/c/Users/TARUN/OneDrive/Desktop/note taking/DigitalNotebook/bin"
mkdir -p "$WINDOWS_BIN_DIR"
cp -f "$LINUX_DIR"/bin/*.apk "$WINDOWS_BIN_DIR/"

echo "============================================================"
echo "  SUCCESS: APK build completed successfully!"
echo "  Your APK is saved at: DigitalNotebook/bin/tflow-debug.apk"
echo "============================================================"
