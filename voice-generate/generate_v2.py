#!/usr/bin/env python3
"""
WebGAL HUST Voice Generation v2 — MiniMax speech-02-hd with improved emotion & voice mapping.
Stage 1: Generate ONE sample per character for approval.
Stage 2: Generate all 122 lines after approval.
"""

import os, re, time, json, sys, requests
from pathlib import Path
from collections import defaultdict

# === Configuration ===
API_KEY = "sk-api-9gkTfEnMqQbgoF5x6hhRnkT4a0hzwG78ygoDj_K__TZ3lfCkZ4B25K7Iu1PtvKAd1YHMFUg3lyq-p7azIsicMDGqOHHSLPDXfXNg4EaFKIi36SwfQxXE1_A"
API_URL = "https://api.minimaxi.com/v1/t2a_v2"
MODEL = "speech-2.8-hd"

SCENE_DIR = Path("d:/project/WebGAL/packages/webgal/public/game/scene")
SCENE_FILES = ["hust_ch1.txt", "hust_ch1_1950s.txt", "hust_ch2.txt", "hust_ch3.txt"]
OUTPUT_DIR = Path("d:/project/WebGAL/packages/webgal/public/game/voice")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_DIR = Path("d:/project/WebGAL/voice-generate/samples")
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

# === Updated Speaker Config (v2) ===
SPEAKER_CONFIG = {
    "林知远": {
        "voice_id": "male-qn-daxuesheng",    # 大学生音色 — natural young male
        "alias": "lin",
        "speed": 1.0,
        "pitch": 0,
    },
    "1024": {
        "voice_id": "Chinese (Mandarin)_Crisp_Girl",  # 清爽干练女声 — not too young
        "alias": "s1024",
        "speed": 1.05,
        "pitch": 0,
    },
    "陈老师": {
        "voice_id": "Chinese (Mandarin)_Gentle_Youth",  # 温和青年男声 — younger teacher
        "alias": "chen",
        "speed": 0.95,
        "pitch": 0,
    },
    "张江陵": {
        "voice_id": "Chinese (Mandarin)_Male_Announcer",  # 男播音员 — deep, authoritative
        "alias": "zhangjl",
        "speed": 0.92,
        "pitch": -2,
    },
    "张工": {
        "voice_id": "Chinese (Mandarin)_Sincere_Adult",  # 诚恳成年人 — substantial, engineer-like
        "alias": "zhangg",
        "speed": 0.95,
        "pitch": -1,
    },
    "李教授": {
        "voice_id": "Chinese (Mandarin)_Reliable_Executive",  # 可靠高管 — authoritative, powerful
        "alias": "li",
        "speed": 0.92,
        "pitch": -1,
    },
    "周师兄": {
        "voice_id": "Chinese (Mandarin)_Unrestrained_Young_Man",  # 不羁青年 — energetic
        "alias": "zhou",
        "speed": 1.08,
        "pitch": 2,
    },
    "苏师姐": {
        "voice_id": "Chinese (Mandarin)_Warm_Bestie",  # 温暖闺蜜 — bright, friendly female
        "alias": "su",
        "speed": 1.05,
        "pitch": 1,
    },
    "王学长": {
        "voice_id": "male-qn-jingying",  # 精英青年 — user said this is fine
        "alias": "wang",
        "speed": 1.0,
        "pitch": 0,
    },
}

DIALOGUE_RE = re.compile(r'^([^:]+):(.+)$')

def strip_action(text):
    """Remove parenthetical action markers from TTS text."""
    return re.sub(r'[（(][^）)]*[）)]', '', text).strip()

def preprocess_text(text):
    """Preprocess text for better TTS prosody."""
    # Replace em-dashes with comma+ellipsis for clearer pauses
    text = text.replace('——', '，')
    # Normalize multiple punctuation
    text = re.sub(r'[！!]{2,}', '！', text)
    text = re.sub(r'[？?]{2,}', '？', text)
    return text

def detect_action_text(text):
    match = re.match(r'^[（(]([^）)]*)[）)]', text)
    if match:
        return match.group(1), text[match.end():].strip()
    return None, text

def detect_emotion(text, action_text):
    """Improved emotion detection from content and context."""
    combined = (action_text or "") + text

    # Happy
    if any(kw in combined for kw in ["笑", "欣慰", "兴奋", "高兴", "激动", "开心", "笑了", "哈哈", "欣慰地笑"]):
        return "happy"
    # Angry
    if any(kw in combined for kw in ["猛拍", "怒", "愤怒", "生气", "斥责", "愤"]):
        return "angry"
    # Surprised
    if any(kw in combined for kw in ["惊讶", "震惊", "吃惊", "惊呼", "愣了"]):
        return "surprised"
    # Sad
    if any(kw in combined for kw in ["沉默", "叹气", "难过", "伤心", "悲伤", "无奈", "苦笑", "叹口气", "低落"]):
        return "sad"
    # Whisper
    if any(kw in combined for kw in ["悄悄", "耳语", "轻声"]):
        return "whisper"
    # Fearful
    if any(kw in combined for kw in ["紧张", "害怕", "恐惧", "颤抖"]):
        return "fearful"

    return None


