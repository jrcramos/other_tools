"""
Automated downloader and installer for portable aria2c.exe
Extracts aria2c.exe into ./bin/
"""
import os
import sys
import zipfile
import urllib.request
import json

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(ROOT_DIR, "bin")
os.makedirs(BIN_DIR, exist_ok=True)

TARGET_EXE = os.path.join(BIN_DIR, "aria2c.exe")

def get_latest_aria2_zip_url():
    # Try fetching from GitHub API first
    api_url = "https://api.github.com/repos/aria2/aria2/releases/latest"
    req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            for asset in data.get("assets", []):
                name = asset.get("name", "").lower()
                if "win-64bit" in name and name.endswith(".zip"):
                    return asset.get("browser_download_url")
    except Exception as e:
        print(f"[!] GitHub API lookup fallback: {e}")

    # Fallback to direct stable release
    return "https://github.com/aria2/aria2/releases/download/release-1.37.0/aria2-1.37.0-win-64bit-build1.zip"

def download_and_install():
    url = get_latest_aria2_zip_url()
    print(f"[*] Downloading aria2 from: {url}")
    zip_temp = os.path.join(BIN_DIR, "aria2_temp.zip")

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp, open(zip_temp, "wb") as f:
        total_len = resp.getheader("Content-Length")
        total_len = int(total_len) if total_len else None
        downloaded = 0
        while True:
            chunk = resp.read(65536)
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
            if total_len:
                pct = (downloaded / total_len) * 100
                print(f"\rDownloading: {downloaded / (1024*1024):.1f} MB / {total_len / (1024*1024):.1f} MB ({pct:.1f}%)", end="", flush=True)

    print("\n[*] Extracting aria2c.exe...")
    with zipfile.ZipFile(zip_temp, "r") as zf:
        for name in zf.namelist():
            if name.endswith("aria2c.exe"):
                with zf.open(name) as src, open(TARGET_EXE, "wb") as dst:
                    dst.write(src.read())
                print(f"[+] Successfully installed aria2c to: {TARGET_EXE}")
                break

    if os.path.exists(zip_temp):
        try:
            os.remove(zip_temp)
        except Exception:
            pass

if __name__ == "__main__":
    download_and_install()
