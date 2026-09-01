# other_tools

A curated collection of media automation, video processing, stream extraction, and Windows power utilities.

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

## 🌐 Stream & Video Downloaders

| Tool | Format | Description |
| :--- | :--- | :--- |
| **[download_audio.cmd](download_audio.cmd)** | `.cmd` | Dedicated **audio & music downloader** powered by `yt-dlp` and `ffmpeg`. Supports MP3 (320k/192k), M4A, FLAC, OPUS, WAV, automatic thumbnail/cover art embedding, ID3 tags & metadata, chapter markers, optional chapter splitting, and batch `.txt` URL lists. |
| **[stream_downloader.cmd](stream_downloader.cmd)** | `.cmd` | Universal **HLS (`.m3u8`)**, **DASH (`.mpd`)**, and live stream downloader. Leverages `N_m3u8DL-RE` for 16-thread segment fetching, `Streamlink` for live recording, and `yt-dlp` fallback with custom headers/referer/cookies. |
| **[downloader.bat](downloader.bat)** | `.bat` | General `yt-dlp` video downloader with auto-detected `URL|Referer` format support and cookie handling. |
| **[downloader_proxy.bat](downloader_proxy.bat)** | `.bat` | `yt-dlp` downloader configured with proxy support. |
| **[update_stream_tools.bat](update_stream_tools.bat)** | `.bat` | One-click updater/installer for portable `N_m3u8DL-RE` and `Streamlink`. |
| **[update_ffmpeg.bat](update_ffmpeg.bat)** | `.bat` | Automated Git-build updater for FFmpeg essentials. |
| **[update_yt-dlp.bat](update_yt-dlp.bat)** | `.bat` | Self-updater for `yt-dlp`. |

---

## 🛠️ System Utilities

| Tool | Format | Description |
| :--- | :--- | :--- |
| **[FixBrightness.bat](FixBrightness.bat)** | `.bat` | Resets Windows display driver instances via `pnputil` to restore display brightness control. |
| **[clean_docker.txt](clean_docker.txt)** | `.txt` | Commands for pruning Docker containers/volumes and compacting WSL2 `docker_data.vhdx` via `diskpart`. |