def parse_scene_files():
    dialogues = []
    speaker_seq = defaultdict(int)

    for filename in SCENE_FILES:
        filepath = SCENE_DIR / filename
        if not filepath.exists():
            continue

        stem = filepath.stem
        if "_" in stem:
            parts = stem.split("_")
            ch_prefix = "_".join(parts[1:])
        else:
            ch_prefix = stem

        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            line_text = line.rstrip("\n").rstrip("\r")
            if not line_text.strip() or line_text.strip().startswith(";"):
                continue

            m = DIALOGUE_RE.match(line_text.strip())
            if not m:
                continue

            speaker = m.group(1).strip()
            if speaker not in SPEAKER_CONFIG:
                continue

            raw_text = m.group(2).strip()
            if not raw_text:
                continue

            action_text, text_after_action = detect_action_text(raw_text)
            clean_text = strip_action(raw_text)
            clean_text = preprocess_text(clean_text)
            emotion = detect_emotion(text_after_action or raw_text, action_text)

            alias = SPEAKER_CONFIG[speaker]["alias"]
            speaker_seq[alias] += 1
            seq = speaker_seq[alias]
            audio_filename = f"{ch_prefix}_{alias}_{seq:04d}.mp3"

            dialogues.append({
                "file": filepath,
                "filename": filename,
                "line_num": i,
                "speaker": speaker,
                "alias": alias,
                "raw_text": raw_text,
                "clean_text": clean_text,
                "action": action_text,
                "emotion": emotion,
                "audio_filename": audio_filename,
                "seq": seq,
                "ch_prefix": ch_prefix,
            })

    return dialogues


def call_tts(text, voice_id, speed, pitch, emotion=None):
    """Single TTS call. Returns audio bytes or None."""
    voice_setting = {
        "voice_id": voice_id,
        "speed": speed,
        "vol": 1.0,
        "pitch": pitch,
    }
    if emotion:
        voice_setting["emotion"] = emotion

    body = {
        "model": MODEL,
        "text": text,
        "stream": False,
        "voice_setting": voice_setting,
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1,
        },
        "output_format": "hex",
    }

    for attempt in range(3):
        try:
            resp = requests.post(
                API_URL,
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json=body,
                timeout=60,
            )
            if resp.status_code == 429:
                wait = 5 * (attempt + 1)
                print(f"    Rate limited (429), wait {wait}s...", flush=True)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            base_resp = data.get("base_resp", {})
            status_code = base_resp.get("status_code", 0)
            if status_code == 1002:
                wait = 3 * (attempt + 1)
                print(f"    Rate limited (RPM), wait {wait}s...", flush=True)
                time.sleep(wait)
                continue
            if status_code != 0:
                print(f"    API error: {base_resp.get('status_msg')}", flush=True)
                return None
            hex_audio = data.get("data", {}).get("audio", "")
            if not hex_audio:
                return None
            return bytes.fromhex(hex_audio)
        except Exception as e:
            print(f"    Error: {e}", flush=True)
            if attempt < 2:
                time.sleep(3 * (attempt + 1))
            else:
                return None
    return None


