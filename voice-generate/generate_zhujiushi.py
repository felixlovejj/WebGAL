#!/usr/bin/env python3
"""
Targeted generation for the 5 朱九思 anecdote lines (lines 86-93 of hust_ch1_1950s.txt).
"""
import requests, time, re
from pathlib import Path

API_KEY = "sk-api--P3zNstAeJ8snsPs5Ie4G-dS31aTQbcxgCWouVnbcOSBWdcB_TwASDh4stf6JWx7_bbYShWVJcfMEQLdLt7hseMwfW8iAclAU_Zwy1wYHxeaBOaPlKo3-5Y"
API_URL = "https://api.minimaxi.com/v1/t2a_v2"
MODEL = "speech-2.8-hd"
OUTPUT_DIR = Path("d:/project/WebGAL/packages/webgal/public/game/vocal")

SPEAKER_CONFIG = {
    "陈老师": {"voice_id": "hunyin_6", "speed": 1.02, "pitch": 0, "default_emotion": "calm"},
    "林知远": {"voice_id": "Chinese (Mandarin)_Straightforward_Boy", "speed": 1.04, "pitch": 0, "default_emotion": "calm"},
}

# 5 new lines with designed tone parameters
LINES = [
    {
        "speaker": "陈老师",
        "text": "你知道吗，<#0.25#>有人说他一生做了两件半事。(breath)第一件，把华工从纯工科学校变成综合性大学。<#0.3#>第二件，就是在最困难的时候，保护了人才。",
        "emotion": "calm",
        "audio_filename": "ch1_1950s_chen_0013.mp3",
    },
    {
        "speaker": "林知远",
        "text": "那半件事是什么？",
        "emotion": "calm",
        "audio_filename": "ch1_1950s_lin_0015.mp3",
    },
    {
        "speaker": "陈老师",
        "text": "种树。<#0.35#>喻家山上山下，他种了半辈子树。(breath)所以我们学校，才叫森林大学。",
        "emotion": "calm",
        "audio_filename": "ch1_1950s_chen_0014.mp3",
    },
    {
        "speaker": "林知远",
        "text": "砍一棵树都要校长审批的那个传说<#0.3#>",
        "emotion": "calm",
        "audio_filename": "ch1_1950s_lin_0016.mp3",
    },
    {
        "speaker": "陈老师",
        "text": "是真的。",
        "emotion": "calm",
        "audio_filename": "ch1_1950s_chen_0015.mp3",
    },
]


def generate(dialogue, max_retries=3):
    cfg = SPEAKER_CONFIG[dialogue["speaker"]]
    body = {
        "model": MODEL,
        "text": dialogue["text"],
        "stream": False,
        "voice_setting": {
            "voice_id": cfg["voice_id"],
            "speed": dialogue.get("speed", cfg["speed"]),
            "vol": 1.0,
            "pitch": dialogue.get("pitch", cfg["pitch"]),
            "emotion": dialogue.get("emotion", cfg["default_emotion"]),
        },
        "audio_setting": {
            "sample_rate": 32000, "bitrate": 128000,
            "format": "mp3", "channel": 1,
        },
        "output_format": "hex",
    }

    for attempt in range(max_retries):
        try:
            resp = requests.post(
                API_URL,
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json=body, timeout=120,
            )
            if resp.status_code == 429:
                wait = 5 * (attempt + 1)
                print(f"    Rate limited (429), retry in {wait}s...", flush=True)
                time.sleep(wait); continue

            resp.raise_for_status()
            data = resp.json()
            sc = data.get("base_resp", {}).get("status_code", 0)

            if sc == 1002:
                wait = 3 * (attempt + 1)
                print(f"    RPM limit, retry in {wait}s...", flush=True)
                time.sleep(wait); continue

            if sc != 0:
                print(f"    API error {sc}: {data.get('base_resp',{}).get('status_msg','')}", flush=True)
                return None

            hex_audio = data.get("data", {}).get("audio", "")
            if not hex_audio:
                print(f"    No audio data", flush=True); return None

            return bytes.fromhex(hex_audio)

        except requests.exceptions.RequestException as e:
            print(f"    HTTP error: {e}", flush=True)
            if attempt < max_retries - 1: time.sleep(3 * (attempt + 1))
            else: return None
        except Exception as e:
            print(f"    Error: {e}", flush=True); return None
    return None


def main():
    print("=" * 60, flush=True)
    print("WebGAL HUST — 朱九思 anecdote voice gen (5 lines)", flush=True)
    print("=" * 60, flush=True)

    success, fail = 0, 0

    for idx, d in enumerate(LINES):
        out = OUTPUT_DIR / d["audio_filename"]
        if out.exists() and out.stat().st_size > 100:
            print(f"  [{idx+1}/{len(LINES)}] SKIP {d['audio_filename']} (exists)", flush=True)
            success += 1; continue
        elif out.exists():
            out.unlink()

        print(f"  [{idx+1}/{len(LINES)}] {d['speaker']}({d['emotion']}) "
              f"\"{d['text'][:80]}\" -> {d['audio_filename']}", flush=True)

        audio = generate(d)
        if audio:
            with open(out, "wb") as f:
                f.write(audio)
            print(f"    OK {len(audio)} bytes", flush=True)
            success += 1
        else:
            print(f"    FAILED", flush=True)
            fail += 1

        if idx < len(LINES) - 1:
            time.sleep(3.5)

    print(f"\n  {success} ok, {fail} failed", flush=True)
    print("Done.", flush=True)


if __name__ == "__main__":
    main()
