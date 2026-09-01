#!/usr/bin/env python3
"""
Universal Stream, HLS, DASH & Segmented Media Downloader
---------------------------------------------------------
Interactive multi-engine downloader supporting:
- High-Speed HLS / M3U8 & DASH / MPD (N_m3u8DL-RE)
- Live Stream Capturing (Streamlink / FFmpeg)
- Universal Web Video & Protected Streams (yt-dlp)
- Stream Structure & Sub-Track Inspection (FFprobe / N_m3u8DL-RE)
"""

import sys
import os
import subprocess
import shutil
import time
import re
import datetime

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def find_binary(name, extra_paths=None):
    """Find location of an executable binary."""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    search_dirs = [
        os.path.join(root_dir, "bin"),
        os.path.join(root_dir, "bin", "ffmpeg", "bin"),
        root_dir,
        r"C:\ffmpeg\bin",
        r"C:\Program Files\ffmpeg\bin",
        os.path.expanduser(r"~\ffmpeg\bin"),
        os.path.expanduser(r"~\Videos\yt-dlp-master"),
        r"C:\tools",
    ]
    if extra_paths:
        search_dirs = extra_paths + search_dirs

    exts = [".exe", ""] if sys.platform == "win32" else [""]
    
    for d in search_dirs:
        for ext in exts:
            candidate = os.path.join(d, f"{name}{ext}")
            if os.path.isfile(candidate):
                return candidate

    found = shutil.which(name)
    if found:
        return found

    return None


def get_environment():
    """Detect available backend engines and default save location."""
    env = {
        "nm3u8": find_binary("N_m3u8DL-RE"),
        "streamlink": find_binary("streamlink"),
        "ytdlp": find_binary("yt-dlp"),
        "ffmpeg": find_binary("ffmpeg"),
        "ffprobe": find_binary("ffprobe"),
        "save_dir": os.path.expanduser(r"~\Videos") if os.path.isdir(os.path.expanduser(r"~\Videos")) else os.getcwd()
    }
    # Check common yt-dlp path
    if not env["ytdlp"] and os.path.isfile(r"C:\Users\joao3\Videos\yt-dlp-master\yt-dlp.exe"):
        env["ytdlp"] = r"C:\Users\joao3\Videos\yt-dlp-master\yt-dlp.exe"

    return env


def parse_piped_url(raw_input):
    """
    Parse piped URL|Referer strings copied from browser extensions or user inputs.
    """
    raw_input = raw_input.strip().strip('"').strip("'")
    if "|" in raw_input:
        parts = raw_input.split("|", 1)
        url = parts[0].strip()
        referer = parts[1].strip()
        return url, referer
    return raw_input, None