def stage1_samples(dialogues):
    """Generate one representative sample per speaker."""
    print("=" * 60)
    print("STAGE 1: Generating 1 sample per character for review")
    print(f"Model: {MODEL}")
    print("=" * 60)

    # Pick representative sample per speaker (first occurrence with decent length)
    samples = {}
    for d in dialogues:
        alias = d["alias"]
        if alias not in samples:
            samples[alias] = d
        else:
            # Prefer longer text (more representative)
            if len(d["clean_text"]) > len(samples[alias]["clean_text"]) and len(d["clean_text"]) < 150:
                samples[alias] = d
            # If the current one is too short, replace
            if len(samples[alias]["clean_text"]) < 15 and len(d["clean_text"]) >= 15:
                samples[alias] = d

    results = []
    for i, (alias, d) in enumerate(sorted(samples.items())):
        config = SPEAKER_CONFIG[d["speaker"]]
        emotion = d["emotion"]
        emotion_str = emotion if emotion else "neutral"

        print(f"\n{'='*40}")
        print(f"[{i+1}/{len(samples)}] {d['speaker']} ({d['alias']})")
        print(f"  Voice: {config['voice_id']}")
        print(f"  Emotion: {emotion_str}")
        print(f"  Text: {d['clean_text'][:120]}")
        print(f"{'='*40}")

        audio = call_tts(
            d["clean_text"],
            config["voice_id"],
            config["speed"],
            config["pitch"],
            emotion,
        )

        if audio:
            out_path = SAMPLE_DIR / f"sample_{d['alias']}_{d['speaker']}.mp3"
            with open(out_path, "wb") as f:
                f.write(audio)
            print(f"  -> Saved: {out_path} ({len(audio)} bytes)", flush=True)
            results.append({"speaker": d["speaker"], "alias": alias, "file": str(out_path), "size": len(audio), "emotion": emotion_str})
        else:
            print(f"  -> FAILED", flush=True)
            results.append({"speaker": d["speaker"], "alias": alias, "file": None, "size": 0, "emotion": emotion_str})

        # Rate limit
        if i < len(samples) - 1:
            time.sleep(3.5)

    print(f"\n{'='*60}")
    print("STAGE 1 COMPLETE — Sample files:")
    for r in results:
        status = "OK" if r["file"] else "FAIL"
        print(f"  [{status}] {r['speaker']} ({r['alias']}) emotion={r['emotion']} -> {r['file']}")
    print(f"\nSample files are in: {SAMPLE_DIR}")
    print("Review these samples, then run Stage 2 to generate all 122 lines.")
    print("=" * 60)


def stage2_all(dialogues):
    """Generate all 122 dialogue lines."""
    print("=" * 60)
    print("STAGE 2: Generating all 122 dialogue lines")
    print(f"Model: {MODEL}")
    print("=" * 60)

    success = 0
    fail = 0

    for idx, d in enumerate(dialogues):
        out_path = OUTPUT_DIR / d["audio_filename"]

        if out_path.exists() and out_path.stat().st_size > 100:
            print(f"  [{idx+1}/{len(dialogues)}] SKIP: {d['audio_filename']}", flush=True)
            success += 1
            continue
        elif out_path.exists():
            out_path.unlink()

        config = SPEAKER_CONFIG[d["speaker"]]
        emotion = d["emotion"]
        emotion_str = emotion if emotion else "neutral"

        print(f"  [{idx+1}/{len(dialogues)}] {d['speaker']}({emotion_str}): "
              f"\"{d['clean_text'][:60]}\" -> {d['audio_filename']}", flush=True)

        audio = call_tts(d["clean_text"], config["voice_id"], config["speed"], config["pitch"], emotion)
        if audio:
            with open(out_path, "wb") as f:
                f.write(audio)
            print(f"    OK ({len(audio)} bytes)", flush=True)
            success += 1
        else:
            print(f"    FAILED", flush=True)
            fail += 1

        if idx < len(dialogues) - 1:
            time.sleep(3.5)

    print(f"\n  Results: {success} success, {fail} failed")
    return success, fail


def update_scene_files(dialogues):
    """Insert audio references into scene files."""
    by_file = defaultdict(list)
    for d in dialogues:
        by_file[d["file"]].append(d)

    for filepath, file_dialogues in by_file.items():
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        line_updates = {}
        for d in file_dialogues:
            line_updates[d["line_num"]] = d["audio_filename"]

        for line_num in sorted(line_updates.keys(), reverse=True):
            line = lines[line_num].rstrip("\n").rstrip("\r")
            filename = line_updates[line_num]
            stripped = re.sub(r'\s+-[a-zA-Z][a-zA-Z0-9_]*\.mp3\s*', '', line)
            if stripped.endswith(";"):
                stripped = stripped.rstrip(";").rstrip()
                lines[line_num] = f"{stripped} -{filename};\n"
            else:
                lines[line_num] = f"{stripped.rstrip()} -{filename}\n"

        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"  Updated: {filepath.name} ({len(file_dialogues)} refs)")


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "1"

    print("Parsing scene files...")
    dialogues = parse_scene_files()
    print(f"  Found {len(dialogues)} dialogue lines")

    by_speaker = defaultdict(int)
    by_emotion = defaultdict(int)
    for d in dialogues:
        by_speaker[d["speaker"]] += 1
        e = d["emotion"] or "neutral"
        by_emotion[e] += 1
    print(f"  By speaker: {dict(by_speaker)}")
    print(f"  By emotion: {dict(by_emotion)}")

    if stage == "1":
        stage1_samples(dialogues)
    elif stage == "2":
        ok, fail = stage2_all(dialogues)
        if fail == 0:
            print("\nUpdating scene files...")
            update_scene_files(dialogues)
        else:
            print(f"\n{fail} failures — not updating scene files. Fix issues and re-run.")
    else:
        print("Usage: python generate_v2.py [1|2]")


if __name__ == "__main__":
    main()
