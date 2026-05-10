#!/usr/bin/env python3
"""
MiniMax TTS Voice Generator for WebGAL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Scans scene files, extracts all dialogue, generates voice via MiniMax TTS API,
saves audio to vocal/, and patches scene files with -vocal= references.

Usage:
    python scripts/minimax-tts.py --dry-run    # Preview only
    python scripts/minimax-tts.py              # Generate & patch
    python scripts/minimax-tts.py --force      # Regenerate existing files
"""

import base64
import hashlib
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# ─── CONFIG ────────────────────────────────────────────────────────────────────

MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
if not MINIMAX_API_KEY:
    print("=" * 60)
    print("  ERROR: MINIMAX_API_KEY not set!")
    print("  Usage: export MINIMAX_API_KEY='sk-xxx' && python scripts/minimax-tts.py")
    print("=" * 60)
    sys.exit(1)
API_URL = "https://api.minimaxi.com/v1/t2a_v2"
MODEL = "speech-02-hd"
OUTPUT_FORMAT = "mp3"
SAMPLE_RATE = 24000
SPEED = 1.0
RATE_LIMIT_DELAY = 0.8  # seconds between API calls

# Character → MiniMax voice_id
VOICE_MAP = {
    "林知远": "male-qn-daxuesheng",
    "1024": "female-shaonv",
    "陈老师": "male-qn-jingying-jingpin",
    "张江陵": "male-qn-jingying",
    "张工": "male-qn-jingying",
    "李教授": "male-qn-qingse-jingpin",
    "周师兄": "male-qn-daxuesheng-jingpin",
    "苏师姐": "female-yujie",
    "王学长": "male-qn-qingse",
    "王浩": "male-qn-daxuesheng",
}
DEFAULT_VOICE = "male-qn-daxuesheng"

# Speaker short IDs for filenames
SPEAKER_ID = {
    "林知远": "lin",
    "1024": "s1024",
    "陈老师": "chen",
    "张江陵": "zhangjl",
    "张工": "zhangg",
    "李教授": "li",
    "周师兄": "zhou",
    "苏师姐": "su",
    "王学长": "wangx",
    "王浩": "wangh",
}

# Commands that have "speaker:" format but are NOT dialogue
COMMAND_KEYWORDS = {
    "setVar", "changeBg", "bgm", "intro", "changeFigure", "changeScene",
    "setTransition", "setAnimation", "setTransform", "miniAvatar", "choose",
    "label", "jumpLabel", "if", "pixiInit", "pixiPerform", "pixi", "unlockBgm",
    "unlockCg", "end", "callScene", "getUserInput", "showVars", "filmMode",
    "setTextbox", "playEffect", "playVideo", "setTempAnimation", "comment",
    "setFilter", "setComplexAnimation", "applyStyle", "wait", "callSteam",
    "setTransition", "changeBg", "changeFigure",
}

# Paths
ROOT = Path(__file__).resolve().parent.parent
SCENE_DIR = ROOT / "packages" / "webgal" / "public" / "game" / "scene"
VOCAL_DIR = ROOT / "packages" / "webgal" / "public" / "game" / "vocal"

# ─── DIALOGUE PARSING ─────────────────────────────────────────────────────────

COMMAND_RE = re.compile(r"^[a-zA-Z]+:")


def is_dialogue_line(line: str) -> bool:
    """Check if a line is speaker dialogue (not a command/comment/label)."""
    stripped = line.strip()
    if not stripped or stripped.startswith(";"):
        return False
    # Must have a colon
    if ":" not in stripped.split(" -")[0].split(";")[0]:
        return False
    # First word before colon must NOT be a known command
    before_colon = stripped.split(":")[0].strip()
    if before_colon in COMMAND_KEYWORDS:
        return False
    return True


def strip_stage_directions(text: str) -> str:
    """Remove （...） and (...) stage directions from dialogue text."""
    depth = 0
    result_chars = []
    for ch in text:
        if ch in "（(":
            depth += 1
        elif ch in "）)":
            depth = max(0, depth - 1)
        elif depth == 0:
            result_chars.append(ch)
    return "".join(result_chars).strip()


