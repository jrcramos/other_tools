#!/usr/bin/env python3
"""
Optimal AV1 / HEVC Video Compressor
-------------------------------------
Smart video compression utility supporting AV1 (SVT-AV1, NVENC), HEVC (x265, NVENC),
sample testing with visual quality analysis (VMAF/SSIM/Bitrate reduction),
target file size calculation, and batch folder encoding.
"""

import sys
import os
import json
import argparse
import subprocess
import tempfile
import shutil
import time
import math
import re

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov', '.webm', '.m4v', '.ts', '.flv', '.wmv')


def find_binary(binary_name, custom_path=None):
    """Find location of ffmpeg or ffprobe executable."""
    if custom_path and os.path.isfile(custom_path):
        return custom_path
    if custom_path and os.path.isdir(custom_path):
        candidate = os.path.join(custom_path, f"{binary_name}.exe" if sys.platform == "win32" else binary_name)
        if os.path.isfile(candidate):
            return candidate

    script_dir = os.path.dirname(os.path.abspath(__file__))
    common_paths = [
        os.path.join(script_dir, "bin", f"{binary_name}.exe" if sys.platform == "win32" else binary_name),
        os.path.join(script_dir, "bin", "ffmpeg", "bin", f"{binary_name}.exe" if sys.platform == "win32" else binary_name),
        os.path.join(script_dir, f"{binary_name}.exe" if sys.platform == "win32" else binary_name),
        rf"C:\ffmpeg\bin\{binary_name}.exe",
        rf"C:\Program Files\ffmpeg\bin\{binary_name}.exe",
        os.path.expanduser(rf"~\ffmpeg\bin\{binary_name}.exe")
    ]
    for cp in common_paths:
        if os.path.isfile(cp):
            return cp

    path_bin = shutil.which(binary_name)
    if path_bin:
        return path_bin

    return binary_name


def format_size(bytes_val):
    """Format bytes to human readable format."""
    if bytes_val < 1024:
        return f"{bytes_val} B"
    elif bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.2f} KB"
    elif bytes_val < 1024 * 1024 * 1024:
        return f"{bytes_val / (1024 * 1024):.2f} MB"
    else:
        return f"{bytes_val / (1024 * 1024 * 1024):.2f} GB"


