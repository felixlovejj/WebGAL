#!/usr/bin/env python3
"""
Voice Design v4 — Final adjustments:
- 王学长: voice too low, raise slightly
- 陈老师: too emotional/agitated, tone down, keep young/clean
"""

import requests, json, time
from pathlib import Path

API_KEY = "sk-api-9gkTfEnMqQbgoF5x6hhRnkT4a0hzwG78ygoDj_K__TZ3lfCkZ4B25K7Iu1PtvKAd1YHMFUg3lyq-p7azIsicMDGqOHHSLPDXfXNg4EaFKIi36SwfQxXE1_A"
API_URL = "https://api.minimaxi.com/v1/voice_design"

SAMPLE_DIR = Path("d:/project/WebGAL/voice-generate/samples")
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

voice_ids_path = Path("d:/project/WebGAL/voice-generate/voice_ids.json")

REGENERATE = [
    {
        "name": "王学长",
        "prompt": "一位32岁的男性芯片工程师，声音沉稳有力，中气十足，每个字都掷地有声。不是低沉浑厚的类型，而是音调适中有底气有自信的技术骨干，说话有分量感和说服力。标准普通话，声音要有力量和信服感，但音调不要过低。",
        "preview_text": "2024年，我们做出了全球最大容量的MRAM存算一体芯片，64兆比特，28纳米全自主。叫喻家山1号。我们不敢停，也不能停。",
    },
    {
        "name": "陈老师",
        "prompt": "一位28岁的青年男教师，声音干净清亮，语速适中干脆不拖沓。性格沉稳但不沉闷，说话有青年的朝气和干劲，但不激动不高亢。是一位理性而坚定的年轻教师，讲述知识时平静有力。标准普通话，声音干净不闷。",
        "preview_text": "新同学？快进来。今天的课在草棚里上，教学楼还没盖完。纸，和笔——这是我昨晚写的程序，47条指令，每一条都手写。",
    },
]


def design_voice(prompt, preview_text):
    body = {"prompt": prompt, "preview_text": preview_text}
    for attempt in range(3):
        try:
            resp = requests.post(
                API_URL,
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json=body, timeout=120,
            )
            if resp.status_code == 429:
                wait = 5 * (attempt + 1)
                print(f"    Rate limited, retry in {wait}s...")
                time.sleep(wait); continue
            resp.raise_for_status()
            data = resp.json()
            sc = data.get("base_resp", {}).get("status_code", 0)
            if sc == 1002:
                wait = 3 * (attempt + 1)
                print(f"    RPM limit, retry in {wait}s...")
                time.sleep(wait); continue
            if sc != 0:
                print(f"    API error {sc}: {data.get('base_resp', {}).get('status_msg', '')}")
                return None, None
            voice_id = data.get("voice_id", "")
            trial_audio_hex = data.get("trial_audio", "")
            if not voice_id:
                print("    No voice_id returned"); return None, None
            audio_bytes = None
            if trial_audio_hex:
                try:
                    audio_bytes = bytes.fromhex(trial_audio_hex)
                except Exception as e:
                    print(f"    Hex decode error: {e}")
            return voice_id, audio_bytes
        except requests.exceptions.RequestException as e:
            print(f"    HTTP error: {e}")
            if attempt < 2: time.sleep(3 * (attempt + 1))
            else: return None, None
        except Exception as e:
            print(f"    Error: {e}"); return None, None
    return None, None


def main():
    with open(voice_ids_path, "r", encoding="utf-8") as f:
        voice_ids = json.load(f)

    for i, vd in enumerate(REGENERATE):
        name = vd["name"]
        print(f"\n[{i+1}/{len(REGENERATE)}] Designing voice for: {name}")
        print(f"  Prompt: {vd['prompt'][:120]}...")

        voice_id, audio = design_voice(vd["prompt"], vd["preview_text"])

        if voice_id:
            voice_ids[name] = {"voice_id": voice_id, "prompt": vd["prompt"]}
            print(f"  -> voice_id: {voice_id}")
            if audio:
                audio_path = SAMPLE_DIR / f"{name}_trial_v4.mp3"
                with open(audio_path, "wb") as f:
                    f.write(audio)
                print(f"  -> saved: {audio_path} ({len(audio)} bytes)")
        else:
            print(f"  -> FAILED")

        if i < len(REGENERATE) - 1:
            time.sleep(4)

    with open(voice_ids_path, "w", encoding="utf-8") as f:
        json.dump(voice_ids, f, ensure_ascii=False, indent=2)
    print(f"\nUpdated voice_ids.json saved.")


if __name__ == "__main__":
    main()
