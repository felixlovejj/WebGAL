#!/usr/bin/env python3
"""Fix 李教授 voice design — prompt was flagged as sensitive."""

import requests, json, time
from pathlib import Path

API_KEY = "sk-api-9gkTfEnMqQbgoF5x6hhRnkT4a0hzwG78ygoDj_K__TZ3lfCkZ4B25K7Iu1PtvKAd1YHMFUg3lyq-p7azIsicMDGqOHHSLPDXfXNg4EaFKIi36SwfQxXE1_A"
API_URL = "https://api.minimaxi.com/v1/voice_design"

SAMPLE_DIR = Path("d:/project/WebGAL/voice-generate/samples")

# Clean prompt without potentially sensitive wording
PROMPT = "一位50多岁的男性计算机教授，声音低沉有磁性，共鸣感强，中气十足。讲话沉稳有力，语速适中偏慢但每个字都有分量。是一位思维锐利、行事果断的学术带头人。标准普通话，声音要有厚度和力量感。"

PREVIEW = "国外的方案，像别人给的鱼竿。看着好用，但鱼线多长、鱼钩多大——全捏在人家手里。华科要做的事——不是用别人的鱼竿，是造自己的渔船。"


def design_voice(prompt, preview_text):
    body = {"prompt": prompt, "preview_text": preview_text}
    for attempt in range(3):
        try:
            resp = requests.post(
                API_URL,
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json=body,
                timeout=120,
            )
            if resp.status_code == 429:
                wait = 5 * (attempt + 1)
                print(f"    Rate limited, retry in {wait}s...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            sc = data.get("base_resp", {}).get("status_code", 0)
            if sc == 1002:
                wait = 3 * (attempt + 1)
                print(f"    RPM limit, retry in {wait}s...")
                time.sleep(wait)
                continue
            if sc != 0:
                print(f"    API error {sc}: {data.get('base_resp', {}).get('status_msg', '')}")
                return None, None
            voice_id = data.get("voice_id", "")
            trial_audio_hex = data.get("trial_audio", "")
            if not voice_id:
                print("    No voice_id returned")
                return None, None
            audio_bytes = None
            if trial_audio_hex:
                try:
                    audio_bytes = bytes.fromhex(trial_audio_hex)
                except Exception as e:
                    print(f"    Hex decode error: {e}")
            return voice_id, audio_bytes
        except requests.exceptions.RequestException as e:
            print(f"    HTTP error: {e}")
            if attempt < 2:
                time.sleep(3 * (attempt + 1))
            else:
                return None, None
        except Exception as e:
            print(f"    Error: {e}")
            return None, None
    return None, None


print("Designing voice for: 李教授")
voice_id, audio = design_voice(PROMPT, PREVIEW)

if voice_id:
    print(f"  -> voice_id: {voice_id}")
    # Update voice_ids.json
    ids_path = Path("d:/project/WebGAL/voice-generate/voice_ids.json")
    with open(ids_path, "r", encoding="utf-8") as f:
        voice_ids = json.load(f)
    voice_ids["李教授"] = {"voice_id": voice_id, "prompt": PROMPT}
    with open(ids_path, "w", encoding="utf-8") as f:
        json.dump(voice_ids, f, ensure_ascii=False, indent=2)
    print("  -> voice_ids.json updated")

    if audio:
        audio_path = SAMPLE_DIR / "李教授_trial_v2.mp3"
        with open(audio_path, "wb") as f:
            f.write(audio)
        print(f"  -> saved: {audio_path}")
else:
    print("  -> FAILED")