def clean_dialogue_text(text: str) -> str:
    """Clean up dialogue text for TTS: remove stage directions, rich text, variables."""
    # Remove stage directions （...） and (...)
    text = strip_stage_directions(text)
    # Remove WebGAL rich text markup [text](style=...)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    # Replace {variable} with default values
    text = text.replace("{playerName}", "林知远")
    text = text.replace("{engine}", "WebGAL")
    text = re.sub(r"\{[^}]+\}", "", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_dialogue(line: str):
    """Extract speaker and text from a dialogue line."""
    stripped = line.strip()
    # Remove inline comment (after ; not preceded by \)
    no_comment = re.sub(r"(?<!\\);.*$", "", stripped).strip()
    # Split args: first " -" that's not inside CJK punctuation
    # Simple: just split on " -"
    parts = no_comment.split(" -")
    content = parts[0].strip()
    # Split on first ":"
    colon_idx = content.index(":")
    speaker = content[:colon_idx].strip()
    text = content[colon_idx + 1:].strip()
    return speaker, text


def extract_all_dialogue(scene_dir: Path):
    """Scan all hust_ch*.txt files and return dialogue entries."""
    scenes = sorted(scene_dir.glob("hust_ch*.txt"))
    entries = []

    for scene_file in scenes:
        lines = scene_file.read_text(encoding="utf-8").splitlines()
        for line_idx, line in enumerate(lines):
            if not is_dialogue_line(line):
                continue
            speaker, text = parse_dialogue(line)
            text_clean = clean_dialogue_text(text)
            if not text_clean:
                continue
            entries.append({
                "file": scene_file.name,
                "line_idx": line_idx,
                "speaker": speaker,
                "text": text_clean,
                "text_raw": text,
                "voice_id": VOICE_MAP.get(speaker, DEFAULT_VOICE),
            })

    return entries


def has_vocal_arg(line: str) -> bool:
    """Check if a dialogue line already has a vocal file argument."""
    for part in line.split(" -"):
        arg = part.strip().rstrip(";")
        if arg.endswith(".mp3") or arg.endswith(".wav") or arg.endswith(".ogg"):
            return True
        if arg.startswith("vocal=") and (".mp3" in arg or ".wav" in arg or ".ogg" in arg):
            return True
    return False


# ─── MINIMAX TTS API ──────────────────────────────────────────────────────────

def _create_ssl_context():
    """Create SSL context that works on Windows/MSYS2."""
    ctx = ssl.create_default_context()
    try:
        # Try to use certifi if available
        import certifi  # type: ignore
        ctx.load_verify_locations(certifi.where())
    except ImportError:
        # Fall back to unverified (needed for Windows/MSYS2 environments)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return ctx


def call_minimax_tts(text: str, voice_id: str, retries=3) -> bytes:
    """Call MiniMax TTS API and return audio bytes."""
    global _SSL_CTX
    try:
        _SSL_CTX
    except NameError:
        _SSL_CTX = _create_ssl_context()  # type: ignore

    payload = json.dumps({
        "model": MODEL,
        "text": text,
        "stream": False,
        "output_format": "hex",
        "language_boost": "Chinese",
        "voice_setting": {
            "voice_id": voice_id,
            "speed": SPEED,
            "vol": 1.0,
            "pitch": 0,
        },
        "audio_setting": {
            "sample_rate": SAMPLE_RATE,
            "format": OUTPUT_FORMAT,
            "channel": 1,
        },
    }).encode("utf-8")

    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json",
    }

    last_error = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(API_URL, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=180, context=_SSL_CTX) as resp:
                body = resp.read()
                ct = resp.headers.get("Content-Type", "")

            # Case 1: direct audio binary
            if "audio" in ct:
                return body

            # Case 2: JSON with base64 audio
            try:
                result = json.loads(body)
            except json.JSONDecodeError:
                # Case 3: raw binary fallback
                return body

            # Case 2: JSON with base64/hex audio
            try:
                result = json.loads(body)
            except json.JSONDecodeError:
                # Case 3: raw binary fallback
                return body

            # Check API status
            br = result.get("base_resp", {})
            if br.get("status_code", 0) != 0:
                raise RuntimeError(f"API error: {br.get('status_msg', br.get('status_message', 'unknown'))}")

            # Extract audio from response (Chinese platform: result.data.audio is hex)
            if "data" in result and isinstance(result["data"], dict):
                audio_hex = result["data"].get("audio", "")
                if audio_hex:
                    return bytes.fromhex(audio_hex)

            if "audio" in result:
                val = result["audio"]
                if isinstance(val, str):
                    # Could be base64 or hex, try both
                    try:
                        return base64.b64decode(val)
                    except Exception:
                        return bytes.fromhex(val)

            raise RuntimeError(f"No audio in response: {list(result.keys())}")

        except urllib.error.HTTPError as e:
            last_error = f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:200]}"
            if e.code in (429, 502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(last_error)
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            last_error = str(e)
            time.sleep(2 ** attempt)
            continue

    raise RuntimeError(f"All retries failed: {last_error}")


# ─── PATCH SCENE FILES ────────────────────────────────────────────────────────

def patch_scene_file(scene_file: Path, line_idx: int, vocal_file: str):
    """Add -vocal=filename.mp3 to a dialogue line."""
    lines = scene_file.read_text(encoding="utf-8").splitlines()
    original = lines[line_idx]

    if has_vocal_arg(original):
        return  # Already has vocal, skip

    # Add vocal arg before the trailing semicolon
    stripped = original.rstrip()
    if stripped.endswith(";"):
        lines[line_idx] = stripped[:-1] + f" -{vocal_file};"
    else:
        lines[line_idx] = stripped + f" -{vocal_file}"

    scene_file.write_text("\n".join(lines), encoding="utf-8")


# ─── MAIN ──────────────────────────────────────────────────────────────────────

def print_header(title):
    width = 60
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def main():
    dry_run = "--dry-run" in sys.argv
    force = "--force" in sys.argv

    print_header("MiniMax TTS Voice Generator for WebGAL")
    print(f"  Scene dir : {SCENE_DIR}")
    print(f"  Vocal dir : {VOCAL_DIR}")
    print(f"  Model     : {MODEL}")
    if dry_run:
        print("  [DRY-RUN mode - no API calls, no file changes]")
    if force:
        print("  [FORCE mode - regenerate existing files]")
    print()

    # ── Step 1: Extract dialogue ──
    print("▶ Step 1: Scanning for dialogue lines...")
    entries = extract_all_dialogue(SCENE_DIR)
    files = set(e["file"] for e in entries)
    print(f"  Found {len(entries)} dialogue lines across {len(files)} files\n")

    # Speaker summary
    speakers = {}
    for e in entries:
        speakers.setdefault(e["speaker"], {"count": 0, "voice": e["voice_id"]})
        speakers[e["speaker"]]["count"] += 1

    # Count chars for cost estimate
    total_chars = sum(len(e["text"]) for e in entries)

    print("  Speakers:")
    for s, info in sorted(speakers.items()):
        print(f"    {s:10s} → {info['voice']:30s} ({info['count']} lines)")
    print(f"\n  Total characters: {total_chars}")
    hd_cost = (total_chars / 10000) * 3.5
    turbo_cost = (total_chars / 10000) * 2.0
    print(f"  Estimated API cost: ¥{hd_cost:.2f} (HD) / ¥{turbo_cost:.2f} (Turbo)")
    print()

    # Check for existing vocal files
    existing_vocals = set(f.name for f in VOCAL_DIR.glob(f"*.{OUTPUT_FORMAT}")) if VOCAL_DIR.exists() else set()
    if existing_vocals:
        print(f"  Existing vocal files: {len(existing_vocals)}")

    # Count per-speaker dialogue
    for e in entries:
        sid = SPEAKER_ID.get(e["speaker"], "other")
    print()

    if dry_run:
        # Show a preview of what will be generated
        print("  Preview (first 15 lines):")
        for e in entries[:15]:
            print(f"    [{e['file']:20s}] {e['speaker']}: {e['text'][:55]}")
        if len(entries) > 15:
            print(f"    ... and {len(entries) - 15} more lines")
        print()

        # Show what files would be patched
        print("  Scene files to patch:")
        for f in sorted(files):
            file_entries = [e for e in entries if e["file"] == f]
            has_vocal = sum(1 for e in file_entries if has_vocal_arg(open(SCENE_DIR / f, encoding="utf-8").readlines()[e["line_idx"]]))
            print(f"    {f:20s} {len(file_entries):3d} dialogue lines  ({has_vocal} already have vocal)")
        print()
        print("  Run without --dry-run to execute.")
        return

    # ── Step 2: Generate audio ──
    print_header("Step 2: Generating Audio via MiniMax TTS")

    VOCAL_DIR.mkdir(parents=True, exist_ok=True)

    # Generate sequential filenames per speaker
    counters = {}
    to_generate = []

    for e in entries:
        sid = SPEAKER_ID.get(e["speaker"], "other")
        counters[sid] = counters.get(sid, 0) + 1
        seq = counters[sid]
        filename = f"{sid}_{seq:04d}.{OUTPUT_FORMAT}"
        e["vocal_file"] = filename
        filepath = VOCAL_DIR / filename
        e["vocal_path"] = filepath

        if filepath.exists() and not force:
            continue  # Skip existing

        to_generate.append(e)

    print(f"  To generate: {len(to_generate)} / {len(entries)} total")
    print(f"  (Skipped {len(entries) - len(to_generate)} already-existing files)\n")

    if not to_generate:
        print("  Nothing to generate. Use --force to regenerate.\n")
    else:
        success = 0
        failed = []
        for i, e in enumerate(to_generate):
            text = e["text"]
            voice = e["voice_id"]
            filename = e["vocal_file"]

            print(f"  [{i+1}/{len(to_generate)}] {e['speaker']}: {text[:45]:45s} ", end="", flush=True)

            try:
                audio = call_minimax_tts(text, voice)
                e["vocal_path"].write_bytes(audio)
                success += 1
                size_kb = len(audio) / 1024
                print(f"✓ {size_kb:.0f}KB")
            except Exception as ex:
                failed.append(e)
                print(f"✗ {ex}")

            # Rate limit
            if i < len(to_generate) - 1:
                time.sleep(RATE_LIMIT_DELAY)

        print(f"\n  Generated: {success}, Failed: {len(failed)}")

    print()

    # ── Step 3: Patch scene files ──
    print_header("Step 3: Patching Scene Files")

    patched = 0
    already_have = 0
    for scene_file in sorted(SCENE_DIR.glob("hust_ch*.txt")):
        lines = scene_file.read_text(encoding="utf-8").splitlines()
        modified = False
        new_lines = list(lines)

        for e in entries:
            if e["file"] != scene_file.name:
                continue
            if not e.get("vocal_file"):
                continue
            idx = e["line_idx"]
            if idx >= len(new_lines):
                continue

            # Relocate line (may have shifted due to previous edits)
            line = new_lines[idx]
            if has_vocal_arg(line):
                already_have += 1
                continue

            # Add vocal arg
            stripped = line.rstrip()
            if stripped.endswith(";"):
                new_lines[idx] = stripped[:-1] + f" -{e['vocal_file']};"
            else:
                new_lines[idx] = stripped + f" -{e['vocal_file']}"
            modified = True
            patched += 1

        if modified:
            scene_file.write_text("\n".join(new_lines), encoding="utf-8")

    print(f"  Patched: {patched} lines")
    print(f"  Already had vocal: {already_have} lines")
    print()

    # ── Summary ──
    print_header("Complete!")
    print(f"  Audio files in: {VOCAL_DIR}")
    print(f"  Total generated: {len(list(VOCAL_DIR.glob(f'*.{OUTPUT_FORMAT}')))}")
    print()
    print("  To test, start the dev server and play the game:")
    print("    yarn dev")
    print()
    print("  To push to GitHub:")
    print("    git add packages/webgal/public/game/vocal/")
    print("    git add packages/webgal/public/game/scene/")
    print("    git commit -m 'add MiniMax TTS voice dubbing'")
    print("    git push")
    print("=" * 60)


if __name__ == "__main__":
    main()
