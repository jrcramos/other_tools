#!/usr/bin/env python3
"""
Subtitle Generator & Audio Extractor for Movies and Series
-----------------------------------------------------------
Uses FFmpeg/FFprobe to list and extract audio streams from video files,
and Whisper (faster-whisper / CTranslate2 with GPU CUDA acceleration or OpenAI Whisper)
to generate timed .SRT subtitle files with optional translation.
"""

import sys
import os
import json
import argparse
import subprocess
import tempfile
import urllib.request
import urllib.parse
import re

# Suppress HuggingFace cache symlink warning on Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Ensure UTF-8 output streams on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

LANGUAGE_CODES = {
    "auto": "Auto-detect",
    "en": "English",
    "pt": "Portuguese",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "ja": "Japanese",
    "zh": "Chinese",
    "ko": "Korean",
    "ru": "Russian",
    "nl": "Dutch",
    "pl": "Polish",
    "tr": "Turkish",
    "ar": "Arabic",
    "hi": "Hindi",
    "sv": "Swedish",
    "da": "Danish",
    "fi": "Finnish",
    "no": "Norwegian",
    "uk": "Ukrainian",
    "cs": "Czech",
    "el": "Greek",
    "he": "Hebrew",
    "hu": "Hungarian",
    "ro": "Romanian",
    "id": "Indonesian",
    "th": "Thai",
    "vi": "Vietnamese"
}

VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov', '.webm', '.m4v', '.ts', '.flv', '.wmv')


def find_binary(binary_name, custom_path=None):
    """Find location of ffmpeg or ffprobe executable."""
    if custom_path and os.path.isfile(custom_path):
        return custom_path
    if custom_path and os.path.isdir(custom_path):
        candidate = os.path.join(custom_path, f"{binary_name}.exe" if sys.platform == "win32" else binary_name)
        if os.path.isfile(candidate):
            return candidate
    
    # Check common installation locations
    common_paths = [
        rf"C:\ffmpeg\bin\{binary_name}.exe",
        rf"C:\Program Files\ffmpeg\bin\{binary_name}.exe",
        os.path.expanduser(rf"~\ffmpeg\bin\{binary_name}.exe")
    ]
    for cp in common_paths:
        if os.path.isfile(cp):
            return cp
            
    # Check system PATH
    import shutil
    path_bin = shutil.which(binary_name)
    if path_bin:
        return path_bin

    return binary_name