def run_nm3u8(url, referer=None, custom_name=None, env=None):
    """Download HLS/DASH stream via N_m3u8DL-RE."""
    nm3u8 = env.get("nm3u8")
    ffmpeg = env.get("ffmpeg")
    save_dir = env.get("save_dir")

    if not nm3u8:
        print("\n[!] N_m3u8DL-RE is not installed.")
        ans = input("Would you like to install it now? (Y/n): ").strip().lower()
        if ans != "n":
            import update_stream_tools
            update_stream_tools.main()
            env["nm3u8"] = find_binary("N_m3u8DL-RE")
            nm3u8 = env.get("nm3u8")
            if not nm3u8:
                print("[-] Installation incomplete. Falling back to yt-dlp...")
                return run_ytdlp(url, referer, custom_name, env)
        else:
            return run_ytdlp(url, referer, custom_name, env)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_name = custom_name.strip() if (custom_name and custom_name.strip()) else f"Stream_{timestamp}"
    # Remove forbidden characters from filename
    out_name = re.sub(r'[\\/*?:"<>|]', '_', out_name)

    cmd = [
        nm3u8,
        url,
        "--save-dir", save_dir,
        "--save-name", out_name,
        "--thread-count", "16",
        "--download-retry-count", "5",
        "--auto-select",
        "--binary-merge"
    ]

    if ffmpeg:
        cmd.extend(["--ffmpeg-binary-path", ffmpeg, "-M", "format=mp4"])
    else:
        cmd.extend(["-M", "format=mp4"])

    if referer:
        cmd.extend([
            "-H", f"Referer: {referer}",
            "-H", f"Origin: {referer}",
            "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ])

    print("\n" + "=" * 72)
    print("      Starting High-Speed Stream Download (N_m3u8DL-RE)")
    print("=" * 72)
    print(f" URL:        {url}")
    if referer:
        print(f" Referer:    {referer}")
    print(f" Output:     {os.path.join(save_dir, out_name)}.mp4")
    print("=" * 72 + "\n")

    try:
        subprocess.run(cmd)
        print("\n[+] Download process finished.")
    except KeyboardInterrupt:
        print("\n[-] Download cancelled by user.")
    except Exception as e:
        print(f"\n[-] Error running N_m3u8DL-RE: {e}")


def run_streamlink(url, referer=None, custom_name=None, env=None):
    """Capture live stream via Streamlink or FFmpeg."""
    streamlink = env.get("streamlink")
    ffmpeg = env.get("ffmpeg")
    save_dir = env.get("save_dir")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_name = custom_name.strip() if (custom_name and custom_name.strip()) else f"Live_{timestamp}"
    out_name = re.sub(r'[\\/*?:"<>|]', '_', out_name)
    out_file = os.path.join(save_dir, f"{out_name}.mp4")

    print("\n" + "=" * 72)
    print("                    Live Stream Recording Mode")
    print("=" * 72)
    print(f" URL:        {url}")
    print(f" Output:     {out_file}")
    print(" NOTE: Press Ctrl+C in this window when you wish to stop recording.")
    print("=" * 72 + "\n")

    if streamlink:
        cmd = [streamlink, url, "best", "-o", out_file]
        if referer:
            cmd.extend(["--http-header", f"Referer={referer}"])
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\n[+] Live stream recording stopped.")
    elif ffmpeg:
        print("[*] Streamlink not found. Using FFmpeg direct stream capture...")
        cmd = [ffmpeg, "-y"]
        if referer:
            cmd.extend(["-headers", f"Referer: {referer}\r\n"])
        cmd.extend(["-i", url, "-c", "copy", out_file])
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\n[+] Stream recording stopped.")
    else:
        print("[-] Error: Neither Streamlink nor FFmpeg was found to record this stream.")


def run_ytdlp(url, referer=None, custom_name=None, env=None):
    """Download video/stream via yt-dlp."""
    ytdlp = env.get("ytdlp")
    ffmpeg = env.get("ffmpeg")
    save_dir = env.get("save_dir")

    if not ytdlp:
        print("[-] Error: yt-dlp executable was not found.")
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    template = f"{save_dir}/{custom_name}.%(ext)s" if custom_name else f"{save_dir}/%(title)s.%(ext)s"

    cmd = [
        ytdlp,
        "--newline",
        "-i",
        "--all-subs",
        "-o", template,
        "--hls-prefer-native",
        "-f", "bestvideo+bestaudio/best/b",
        "--remux-video", "mp4"
    ]

    if ffmpeg:
        cmd.extend(["--ffmpeg-location", os.path.dirname(ffmpeg)])

    if referer:
        cmd.extend([
            "--add-header", f"Referer: {referer}",
            "--add-header", f"Origin: {referer}"
        ])

    cmd.append(url)

    print("\n" + "=" * 72)
    print("                  Starting yt-dlp Stream Extractor")
    print("=" * 72)
    print(f" URL:        {url}")
    if referer:
        print(f" Referer:    {referer}")
    print("=" * 72 + "\n")

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n[-] Cancelled by user.")


def run_probe(url, referer=None, env=None):
    """Inspect and probe stream formats and tracks."""
    nm3u8 = env.get("nm3u8")
    ytdlp = env.get("ytdlp")
    ffprobe = env.get("ffprobe")

    print("\n" + "=" * 72)
    print("               Probing Stream Formats & Structure")
    print("=" * 72 + "\n")

    if nm3u8:
        print("[*] Probing manifest with N_m3u8DL-RE:")
        cmd = [nm3u8, url, "--no-log", "--write-meta-json=false"]
        if referer:
            cmd.extend(["-H", f"Referer: {referer}"])
        subprocess.run(cmd)
    elif ytdlp:
        print("[*] Querying formats with yt-dlp:")
        cmd = [ytdlp, "-F", url]
        if referer:
            cmd.extend(["--add-header", f"Referer: {referer}"])
        subprocess.run(cmd)
    elif ffprobe:
        print("[*] Querying stream with FFprobe:")
        cmd = [ffprobe, "-v", "error", "-show_entries", "stream=index,codec_name,codec_type,width,height,bit_rate", "-of", "json", url]
        subprocess.run(cmd)
    else:
        print("[-] No probing tool (N_m3u8DL-RE, yt-dlp, ffprobe) found.")


def main():
    while True:
        env = get_environment()

        print("\n" + "=" * 72)
        print("       UNIVERSAL STREAM, HLS & SEGMENTED MEDIA DOWNLOADER v1.0")
        print("=" * 72)
        print(" Detected Engine Backends:")
        print(f"  * N_m3u8DL-RE (Fast HLS/DASH) : {'[✓] ' + env['nm3u8'] if env['nm3u8'] else '[X] Not Installed (Choose 5)'}")
        print(f"  * Streamlink  (Live Streams)  : {'[✓] ' + env['streamlink'] if env['streamlink'] else '[X] Not Installed (Choose 5)'}")
        print(f"  * yt-dlp      (Universal)     : {'[✓] ' + env['ytdlp'] if env['ytdlp'] else '[-] Not Found'}")
        print(f"  * FFmpeg      (Muxer/Capture) : {'[✓] ' + env['ffmpeg'] if env['ffmpeg'] else '[-] Not Found'}")
        print(f" Save Directory: {env['save_dir']}")
        print("=" * 72)
        print("\nSelect Mode:")
        print(" 1. High-Speed HLS / DASH / M3U8 Downloader (Multi-Threaded N_m3u8DL-RE)")
        print(" 2. Live Stream Capture / Recorder (Streamlink or FFmpeg Live)")
        print(" 3. Universal yt-dlp Stream Downloader")
        print(" 4. Inspect / Probe Stream URL (View available resolutions & tracks)")
        print(" 5. Download / Update Stream Engine Tools (N_m3u8DL-RE & Streamlink)")
        print(" 6. Exit")

        choice = input("\nEnter choice (1-6) [Default 1]: ").strip() or "1"

        if choice == "6":
            break
        elif choice == "5":
            try:
                import update_stream_tools
                update_stream_tools.main()
            except Exception as e:
                print(f"[-] Updater error: {e}")
            input("\nPress ENTER to return to menu...")
            continue

        url_raw = input("\nEnter Stream URL (.m3u8, .mpd, live URL, or paste URL|Referer): ").strip()
        if not url_raw:
            print("[-] URL cannot be empty.")
            time.sleep(1)
            continue

        url, parsed_referer = parse_piped_url(url_raw)
        referer = parsed_referer
        if referer:
            print(f"[+] Auto-detected Referer: {referer}")
        else:
            custom_ref = input("Enter Referer URL (optional, press ENTER to skip): ").strip()
            referer = custom_ref if custom_ref else None

        if choice == "4":
            run_probe(url, referer=referer, env=env)
            input("\nPress ENTER to return to menu...")
            continue

        custom_name = input("Custom output filename (optional, press ENTER for auto-title): ").strip() or None

        if choice == "1":
            run_nm3u8(url, referer=referer, custom_name=custom_name, env=env)
        elif choice == "2":
            run_streamlink(url, referer=referer, custom_name=custom_name, env=env)
        elif choice == "3":
            run_ytdlp(url, referer=referer, custom_name=custom_name, env=env)

        input("\nPress ENTER to continue...")


if __name__ == "__main__":
    main()
