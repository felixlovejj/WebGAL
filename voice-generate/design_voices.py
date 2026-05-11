#!/usr/bin/env python3
"""
Voice Design — Create custom voices via MiniMax /v1/voice_design
Generates trial audio for each character using speech-2.8-hd compatible voices.
"""

import requests, json, time, os
from pathlib import Path

API_KEY = "sk-api--P3zNstAeJ8snsPs5Ie4G-dS31aTQbcxgCWouVnbcOSBWdcB_TwASDh4stf6JWx7_bbYShWVJcfMEQLdLt7hseMwfW8iAclAU_Zwy1wYHxeaBOaPlKo3-5Y"
API_URL = "https://api.minimaxi.com/v1/voice_design"

SAMPLE_DIR = Path("d:/project/WebGAL/voice-generate/samples")
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CHARACTER VOICE DESIGNS
# ============================================================
VOICE_DESIGNS = [
    {
        "name": "林知远",
        "prompt": "一位20岁出头的理工科男大学生，声音清亮自然有朝气，带着年轻人特有的好奇和思考感。说话时既有debug时的沮丧，也有被前辈故事打动后的坚定和热血。标准普通话，真诚不做作，语速适中，像身边真实存在的同学。",
        "preview_text": "不是吧，这红黑树的旋转逻辑明明是对的啊，怎么还是段错误。",
    },
    {
        "name": "1024",
        "prompt": "一位年轻的女性AI导航员，声音清脆明亮有活力，带有科技感但亲切不机械。出场时活泼像跳跃的小精灵，讲解历史时又能沉稳有力量，结尾寄语时庄重温暖。标准普通话，像一位聪明又可靠的伙伴。",
        "preview_text": "叮！检测到一名正在debug的计算机学子。我是1024，你的历史编译助手。",
    },
    {
        "name": "陈老师",
        "prompt": "一位30岁的青年男教师，声音温和有书卷气，带着1950年代知识分子的坚韧和理想。耐心讲解时娓娓道来像讲述故事，说到国家需要时语气坚定有力。不是苍老的声音，而是有岁月感但不失朝气的青年。标准普通话。",
        "preview_text": "新同学？快进来。今天的课在草棚里上，教学楼还没盖完。",
    },
    {
        "name": "张江陵",
        "prompt": "一位45岁的男性科研工作者，声音沉稳厚重有力量，带着工程师的严谨和开拓者的自豪。讲述自主研制计算机时充满底气，回忆从零起步时略带沧桑但不消极。标准普通话，像一位让人肃然起敬的技术前辈。",
        "preview_text": "我是张江陵，1974年开始做外部存储。这是我们的DJS-112，全自主——CPU、内存、外设接口全部自己设计，全国第一个用海明码纠错的。",
    },
    {
        "name": "张工",
        "prompt": "一位38岁的男性工程师，声音浑厚有力度，语速偏慢显得稳重。谈技术自主时热切坚定，谈国外技术垄断时带着愤慨和骨气。标准普通话，像一位经历过技术封锁但从不服输的老工程师。",
        "preview_text": "我们正在搞国产微型计算机。主板自己设计，操作系统自己写——全套自主。",
    },
    {
        "name": "李教授",
        "prompt": "一位50多岁的男性计算机教授，声音深沉有磁性，从容不迫透着智者的沉稳。讲述留学和回国经历时情感真挚饱满，谈到技术和国家安全时充满使命感和力量。标准普通话，给人如沐春风的导师感觉。",
        "preview_text": "国外的方案，像别人给的鱼竿。看着好用，但鱼线多长、鱼钩多大——全捏在人家手里。华科要做的事——不是用别人的鱼竿，是造自己的渔船。",
    },
    {
        "name": "周师兄",
        "prompt": "一位22岁的男性研究生，声音阳光有冲劲，语速较快思维敏捷。谈论技术卡脖子时锐利有力，给建议时热情真诚。有年轻人的锐气但不浮躁。标准普通话，像一个有想法有态度的师兄。",
        "preview_text": "你们想过没有——为什么ChatGPT不是中国公司做出来的？从芯片到AI框架，每一层都有'卡脖子'。底层全捏在别人手里，你在上面写再多应用，不是沙上建塔吗？",
    },
    {
        "name": "苏师姐",
        "prompt": "一位24岁的女性研究生，声音知性清亮有自信，语速适中偏快显得思维敏捷。理智不情绪化，鼓励后辈时温暖有力量，不是御姐音而是高知女性的从容和睿智。标准普通话。",
        "preview_text": "别被'卡脖子'吓到。正因为他们不给，你才要自己造。这是'危'和'机'并存的时代。",
    },
    {
        "name": "王学长",
        "prompt": "一位28岁的青年男性芯片工程师，声音沉稳专业有实干感，语速适中。讲述喻家山1号芯片成果时平和但有力，谈技术挑战时理性坚定不空洞。标准普通话，给人踏实可靠的印象。",
        "preview_text": "2024年，我们做出了全球最大容量的MRAM存算一体芯片——64兆比特，28纳米全自主。叫'喻家山1号'。童薇老师说：'我们不敢停，也不能停。'",
    },
]


def design_voice(name, prompt, preview_text):
    """Call voice_design API, return (voice_id, audio_bytes)."""
    body = {
        "prompt": prompt,
        "preview_text": preview_text,
    }

    for attempt in range(3):
        try:
            resp = requests.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                },
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
                    print(f"    Audio: {len(audio_bytes)} bytes")
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
    results = {}

    for i, vd in enumerate(VOICE_DESIGNS):
        name = vd["name"]
        print(f"\n[{i+1}/{len(VOICE_DESIGNS)}] Designing voice for: {name}")
        print(f"  Prompt: {vd['prompt'][:80]}...")
        print(f"  Preview: {vd['preview_text'][:60]}...")

        voice_id, audio = design_voice(name, vd["prompt"], vd["preview_text"])

        if voice_id:
            results[name] = {
                "voice_id": voice_id,
                "prompt": vd["prompt"],
            }
            print(f"  -> voice_id: {voice_id}")

            # Save trial audio
            safe_name = name.replace(" ", "_")
            if audio:
                audio_path = SAMPLE_DIR / f"{safe_name}_trial.mp3"
                with open(audio_path, "wb") as f:
                    f.write(audio)
                print(f"  -> saved: {audio_path}")
        else:
            print(f"  -> FAILED")

        # Rate limit: max ~20 RPM, so 3s between calls
        if i < len(VOICE_DESIGNS) - 1:
            time.sleep(4)

    # Save voice_id mapping
    mapping_path = Path("d:/project/WebGAL/voice-generate/voice_ids.json")
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nVoice IDs saved to: {mapping_path}")
    print(f"Trial audio saved to: {SAMPLE_DIR}/")


if __name__ == "__main__":
    main()