def probe_audio_streams(video_path, ffprobe_exe="ffprobe"):
    """Probe audio streams in a video file using ffprobe."""
    cmd = [
        ffprobe_exe,
        "-v", "quiet",
        "-print_format", "json",
        "-show_streams",
        "-select_streams", "a",
        video_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        streams = data.get("streams", [])
        
        audio_tracks = []
        for idx, stream in enumerate(streams):
            tags = stream.get("tags", {})
            lang = tags.get("language", tags.get("LANGUAGE", "und"))
            title = tags.get("title", tags.get("TITLE", ""))
            codec = stream.get("codec_name", "unknown")
            channels = stream.get("channels", 2)
            channel_layout = stream.get("channel_layout", f"{channels} ch")
            
            track_info = {
                "relative_index": idx,
                "stream_index": stream.get("index", idx),
                "codec": codec,
                "channels": channels,
                "channel_layout": channel_layout,
                "language": lang,
                "title": title
            }
            audio_tracks.append(track_info)
        return audio_tracks
    except Exception as e:
        print(f"Error probing video streams for {video_path}: {e}", file=sys.stderr)
        return []


def extract_audio_track(video_path, relative_track_index, output_wav_path, ffmpeg_exe="ffmpeg"):
    """Extract specified audio track to 16kHz mono WAV file."""
    cmd = [
        ffmpeg_exe,
        "-y",
        "-i", video_path,
        "-map", f"0:a:{relative_track_index}",
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        output_wav_path
    ]
    
    print(f"Extracting audio track #{relative_track_index} with FFmpeg...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg audio extraction failed: {result.stderr}")
    print("Audio extraction complete.")


def translate_text_batch(texts, source_lang='auto', target_lang='pt'):
    """Translate a list of text strings using Google Translate free endpoint."""
    if not texts:
        return []
    
    translated = []
    chunk_size = 20
    for i in range(0, len(texts), chunk_size):
        chunk = texts[i:i+chunk_size]
        delimiter = "\n---SEGMENT---\n"
        combined_text = delimiter.join(chunk)
        
        sl = 'auto' if not source_lang or source_lang == 'auto' else source_lang
        tl = target_lang
        
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={sl}&tl={tl}&dt=t&q=" + urllib.parse.quote(combined_text)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                res_text = "".join([item[0] for item in data[0] if item and item[0]])
                split_res = res_text.split("---SEGMENT---")
                split_res = [s.strip() for s in split_res]
                
                if len(split_res) == len(chunk):
                    translated.extend(split_res)
                else:
                    for single in chunk:
                        single_url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={sl}&tl={tl}&dt=t&q=" + urllib.parse.quote(single)
                        sreq = urllib.request.Request(single_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(sreq, timeout=10) as sresp:
                            sdata = json.loads(sresp.read().decode('utf-8'))
                            translated.append("".join([item[0] for item in sdata[0] if item and item[0]]))
        except Exception as e:
            print(f"Warning: Translation request failed ({e}). Keeping original text for segment.", file=sys.stderr)
            translated.extend(chunk)
            
    return translated


def format_srt_time(seconds):
    """Format seconds float into SRT timestamp format HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        secs += 1
        millis = 0
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def load_whisper_engine(model_name):
    """Load Whisper model with GPU CUDA acceleration (preferring faster-whisper)."""
    # 1. Try faster-whisper (CTranslate2 - up to 4x-8x faster on GPU/CPU)
    try:
        from faster_whisper import WhisperModel
        import torch
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        
        print(f"\n[ENGINE] Using faster-whisper (CTranslate2) | Device: {device.upper()} | Compute: {compute_type}")
        if device == "cuda":
            print(f"[GPU] {torch.cuda.get_device_name(0)}")
            
        model = WhisperModel(model_name, device=device, compute_type=compute_type)
        return ("faster-whisper", model, device)
    except Exception as e:
        print(f"INFO: faster-whisper load notice ({e}). Falling back to openai-whisper...", file=sys.stderr)

    # 2. Fallback to openai-whisper with PyTorch CUDA optimization
    try:
        import whisper
        import torch
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"\n[ENGINE] Using openai-whisper | Device: {device.upper()}")
        if device == "cuda":
            print(f"[GPU] {torch.cuda.get_device_name(0)}")
            
        model = whisper.load_model(model_name, device=device)
        return ("openai-whisper", model, device)
    except ImportError:
        print("ERROR: Neither faster-whisper nor openai-whisper is installed.", file=sys.stderr)
        print("Please run: pip install faster-whisper openai-whisper", file=sys.stderr)
        sys.exit(1)


def generate_subtitles_for_audio(wav_path, output_srt_path, engine_tuple, source_lang=None, target_lang=None):
    """Transcribe extracted WAV audio using loaded engine and save SRT file."""
    engine_name, model, device = engine_tuple

    segments_data = []
    detected_lang = source_lang or "auto"

    if engine_name == "faster-whisper":
        task = "translate" if (target_lang == "en" and source_lang != "en") else "transcribe"
        use_native_translation = (task == "translate")
        
        lang_arg = None if (not source_lang or source_lang == "auto") else source_lang
        
        print(f"Starting audio transcription with faster-whisper (Language: {source_lang or 'auto'})...")
        segments_gen, info = model.transcribe(
            wav_path, 
            language=lang_arg, 
            task=task,
            beam_size=5,
            vad_filter=True, # Voice Activity Detection speeds up silent parts
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        detected_lang = info.language
        print(f"Transcription finished! Detected/Used audio language: '{detected_lang}' (Probability: {info.language_probability:.2f})")
        
        for seg in segments_gen:
            segments_data.append({
                "start": seg.start,
                "end": seg.end,
                "text": seg.text.strip()
            })

    else:
        # openai-whisper engine
        transcribe_options = {
            "condition_on_previous_text": False,
            "fp16": (device == "cuda")
        }
        if source_lang and source_lang != "auto":
            transcribe_options["language"] = source_lang

        use_native_translation = False
        if target_lang == "en" and source_lang != "en":
            transcribe_options["task"] = "translate"
            use_native_translation = True
            print("Using Whisper native translation to English.")
        else:
            transcribe_options["task"] = "transcribe"

        print(f"Starting audio transcription with openai-whisper (Language: {source_lang or 'auto'})...")
        result = model.transcribe(wav_path, **transcribe_options)
        detected_lang = result.get("language", source_lang or "unknown")
        print(f"Transcription finished! Detected/Used audio language: '{detected_lang}'")
        
        for seg in result.get("segments", []):
            segments_data.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip()
            })

    if not segments_data:
        print("Warning: No speech segments detected in audio file.")
        
    needs_external_translation = (
        target_lang 
        and target_lang != "auto" 
        and target_lang != detected_lang 
        and not use_native_translation
    )

    if needs_external_translation:
        target_name = LANGUAGE_CODES.get(target_lang, target_lang)
        print(f"Translating {len(segments_data)} subtitle segments to {target_name} ({target_lang})...")
        original_texts = [seg["text"] for seg in segments_data]
        translated_texts = translate_text_batch(original_texts, source_lang=detected_lang, target_lang=target_lang)
        for seg, trans_text in zip(segments_data, translated_texts):
            seg["text"] = trans_text

    print(f"Writing SRT subtitle file to: {output_srt_path}")
    with open(output_srt_path, "w", encoding="utf-8-sig") as f:
        for idx, seg in enumerate(segments_data, 1):
            start_str = format_srt_time(seg["start"])
            end_str = format_srt_time(seg["end"])
            text = seg["text"]
            
            f.write(f"{idx}\n")
            f.write(f"{start_str} --> {end_str}\n")
            f.write(f"{text}\n\n")
            
    print("Subtitle generation complete!")


def normalize_path(path_str):
    if not path_str:
        return ""
    p = path_str.strip()
    p = p.strip('"').strip("'").strip()
    if not p:
        return ""
    if sys.platform == "win32":
        p = p.replace('/', '\\')
        p = os.path.normpath(p)
        if re.match(r'^[a-zA-Z]\\[^\:]', p):
            p = p[0] + ":" + p[1:]
    else:
        p = os.path.normpath(p)
    return p


def main():
    parser = argparse.ArgumentParser(description="Extract audio track and generate SRT subtitles for movies/series.")
    parser.add_argument("--input", "-i", nargs="+", help="Input video file path(s) or folder(s)")
    parser.add_argument("--input-file-list", help="Text file containing list of input video paths (one per line)")
    parser.add_argument("--list-tracks", action="store_true", help="List audio tracks for video file and exit")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format for track listing (json or text)")
    parser.add_argument("--count-input-list", action="store_true", help="Output total count of valid video files and exit")
    parser.add_argument("--track", "-t", type=int, default=0, help="Relative audio track index (0, 1, 2...)")
    parser.add_argument("--model", "-m", default="base", choices=["tiny", "base", "small", "medium", "large-v3", "turbo"], help="Whisper model size")
    parser.add_argument("--source-lang", "-sl", default="auto", help="Audio spoken language code (e.g. en, pt, es, ja, auto)")
    parser.add_argument("--target-lang", "-tl", default="auto", help="Target subtitle language code (e.g. en, pt, es, ja, auto)")
    parser.add_argument("--output", "-o", help="Output SRT file path (single file mode only)")
    parser.add_argument("--ffmpeg-path", help="Custom path to ffmpeg executable")
    parser.add_argument("--ffprobe-path", help="Custom path to ffprobe executable")

    args = parser.parse_args()

    ffmpeg_bin = find_binary("ffmpeg", args.ffmpeg_path)
    ffprobe_bin = find_binary("ffprobe", args.ffprobe_path)

    # Collect input files
    input_files = []
    
    def add_path(p):
        p = normalize_path(p)
        if not p or not os.path.exists(p):
            return
        if os.path.isfile(p):
            if p.lower().endswith(VIDEO_EXTENSIONS) or not os.path.splitext(p)[1]:
                if p not in input_files:
                    input_files.append(p)
        elif os.path.isdir(p):
            for root, _, files in os.walk(p):
                for file in sorted(files):
                    if file.lower().endswith(VIDEO_EXTENSIONS):
                        full_p = os.path.join(root, file)
                        if full_p not in input_files:
                            input_files.append(full_p)

    if args.input_file_list and os.path.isfile(args.input_file_list):
        lines = []
        try:
            with open(args.input_file_list, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            try:
                with open(args.input_file_list, "r", encoding="utf-8", errors="replace") as f:
                    lines = f.readlines()
            except Exception:
                pass
        for line in lines:
            add_path(line)

    if args.input:
        for inp in args.input:
            add_path(inp)

    if args.count_input_list:
        print(len(input_files))
        sys.exit(0)

    if not input_files:
        parser.print_help()
        sys.exit(1)

    # If --list-tracks, output list of audio tracks for the first input file
    if args.list_tracks:
        tracks = probe_audio_streams(input_files[0], ffprobe_bin)
        if args.format == "text":
            if not tracks:
                print("  No audio tracks found or unable to probe video file.")
            for t in tracks:
                lang = t.get('language', 'und')
                codec = t.get('codec', 'unknown')
                channels = t.get('channels', 2)
                ch_layout = t.get('channel_layout', f"{channels} ch")
                title = t.get('title', '')
                title_str = f" - {title}" if title else ""
                print(f"  Track #{t['relative_index']}: Language={lang}, Codec={codec}, Channels={ch_layout}{title_str}")
        else:
            print(json.dumps(tracks, indent=2))
        sys.exit(0)

    # Load Whisper engine once (preferring GPU CUDA + faster-whisper VAD)
    engine_tuple = load_whisper_engine(args.model)

    print(f"\nProcessing {len(input_files)} video file(s) sequentially:")
    for idx, vid_path in enumerate(input_files, 1):
        print(f"\n========================================================================")
        print(f" [{idx}/{len(input_files)}] Processing: {os.path.basename(vid_path)}")
        print(f" Path: {vid_path}")
        print(f"========================================================================")

        if len(input_files) == 1 and args.output:
            out_srt = args.output
        else:
            base_name, _ = os.path.splitext(vid_path)
            lang_suffix = f".{args.target_lang}" if args.target_lang and args.target_lang != "auto" else ""
            out_srt = f"{base_name}{lang_suffix}.srt"

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_wav = os.path.join(temp_dir, f"audio_{idx}.wav")
                extract_audio_track(vid_path, args.track, temp_wav, ffmpeg_bin)
                generate_subtitles_for_audio(
                    temp_wav, 
                    out_srt, 
                    engine_tuple=engine_tuple, 
                    source_lang=args.source_lang, 
                    target_lang=args.target_lang
                )
                print(f"SUCCESS: Generated {out_srt}")
        except Exception as e:
            print(f"ERROR processing '{vid_path}': {e}", file=sys.stderr)
            continue

    print(f"\n========================================================================")
    print(f" ALL {len(input_files)} VIDEO(S) PROCESSED SUCCESSFULLY!")
    print(f"========================================================================\n")


if __name__ == "__main__":
    main()
