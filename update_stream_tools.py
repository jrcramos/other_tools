#!/usr/bin/env python3
"""
Stream Tools Updater / Portable Installer
------------------------------------------
Downloads and extracts the latest N_m3u8DL-RE binary from GitHub releases
and updates Streamlink via pip or winget.
"""

import sys
import os
import urllib.request
import json
import zipfile
import io
import subprocess
import shutil

# Ensure UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def install_nm3u8(target_dir):
    """Download and install latest N_m3u8DL-RE from GitHub releases."""
    print("=" * 72)
    print("          N_m3u8DL-RE Portable Installer & Updater")
    print("=" * 72)
    print(f"[*] Target Directory: {target_dir}")
    os.makedirs(target_dir, exist_ok=True)

    api_url = "https://api.github.com/repos/nilaoda/N_m3u8DL-RE/releases"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        print("[*] Fetching release metadata from GitHub...")
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            releases = json.loads(resp.read().decode('utf-8'))

        download_url = None
        asset_name = None
        for r in releases:
            for a in r.get("assets", []):
                name = a.get("name", "")
                if "win-x64" in name and name.endswith(".zip"):
                    download_url = a.get("browser_download_url")
                    asset_name = name
                    break
            if download_url:
                break

        if not download_url:
            print("[-] Error: No compatible Windows x64 zip asset found on GitHub.")
            return False

        print(f"[*] Downloading {asset_name}...")
        dl_req = urllib.request.Request(download_url, headers=headers)
        with urllib.request.urlopen(dl_req, timeout=60) as dl_resp:
            content = dl_resp.read()

        print("[*] Extracting N_m3u8DL-RE.exe...")
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            exe_names = [n for n in z.namelist() if n.endswith("N_m3u8DL-RE.exe")]
            if not exe_names:
                print("[-] Error: N_m3u8DL-RE.exe not found inside the zip archive.")
                return False

            target_exe = os.path.join(target_dir, "N_m3u8DL-RE.exe")
            with open(target_exe, "wb") as f:
                f.write(z.read(exe_names[0]))

        print(f"[+] SUCCESS: N_m3u8DL-RE installed to: {target_exe}")
        
        # Verify execution
        try:
            res = subprocess.run([target_exe, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            ver = res.stdout.strip() or res.stderr.strip()
            print(f"[+] Version info: {ver}")
        except Exception:
            pass

        return True

    except Exception as e:
        print(f"[-] Failed to download/install N_m3u8DL-RE: {e}")
        return False


def check_streamlink():
    """Check and update streamlink."""
    print("\n" + "=" * 72)
    print("               Streamlink Live Stream Engine")
    print("=" * 72)
    
    streamlink_bin = shutil.which("streamlink")
    if streamlink_bin:
        print(f"[+] Streamlink is already installed: {streamlink_bin}")
        print("[*] Checking for updates via pip...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "streamlink"], check=False)
        except Exception as e:
            print(f"[-] Pip update note: {e}")
    else:
        print("[-] Streamlink not found on PATH. Attempting to install via pip...")
        try:
            res = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "streamlink"])
            if res.returncode == 0:
                print("[+] Streamlink installed successfully!")
            else:
                print("[-] Pip install failed. You can also run: winget install streamlink")
        except Exception as e:
            print(f"[-] Install note: {e}")


def main():
    script_root = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(script_root, "bin")
    os.makedirs(target_dir, exist_ok=True)
    install_nm3u8(target_dir)
    check_streamlink()
    print("\n" + "=" * 72)
    print("                     ALL TOOLS UPDATED")
    print("=" * 72 + "\n")


if __name__ == "__main__":
    main()
