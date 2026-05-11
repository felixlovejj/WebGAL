#!/usr/bin/env python3
"""
Voice Design v2 — Adjust voice designs per user feedback.
- Swap 张工 <-> 张江陵
- Regenerate: 陈老师, 李教授, 苏师姐, 王学长
"""

import requests, json, time
from pathlib import Path

API_KEY = "sk-api-9gkTfEnMqQbgoF5x6hhRnkT4a0hzwG78ygoDj_K__TZ3lfCkZ4B25K7Iu1PtvKAd1YHMFUg3lyq-p7azIsicMDGqOHHSLPDXfXNg4EaFKIi36SwfQxXE1_A"
API_URL = "https://api.minimaxi.com/v1/voice_design"

SAMPLE_DIR = Path("d:/project/WebGAL/voice-generate/samples")
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

# Load existing voice IDs
voice_ids_path = Path("d:/project/WebGAL/voice-generate/voice_ids.json")
with open(voice_ids_path, "r", encoding="utf-8") as f:
    voice_ids = json.load(f)

# ============================================================
# 1. SWAP: 张工 <-> 张江陵
# ============================================================
print("Swapping 张工 <-> 张江陵 voice_ids...")
zhangg_id = voice_ids["张工"]["voice_id"]
zhangjl_id = voice_ids["张江陵"]["voice_id"]
voice_ids["张工"]["voice_id"] = zhangjl_id
voice_ids["张江陵"]["voice_id"] = zhangg_id
# Also swap prompts (the voice was designed for the other person)
zhangg_prompt = voice_ids["张工"]["prompt"]
voice_ids["张工"]["prompt"] = voice_ids["张江陵"]["prompt"]
voice_ids["张江陵"]["prompt"] = zhangg_prompt
print("  Done.")

# ============================================================
# 2. REGENERATE: 陈老师, 李教授, 苏师姐, 王学长
# ============================================================
REGENERATE = [
    {
        "name": "陈老师",
        "prompt": "一位30岁的青年男教师，声音温和清亮中透着精明，有书卷气但不木讷，语速适中稍快显得思维敏捷有活力。耐心讲解时娓娓道来，说到国家需要时语气坚定有力。不苍老，是那个年代有头脑有抱负的知识青年。标准普通话。",
        "preview_text": "新同学？快进来。今天的课在草棚里上，教学楼还没盖完。纸，和笔——这是我昨晚写的程序，47条指令，每一条都手写。",
    },
    {
        "name": "李教授",
        "prompt": "一位50多岁的男性计算机教授，头发半白但精神矍铄，声音硬朗有磁性，中气十足透着精明和力量感。不是温和的老先生，而是精明强干、思维锐利的技术领袖。语速适中偏慢但每个字都有分量，像一位经历过风浪、掌管过国家级项目的硬朗学者。标准普通话，声音要打得开，共鸣感强。",
        "preview_text": "国外的方案，像别人给的鱼竿。看着好用，但鱼线多长、鱼钩多大——全捏在人家手里。华科要做的事——不是用别人的鱼竿，是造自己的渔船。",
    },
    {
        "name": "苏师姐",
        "prompt": "一位22-23岁的女性研究生，声音知性清亮带着年轻人特有的朝气和锐气，语速适中偏快显得思维敏捷。自信但不骄傲，鼓励后辈时温暖有力。是年轻高知女性的感觉——有想法、有活力、有亲和力。标准普通话。",
        "preview_text": "别被'卡脖子'吓到。正因为他们不给，你才要自己造。这是'危'和'机'并存的时代。",
    },
    {
        "name": "王学长",
        "prompt": "一位32岁的男性芯片工程师，声音成熟稳重有厚度，语速适中，说话有分寸感。讲述喻家山1号芯片成果时平和但有力——是那种经历过项目打磨的技术骨干的从容，不是年轻人的热情洋溢。标准普通话，给人踏实可靠、值得信赖的印象。",
        "preview_text": "2024年，我们做出了全球最大容量的MRAM存算一体芯片——64兆比特，28纳米全自主。叫'喻家山1号'。童薇老师说：'我们不敢停，也不能停。'",
    },
]


def design_voice(name, prompt, preview_text):
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


def main():
    for i, vd in enumerate(REGENERATE):
        name = vd["name"]
        print(f"\n[{i+1}/{len(REGENERATE)}] Designing voice for: {name}")
        print(f"  Prompt: {vd['prompt'][:100]}...")

        voice_id, audio = design_voice(name, vd["prompt"], vd["preview_text"])

        if voice_id:
            voice_ids[name] = {
                "voice_id": voice_id,
                "prompt": vd["prompt"],
            }
            print(f"  -> voice_id: {voice_id}")

            if audio:
                audio_path = SAMPLE_DIR / f"{name}_trial_v2.mp3"
                with open(audio_path, "wb") as f:
                    f.write(audio)
                print(f"  -> saved: {audio_path}")
        else:
            print(f"  -> FAILED")

        if i < len(REGENERATE) - 1:
            time.sleep(4)

    # Save updated mapping
    with open(voice_ids_path, "w", encoding="utf-8") as f:
        json.dump(voice_ids, f, ensure_ascii=False, indent=2)
    print(f"\nUpdated voice_ids.json saved.")


if __name__ == "__main__":
    main()
