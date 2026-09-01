# ⚡ Power Tools — media and other automation v1.0

A curated collection of media automation, video processing, stream extraction, and Windows power utilities.

## 🖥️ Desktop Application Hub

Launch the modern **CustomTkinter GUI** that unifies all tools into a single desktop dashboard:
* **[run_ui.cmd](run_ui.cmd)** / **[app.py](app.py)** — One-click launcher with auto-dependency verification, dark/light themes, live streaming terminal logs, and threaded non-blocking execution.

---

## 🌐 Stream & Video Downloaders

| Tool | Format | Description |
| :--- | :--- | :--- |
| **[downloader.bat](downloader.bat)** | `.bat` | General `yt-dlp` video downloader with auto-detected `URL|Referer` format support, cookie handling, and MP4 remuxing. |
| **[downloader_proxy.bat](downloader_proxy.bat)** | `.bat` | `yt-dlp` video downloader configured with SOCKS5 / HTTP proxy support. |
| **[download_channel_playlist.cmd](download_channel_playlist.cmd)** | `.cmd` | **Channel, Playlist & Course Archiver**. Designed for whole YouTube playlists/channels with ordered index numbering (`01 - Title.mp4`), date prefixing, embedded subtitles, and automatic archive tracking (`download_archive.txt`) to only download new videos on subsequent runs. |
| **[download_audio.cmd](download_audio.cmd)** | `.cmd` | Dedicated **audio & music downloader** powered by `yt-dlp` and `ffmpeg`. Supports MP3 (320k/192k), M4A, FLAC, OPUS, WAV, automatic thumbnail/cover art embedding, ID3 tags & metadata, chapter markers, optional chapter splitting, and batch `.txt` URL lists. |
| **[stream_downloader.cmd](stream_downloader.cmd)** | `.cmd` | Universal **HLS (`.m3u8`)**, **DASH (`.mpd`)**, and live stream downloader. Leverages `N_m3u8DL-RE` for 16-thread segment fetching, `Streamlink` for live recording, and `yt-dlp` fallback with custom headers/referer/cookies. |
| **[update_stream_tools.bat](update_stream_tools.bat)** | `.bat` | One-click updater/installer for portable `N_m3u8DL-RE` and `Streamlink` into `./bin/`. |
| **[update_ffmpeg.bat](update_ffmpeg.bat)** | `.bat` | Automated Git-build updater for FFmpeg essentials into `./bin/`. |
| **[update_yt-dlp.bat](update_yt-dlp.bat)** | `.bat` | Self-updater and installer for `yt-dlp` into `./bin/`. |

---

## 🚀 General File Downloader

| Tool | Format | Description |
| :--- | :--- | :--- |
| **[aria2_downloader.cmd](aria2_downloader.cmd)** | `.cmd` | **16-Connection Turbo File Accelerator**. Uses portable `aria2c` to split direct downloads (.zip, .iso, Google Drive, direct links) into 16–32 parallel streams with auto-resume, piped `URL|Referer` support, and batch `.txt` input. |
| **[update_aria2.bat](update_aria2.bat)** | `.bat` | One-click updater/installer for portable `aria2c.exe` into `./bin/`. |

---

## 🎬 Video & Media Processing Tools

| Tool | Format | Description |
| :--- | :--- | :--- |
| **[video_compressor.cmd](video_compressor.cmd)** / **[video_compressor.py](video_compressor.py)** | `.cmd` / `.py` | **AV1 / HEVC Smart Video Compressor**. Features VMAF/CRF sample benchmarking, preset quality profiles (Archival, High, Balanced, Compact), target file size mode (e.g. 50MB), audio passthrough or compression, NVIDIA NVENC GPU acceleration, and batch folder processing. |
| **[video_converter.cmd](video_converter.cmd)** | `.cmd` | Simple resolution downscaler / converter (360p, 480p, 720p, 1080p). |
| **[cut_video.cmd](cut_video.cmd)** | `.cmd` | Interactive video trimmer and splitter using FFmpeg keyframe/lossless or re-encode cutting. |
| **[video_joiner.cmd](video_joiner.cmd)** | `.cmd` | Lossless concatenation and joining of multiple video segments. |
| **[video_snapshots.cmd](video_snapshots.cmd)** | `.cmd` | Video contact sheet generator, thumbnail grids, interval frame extraction, or high-res stills. |
| **[video_to_gif.cmd](video_to_gif.cmd)** | `.cmd` | High-quality **GIF and Animated WebP converter** with two-pass `palettegen`/`paletteuse` filtering, custom trimming, aspect-ratio scaling (480p, 720p, custom), FPS selection, and dithering optimization. |
| **[extract_audio.cmd](extract_audio.cmd)** | `.cmd` | Extracts individual audio tracks or converts streams to MP3/AAC/FLAC/WAV. |
| **[subtitle_generator.cmd](subtitle_generator.cmd)** / **[subtitle_generator.py](subtitle_generator.py)** | `.cmd` / `.py` | GPU-accelerated subtitle generator using `faster-whisper` / CTranslate2 with multi-language detection, translation, and SRT export. |

---

## 🛠️ System Utilities

| Tool | Format | Description |
| :--- | :--- | :--- |
| **[FixBrightness.bat](FixBrightness.bat)** | `.bat` | Resets Windows display driver instances via `pnputil` to restore display brightness control. |
| **[clean_docker.txt](clean_docker.txt)** | `.txt` | Commands for pruning Docker containers/volumes and compacting WSL2 `docker_data.vhdx` via `diskpart`. |