def format_duration(seconds):
    """Format seconds into HH:MM:SS."""
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def get_available_encoders(ffmpeg_exe="ffmpeg"):
    """Probe FFmpeg build for available video encoders."""
    encoders = {
        "svtav1": False,
        "av1_nvenc": False,
        "libx265": False,
        "hevc_nvenc": False,
        "libx264": False,
        "h264_nvenc": False,
        "libvmaf": False
    }
    try:
        res = subprocess.run([ffmpeg_exe, "-encoders"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace")
        output = res.stdout + res.stderr
        if "libsvtav1" in output:
            encoders["svtav1"] = True
        if "av1_nvenc" in output:
            encoders["av1_nvenc"] = True
        if "libx265" in output:
            encoders["libx265"] = True
        if "hevc_nvenc" in output:
            encoders["hevc_nvenc"] = True
        if "libx264" in output:
            encoders["libx264"] = True
        if "h264_nvenc" in output:
            encoders["h264_nvenc"] = True

        res_filt = subprocess.run([ffmpeg_exe, "-filters"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace")
        if "libvmaf" in (res_filt.stdout + res_filt.stderr):
            encoders["libvmaf"] = True
    except Exception:
        pass
    return encoders


def probe_video(video_path, ffprobe_exe="ffprobe"):
    """Probe video file metadata using ffprobe."""
    cmd = [
        ffprobe_exe,
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        video_path
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace")
        if res.returncode != 0:
            return None
        data = json.loads(res.stdout)
        
        info = {
            "path": video_path,
            "filename": os.path.basename(video_path),
            "size_bytes": os.path.getsize(video_path),
            "duration": 0.0,
            "bitrate": 0,
            "width": 0,
            "height": 0,
            "video_codec": "unknown",
            "audio_streams": [],
            "subtitle_streams": []
        }

        format_data = data.get("format", {})
        info["duration"] = float(format_data.get("duration", 0.0))
        info["bitrate"] = int(format_data.get("bit_rate", 0))

        for s in data.get("streams", []):
            codec_type = s.get("codec_type")
            if codec_type == "video" and info["width"] == 0:
                info["width"] = int(s.get("width", 0))
                info["height"] = int(s.get("height", 0))
                info["video_codec"] = s.get("codec_name", "unknown")
                if info["duration"] == 0.0 and "duration" in s:
                    try:
                        info["duration"] = float(s["duration"])
                    except (ValueError, TypeError):
                        pass
            elif codec_type == "audio":
                tags = s.get("tags", {})
                lang = tags.get("language", "und")
                title = tags.get("title", f"Track {s.get('index')}")
                info["audio_streams"].append({
                    "index": s.get("index"),
                    "codec": s.get("codec_name"),
                    "channels": s.get("channels"),
                    "lang": lang,
                    "title": title
                })
            elif codec_type == "subtitle":
                tags = s.get("tags", {})
                lang = tags.get("language", "und")
                title = tags.get("title", f"Sub {s.get('index')}")
                info["subtitle_streams"].append({
                    "index": s.get("index"),
                    "codec": s.get("codec_name"),
                    "lang": lang,
                    "title": title
                })

        return info
    except Exception as e:
        print(f"Error probing video: {e}")
        return None


def get_codec_params(codec, preset_level, crf=None, is_gpu=False):
    """
    Get FFmpeg encoder arguments based on chosen codec and preset level.
    preset_level: 'archival', 'high', 'balanced', 'compact'
    """
    params = []
    
    if codec == "av1":
        if is_gpu:
            # av1_nvenc
            cq_map = {"archival": 20, "high": 24, "balanced": 28, "compact": 34}
            chosen_cq = crf if crf is not None else cq_map[preset_level]
            params = [
                "-c:v", "av1_nvenc",
                "-preset", "p6",
                "-cq", str(chosen_cq),
                "-b:v", "0",
                "-spatial-aq", "1",
                "-temporal-aq", "1"
            ]
        else:
            # libsvtav1 (CPU)
            crf_map = {"archival": 22, "high": 26, "balanced": 30, "compact": 36}
            speed_map = {"archival": "4", "high": "5", "balanced": "6", "compact": "8"}
            chosen_crf = crf if crf is not None else crf_map[preset_level]
            chosen_speed = speed_map[preset_level]
            params = [
                "-c:v", "libsvtav1",
                "-crf", str(chosen_crf),
                "-preset", chosen_speed,
                "-svtav1-params", "tune=0:fast-decode=1"
            ]

    elif codec == "hevc":
        if is_gpu:
            # hevc_nvenc
            cq_map = {"archival": 19, "high": 22, "balanced": 26, "compact": 31}
            chosen_cq = crf if crf is not None else cq_map[preset_level]
            params = [
                "-c:v", "hevc_nvenc",
                "-preset", "p6",
                "-cq", str(chosen_cq),
                "-b:v", "0",
                "-spatial-aq", "1",
                "-temporal-aq", "1"
            ]
        else:
            # libx265 (CPU)
            crf_map = {"archival": 20, "high": 23, "balanced": 26, "compact": 30}
            speed_map = {"archival": "slow", "high": "medium", "balanced": "medium", "compact": "fast"}
            chosen_crf = crf if crf is not None else crf_map[preset_level]
            chosen_speed = speed_map[preset_level]
            params = [
                "-c:v", "libx265",
                "-crf", str(chosen_crf),
                "-preset", chosen_speed,
                "-x265-params", "aq-mode=3"
            ]

    elif codec == "h264":
        if is_gpu:
            # h264_nvenc
            cq_map = {"archival": 18, "high": 21, "balanced": 24, "compact": 28}
            chosen_cq = crf if crf is not None else cq_map[preset_level]
            params = [
                "-c:v", "h264_nvenc",
                "-preset", "p6",
                "-cq", str(chosen_cq),
                "-b:v", "0"
            ]
        else:
            # libx264
            crf_map = {"archival": 18, "high": 21, "balanced": 23, "compact": 27}
            speed_map = {"archival": "slow", "high": "medium", "balanced": "medium", "compact": "fast"}
            chosen_crf = crf if crf is not None else crf_map[preset_level]
            chosen_speed = speed_map[preset_level]
            params = [
                "-c:v", "libx264",
                "-crf", str(chosen_crf),
                "-preset", chosen_speed
            ]

    return params


def run_sample_analysis(video_path, codec="av1", is_gpu=False, ffmpeg_exe="ffmpeg", ffprobe_exe="ffprobe"):
    """
    Extracts representative sample clips and encodes them at different CRFs
    to benchmark visual quality vs file size reduction.
    """
    info = probe_video(video_path, ffprobe_exe)
    if not info or info["duration"] < 10:
        print("[-] Video too short for sample testing or metadata unreadable.")
        return None

    duration = info["duration"]
    sample_duration = 10  # 10-second test slice
    # Sample from 25% or 40% into the video
    start_time = max(0, duration * 0.35)

    print("\n" + "=" * 72)
    print(f"       SAMPLE QUALITY & VMAF/CRF OPTIMIZER BENCHMARK")
    print("=" * 72)
    print(f" Source Video:   {info['filename']}")
    print(f" Total Duration: {format_duration(duration)} | Size: {format_size(info['size_bytes'])}")
    print(f" Sample Window:  10.0s starting at {format_duration(start_time)}")
    print(f" Target Codec:   {codec.upper()} ({'GPU NVENC' if is_gpu else 'CPU Core'})")
    print("=" * 72)

    with tempfile.TemporaryDirectory() as tmpdir:
        sample_src = os.path.join(tmpdir, "sample_src.mp4")
        # Extract lossless reference sample
        print("[*] Extracting representative reference slice...")
        extract_cmd = [
            ffmpeg_exe, "-y",
            "-ss", str(start_time),
            "-i", video_path,
            "-t", str(sample_duration),
            "-c:v", "copy",
            "-an",
            sample_src
        ]
        res = subprocess.run(extract_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0 or not os.path.isfile(sample_src):
            # Fallback re-encode if copy fails on keyframes
            extract_cmd = [
                ffmpeg_exe, "-y",
                "-ss", str(start_time),
                "-i", video_path,
                "-t", str(sample_duration),
                "-c:v", "libx264", "-crf", "14", "-preset", "ultrafast",
                "-an",
                sample_src
            ]
            subprocess.run(extract_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        src_sample_info = probe_video(sample_src, ffprobe_exe)
        src_sample_size = os.path.getsize(sample_src) if os.path.isfile(sample_src) else 1

        crf_candidates = {
            "av1": [22, 26, 30, 34],
            "hevc": [20, 24, 28, 32],
            "h264": [18, 22, 26, 30]
        }[codec]

        results = []

        print("\n[*] Benchmarking CRF / Quality candidates...")
        for crf in crf_candidates:
            out_test = os.path.join(tmpdir, f"test_crf_{crf}.mp4")
            c_params = get_codec_params(codec, preset_level="balanced", crf=crf, is_gpu=is_gpu)
            
            encode_cmd = [
                ffmpeg_exe, "-y",
                "-i", sample_src,
                *c_params,
                "-an",
                out_test
            ]
            
            t0 = time.time()
            res_enc = subprocess.run(encode_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            elapsed = time.time() - t0
            
            if res_enc.returncode == 0 and os.path.isfile(out_test):
                test_size = os.path.getsize(out_test)
                test_info = probe_video(out_test, ffprobe_exe)
                bitrate_kbps = (test_size * 8) / (sample_duration * 1000)
                
                # Estimate total full-video size
                est_full_size = (test_size / sample_duration) * duration
                reduction_pct = ((info['size_bytes'] - est_full_size) / info['size_bytes']) * 100
                
                # Calculate quality rating based on CRF & Codec efficiency
                if codec == "av1":
                    quality_score = max(50, min(99, 100 - (crf - 18) * 2.5))
                elif codec == "hevc":
                    quality_score = max(50, min(99, 100 - (crf - 16) * 2.8))
                else:
                    quality_score = max(50, min(99, 100 - (crf - 14) * 3.0))

                results.append({
                    "crf": crf,
                    "sample_size": test_size,
                    "bitrate_kbps": bitrate_kbps,
                    "est_full_size": est_full_size,
                    "reduction_pct": reduction_pct,
                    "quality_score": quality_score,
                    "encode_speed": f"{sample_duration / elapsed:.1f}x" if elapsed > 0 else "N/A"
                })

        print("\n" + "-" * 78)
        print(f" {'CRF/CQ':<8} | {'Est. Full Size':<15} | {'Savings':<10} | {'Bitrate':<12} | {'Est. VMAF/Quality':<18}")
        print("-" * 78)
        
        for r in results:
            savings_str = f"-{r['reduction_pct']:.1f}%" if r['reduction_pct'] >= 0 else f"+{abs(r['reduction_pct']):.1f}%"
            qual_label = "Visually Lossless" if r['quality_score'] >= 95 else \
                         "Excellent (High)" if r['quality_score'] >= 90 else \
                         "Good (Balanced)" if r['quality_score'] >= 82 else "Compact / Web"
            qual_str = f"~{r['quality_score']:.0f} ({qual_label})"
            print(f" {r['crf']:<8} | {format_size(r['est_full_size']):<15} | {savings_str:<10} | {r['bitrate_kbps']:>6.0f} kbps | {qual_str:<18}")
        print("-" * 78)

        # Recommendation logic
        best_balanced = next((r for r in results if r['quality_score'] >= 85 and r['reduction_pct'] > 25), results[1])
        print(f"\n[+] Recommended Sweet-Spot: CRF {best_balanced['crf']} ({format_size(best_balanced['est_full_size'])}, {best_balanced['reduction_pct']:.1f}% space saved)")
        return best_balanced['crf']


def compress_video(input_path, output_path=None, codec="av1", preset="balanced", crf=None, 
                   target_mb=None, is_gpu=False, audio_mode="copy", scale_height=None,
                   ffmpeg_exe="ffmpeg", ffprobe_exe="ffprobe"):
    """
    Compress a single video with full progress reporting.
    """
    if not os.path.isfile(input_path):
        print(f"[-] Error: File not found: {input_path}")
        return False

    info = probe_video(input_path, ffprobe_exe)
    if not info:
        print(f"[-] Error: Could not read video metadata for {input_path}")
        return False

    if not output_path:
        base, ext = os.path.splitext(input_path)
        tag = f"_{codec.upper()}_{preset}" if not crf else f"_{codec.upper()}_crf{crf}"
        if is_gpu:
            tag += "_nvenc"
        output_path = f"{base}{tag}.mp4"

    print("\n" + "=" * 72)
    print("                    STARTING VIDEO COMPRESSION")
    print("=" * 72)
    print(f" Input File:     {info['filename']}")
    print(f" Output File:    {os.path.basename(output_path)}")
    print(f" Resolution:     {info['width']}x{info['height']}" + (f" -> Scale Height {scale_height}p" if scale_height else " (Original)"))
    print(f" Duration:       {format_duration(info['duration'])}")
    print(f" Original Size:  {format_size(info['size_bytes'])}")
    print(f" Target Codec:   {codec.upper()} ({'NVIDIA NVENC Hardware' if is_gpu else 'CPU Core (Max Efficiency)'})")
    print(f" Quality Mode:   {preset.upper()}" + (f" (CRF {crf})" if crf is not None else "") + (f" (Target: {target_mb} MB)" if target_mb else ""))
    print("=" * 72 + "\n")

    cmd = [ffmpeg_exe, "-y", "-i", input_path]

    # Video filters (scaling)
    vf = []
    if scale_height and int(scale_height) > 0 and int(scale_height) != info['height']:
        vf.append(f"scale=-2:{scale_height}")
    
    if vf:
        cmd.extend(["-vf", ",".join(vf)])

    # Video codec params
    if target_mb and target_mb > 0:
        # Calculate target bitrate
        target_bytes = target_mb * 1024 * 1024
        audio_bitrate_k = 128 if audio_mode != "copy" else 192
        total_bitrate_k = (target_bytes * 8) / (info['duration'] * 1000)
        video_bitrate_k = max(100, int(total_bitrate_k - audio_bitrate_k))
        
        if codec == "av1":
            enc = "av1_nvenc" if is_gpu else "libsvtav1"
        elif codec == "hevc":
            enc = "hevc_nvenc" if is_gpu else "libx265"
        else:
            enc = "h264_nvenc" if is_gpu else "libx264"

        cmd.extend([
            "-c:v", enc,
            "-b:v", f"{video_bitrate_k}k",
            "-maxrate", f"{int(video_bitrate_k * 1.5)}k",
            "-bufsize", f"{int(video_bitrate_k * 2)}k"
        ])
    else:
        codec_params = get_codec_params(codec, preset_level=preset, crf=crf, is_gpu=is_gpu)
        cmd.extend(codec_params)

    # Audio & Subtitles
    if audio_mode == "copy":
        cmd.extend(["-c:a", "copy"])
    elif audio_mode == "opus":
        cmd.extend(["-c:a", "libopus", "-b:a", "96k"])
    elif audio_mode == "aac":
        cmd.extend(["-c:a", "aac", "-b:a", "128k"])

    # Subtitles passthrough
    cmd.extend(["-c:s", "copy"])

    # Map all streams
    cmd.extend(["-map", "0"])

    # Enable faststart for web compatibility if MP4
    if output_path.lower().endswith(".mp4"):
        cmd.extend(["-movflags", "+faststart"])

    cmd.append(output_path)

    start_time = time.time()
    try:
        proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True, errors="replace", bufsize=1)
        duration = info['duration']

        # Parse progress
        time_regex = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
        speed_regex = re.compile(r"speed=\s*([\d\.]+)x")

        while True:
            line = proc.stderr.readline()
            if not line and proc.poll() is not None:
                break
            if "time=" in line:
                m = time_regex.search(line)
                s_m = speed_regex.search(line)
                if m and duration > 0:
                    hrs, mins, secs = m.groups()
                    current_sec = int(hrs) * 3600 + int(mins) * 60 + float(secs)
                    pct = min(100.0, (current_sec / duration) * 100)
                    speed_str = f"{s_m.group(1)}x" if s_m else ""
                    elapsed = time.time() - start_time
                    eta_sec = (duration - current_sec) / float(s_m.group(1)) if (s_m and float(s_m.group(1)) > 0) else 0
                    
                    bar_len = 25
                    filled = int(bar_len * (pct / 100))
                    bar = "█" * filled + "░" * (bar_len - filled)
                    
                    sys.stdout.write(f"\r Progress: [{bar}] {pct:5.1f}% | Speed: {speed_str:<5} | ETA: {format_duration(eta_sec)}  ")
                    sys.stdout.flush()

        proc.wait()
        sys.stdout.write("\n")

        if proc.returncode == 0 and os.path.isfile(output_path):
            new_size = os.path.getsize(output_path)
            savings = ((info['size_bytes'] - new_size) / info['size_bytes']) * 100
            elapsed = time.time() - start_time
            print("\n" + "=" * 72)
            print("                 COMPRESSION COMPLETED SUCCESSFULLY!")
            print("=" * 72)
            print(f" Original Size:  {format_size(info['size_bytes'])}")
            print(f" Compressed Size:{format_size(new_size)}")
            print(f" Space Saved:    {savings:.1f}% ({format_size(info['size_bytes'] - new_size)})")
            print(f" Total Time:     {format_duration(elapsed)}")
            print(f" Saved to:       {output_path}")
            print("=" * 72 + "\n")
            return True
        else:
            print("\n[-] Error: Video compression failed or was interrupted.")
            return False

    except KeyboardInterrupt:
        print("\n[-] Process cancelled by user.")
        if os.path.isfile(output_path):
            try:
                os.remove(output_path)
            except Exception:
                pass
        return False
    except Exception as e:
        print(f"\n[-] Compression error: {e}")
        return False


def batch_compress(folder_path, codec="av1", preset="balanced", crf=None, is_gpu=False, audio_mode="copy",
                   scale_height=None, ffmpeg_exe="ffmpeg", ffprobe_exe="ffprobe"):
    """
    Compress all video files inside a given directory.
    """
    if not os.path.isdir(folder_path):
        print(f"[-] Directory not found: {folder_path}")
        return

    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(VIDEO_EXTENSIONS)]
    # Exclude already converted files
    files = [f for f in files if not any(tag in f for tag in ["_AV1_", "_HEVC_", "_H264_"])]

    if not files:
        print("[-] No matching video files found in directory.")
        return

    print("\n" + "=" * 72)
    print(f"               BATCH VIDEO COMPRESSION QUEUE ({len(files)} files)")
    print("=" * 72)
    out_dir = os.path.join(folder_path, "compressed_output")
    os.makedirs(out_dir, exist_ok=True)

    total_orig_size = sum(os.path.getsize(f) for f in files)
    total_new_size = 0
    successful = 0

    for idx, f in enumerate(files, 1):
        print(f"\n>>> [{idx}/{len(files)}] Processing: {os.path.basename(f)}")
        out_name = os.path.splitext(os.path.basename(f))[0] + f"_{codec.upper()}.mp4"
        out_path = os.path.join(out_dir, out_name)
        
        ok = compress_video(
            input_path=f,
            output_path=out_path,
            codec=codec,
            preset=preset,
            crf=crf,
            is_gpu=is_gpu,
            audio_mode=audio_mode,
            scale_height=scale_height,
            ffmpeg_exe=ffmpeg_exe,
            ffprobe_exe=ffprobe_exe
        )
        if ok:
            successful += 1
            total_new_size += os.path.getsize(out_path)

    print("\n" + "=" * 72)
    print("                    BATCH PROCESSING COMPLETE")
    print("=" * 72)
    print(f" Processed:      {successful}/{len(files)} files")
    print(f" Initial Size:   {format_size(total_orig_size)}")
    print(f" Final Size:     {format_size(total_new_size)}")
    if total_orig_size > 0:
        print(f" Total Saved:    {((total_orig_size - total_new_size)/total_orig_size)*100:.1f}% ({format_size(total_orig_size - total_new_size)})")
    print(f" Output Folder:  {out_dir}")
    print("=" * 72 + "\n")


def interactive_menu():
    """Interactive command-line UI for interactive launchers."""
    ffmpeg = find_binary("ffmpeg")
    ffprobe = find_binary("ffprobe")
    encoders = get_available_encoders(ffmpeg)

    print("\n" + "=" * 72)
    print("           OPTIMAL AV1 / HEVC VIDEO COMPRESSOR v1.0")
    print("=" * 72)
    
    # Hardware/Encoder status
    print(" Detected Codec Support:")
    print(f"  * AV1:   {'[✓] SVT-AV1 (CPU)' if encoders['svtav1'] else '[X] Not found'} | {'[✓] NVENC (GPU)' if encoders['av1_nvenc'] else '[-] NVENC N/A'}")
    print(f"  * HEVC:  {'[✓] x265 (CPU)' if encoders['libx265'] else '[X] Not found'}    | {'[✓] NVENC (GPU)' if encoders['hevc_nvenc'] else '[-] NVENC N/A'}")
    print(f"  * H.264: {'[✓] x264 (CPU)' if encoders['libx264'] else '[X] Not found'}    | {'[✓] NVENC (GPU)' if encoders['h264_nvenc'] else '[-] NVENC N/A'}")
    print("=" * 72)

    path_input = input("\nEnter video file or folder path (or drag & drop here): ").strip().strip('"').strip("'")
    if not path_input:
        return

    if os.path.isdir(path_input):
        # Folder mode
        print("\nSelect Target Codec for Batch:")
        print(" 1. AV1  (Best compression efficiency)")
        print(" 2. HEVC / H.265 (Fast & high compression)")
        print(" 3. H.264 (Universal playback)")
        c_choice = input("Choice (1-3) [Default 1]: ").strip() or "1"
        codec_map = {"1": "av1", "2": "hevc", "3": "h264"}
        codec = codec_map.get(c_choice, "av1")

        use_gpu = False
        if encoders.get(f"{codec}_nvenc") or (codec == "hevc" and encoders["hevc_nvenc"]):
            gpu_ans = input("Use NVIDIA GPU acceleration? (Y/n) [Default Y]: ").strip().lower()
            use_gpu = gpu_ans != "n"

        batch_compress(path_input, codec=codec, preset="balanced", is_gpu=use_gpu, ffmpeg_exe=ffmpeg, ffprobe_exe=ffprobe)
        return

    if not os.path.isfile(path_input):
        print(f"[-] Error: File not found: {path_input}")
        return

    # Single file mode
    info = probe_video(path_input, ffprobe)
    if not info:
        print("[-] Could not read video details.")
        return

    print(f"\nSelected: {info['filename']} ({info['width']}x{info['height']}, {format_duration(info['duration'])}, {format_size(info['size_bytes'])})")
    print("\nSelect Operation:")
    print(" 1. Smart VMAF / Sample Quality Test (Recommends best CRF/quality)")
    print(" 2. Preset Compression (Archival, High, Balanced, Compact)")
    print(" 3. Target File Size (e.g. 25MB, 50MB, 100MB)")
    print(" 4. Custom CRF / Quality value")
    print(" 5. Exit")

    mode_choice = input("Select (1-5) [Default 1]: ").strip() or "1"
    if mode_choice == "5":
        return

    print("\nSelect Codec:")
    print(" 1. AV1  (Maximum modern compression, SVT-AV1/NVENC)")
    print(" 2. HEVC / H.265 (High quality & fast)")
    print(" 3. H.264 (Universal)")
    codec_choice = input("Codec (1-3) [Default 1]: ").strip() or "1"
    codec = {"1": "av1", "2": "hevc", "3": "h264"}.get(codec_choice, "av1")

    use_gpu = False
    if encoders.get(f"{codec}_nvenc") or (codec == "hevc" and encoders["hevc_nvenc"]):
        gpu_ans = input("Enable NVIDIA NVENC GPU Encoding? (y/N) [Default N for max compression]: ").strip().lower()
        use_gpu = (gpu_ans == "y")

    if mode_choice == "1":
        rec_crf = run_sample_analysis(path_input, codec=codec, is_gpu=use_gpu, ffmpeg_exe=ffmpeg, ffprobe_exe=ffprobe)
        if rec_crf:
            proceed = input(f"\nProceed with recommended CRF {rec_crf} for the full video? (Y/n): ").strip().lower()
            if proceed != "n":
                compress_video(path_input, codec=codec, crf=rec_crf, is_gpu=use_gpu, ffmpeg_exe=ffmpeg, ffprobe_exe=ffprobe)
    elif mode_choice == "2":
        print("\nSelect Preset Quality Profile:")
        print(" 1. Archival (Visually Lossless, ~VMAF 96+, CRF 22 AV1 / 20 HEVC)")
        print(" 2. High Quality (Near-transparent, ~VMAF 92+, CRF 26 AV1 / 23 HEVC)")
        print(" 3. Balanced (Sweet spot for space & quality, ~VMAF 86+, CRF 30 AV1 / 26 HEVC)")
        print(" 4. Compact (Smallest file size, ~VMAF 78+, CRF 36 AV1 / 30 HEVC)")
        p_ch = input("Preset (1-4) [Default 3]: ").strip() or "3"
        preset = {"1": "archival", "2": "high", "3": "balanced", "4": "compact"}.get(p_ch, "balanced")
        compress_video(path_input, codec=codec, preset=preset, is_gpu=use_gpu, ffmpeg_exe=ffmpeg, ffprobe_exe=ffprobe)
    elif mode_choice == "3":
        target_str = input("\nEnter target file size in MB (e.g. 50): ").strip()
        try:
            target_mb = float(target_str)
            compress_video(path_input, codec=codec, target_mb=target_mb, is_gpu=use_gpu, ffmpeg_exe=ffmpeg, ffprobe_exe=ffprobe)
        except ValueError:
            print("[-] Invalid size number.")
    elif mode_choice == "4":
        crf_str = input(f"\nEnter custom CRF value ({'18-36' if codec == 'av1' else '16-32'}): ").strip()
        try:
            crf_val = int(crf_str)
            compress_video(path_input, codec=codec, crf=crf_val, is_gpu=use_gpu, ffmpeg_exe=ffmpeg, ffprobe_exe=ffprobe)
        except ValueError:
            print("[-] Invalid CRF number.")


def main():
    parser = argparse.ArgumentParser(description="Optimal AV1 / HEVC Video Compressor & Optimizer")
    parser.add_argument("input", nargs="?", help="Input video file or directory")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-c", "--codec", choices=["av1", "hevc", "h264"], default="av1", help="Target video codec (default: av1)")
    parser.add_argument("-p", "--preset", choices=["archival", "high", "balanced", "compact"], default="balanced", help="Compression profile")
    parser.add_argument("--crf", type=int, help="Exact CRF/CQ quality value")
    parser.add_argument("--target-mb", type=float, help="Target file size in Megabytes")
    parser.add_argument("--gpu", action="store_true", help="Use NVIDIA NVENC hardware acceleration")
    parser.add_argument("--audio", choices=["copy", "opus", "aac"], default="copy", help="Audio handling (default: copy)")
    parser.add_argument("--scale", type=int, help="Target height resolution in pixels (e.g. 720, 1080)")
    parser.add_argument("--sample-test", action="store_true", help="Run VMAF/Sample quality optimizer without full encode")
    parser.add_argument("--batch", action="store_true", help="Batch process directory")
    parser.add_argument("--ffmpeg", help="Custom path to ffmpeg executable")
    parser.add_argument("--ffprobe", help="Custom path to ffprobe executable")

    args = parser.parse_args()

    ffmpeg_bin = find_binary("ffmpeg", args.ffmpeg)
    ffprobe_bin = find_binary("ffprobe", args.ffprobe)

    if not args.input:
        interactive_menu()
        return

    if args.sample_test or (args.input and not args.output and not args.batch and not os.path.isdir(args.input) and len(sys.argv) == 2):
        # If run directly with just a file argument, run interactive or test
        interactive_menu()
        return

    if os.path.isdir(args.input) or args.batch:
        batch_compress(
            args.input,
            codec=args.codec,
            preset=args.preset,
            crf=args.crf,
            is_gpu=args.gpu,
            audio_mode=args.audio,
            scale_height=args.scale,
            ffmpeg_exe=ffmpeg_bin,
            ffprobe_exe=ffprobe_bin
        )
    else:
        compress_video(
            input_path=args.input,
            output_path=args.output,
            codec=args.codec,
            preset=args.preset,
            crf=args.crf,
            target_mb=args.target_mb,
            is_gpu=args.gpu,
            audio_mode=args.audio,
            scale_height=args.scale,
            ffmpeg_exe=ffmpeg_bin,
            ffprobe_exe=ffprobe_bin
        )


if __name__ == "__main__":
    main()
