#!/usr/bin/env python3
"""
WebGAL HUST Voice Generation — MiniMax speech-02-hd
Per-line manual tone assignment, emotion-rich, natural delivery.
Usage:
  python generate_all.py          # generate all lines
  python generate_all.py --sample # generate one sample per speaker only
"""

import os, re, time, sys, requests
from pathlib import Path
from collections import defaultdict

# ============================================================
# CONFIGURATION
# ============================================================
API_KEY = "sk-api-9gkTfEnMqQbgoF5x6hhRnkT4a0hzwG78ygoDj_K__TZ3lfCkZ4B25K7Iu1PtvKAd1YHMFUg3lyq-p7azIsicMDGqOHHSLPDXfXNg4EaFKIi36SwfQxXE1_A"
API_URL = "https://api.minimaxi.com/v1/t2a_v2"
MODEL = "speech-02-hd"

SCENE_DIR = Path("d:/project/WebGAL/packages/webgal/public/game/scene")
SCENE_FILES = ["hust_ch1.txt", "hust_ch1_1950s.txt", "hust_ch2.txt", "hust_ch3.txt"]
OUTPUT_DIR = Path("d:/project/WebGAL/packages/webgal/public/game/vocal")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# SPEAKER VOICE MAPPING (jingpin for higher quality)
# ============================================================
SPEAKER_CONFIG = {
    "林知远": {
        "voice_id": "male-qn-qingse-jingpin",   # 青涩青年·精品 — young student protagonist
        "alias": "lin", "speed": 1.0, "pitch": 0, "default_emotion": "calm",
    },
    "1024": {
        "voice_id": "female-chengshu-jingpin",   # 成熟女性·精品 — wise, calm system guide
        "alias": "s1024", "speed": 1.0, "pitch": 0, "default_emotion": "calm",
    },
    "陈老师": {
        "voice_id": "male-qn-daxuesheng-jingpin", # 青年大学生·精品 — younger, grad-student teacher
        "alias": "chen", "speed": 0.98, "pitch": 0, "default_emotion": "calm",
    },
    "张江陵": {
        "voice_id": "male-qn-jingying-jingpin",   # 精英青年·精品 — authoritative pioneer
        "alias": "zhangjl", "speed": 0.93, "pitch": -2, "default_emotion": "calm",
    },
    "张工": {
        "voice_id": "audiobook_male_2",           # 男声有声书2 — deep engineer voice
        "alias": "zhangg", "speed": 0.95, "pitch": -2, "default_emotion": "calm",
    },
    "李教授": {
        "voice_id": "presenter_male",              # 男播音员 — authoritative, powerful
        "alias": "li", "speed": 0.92, "pitch": -1, "default_emotion": "calm",
    },
    "周师兄": {
        "voice_id": "male-qn-daxuesheng-jingpin", # 青年大学生·精品 — young energetic senior
        "alias": "zhou", "speed": 1.08, "pitch": 2, "default_emotion": "calm",
    },
    "苏师姐": {
        "voice_id": "presenter_female",             # 女播音员 — 高知女性, intellectual
        "alias": "su", "speed": 1.08, "pitch": 1, "default_emotion": "calm",
    },
    "王学长": {
        "voice_id": "male-qn-jingying-jingpin",   # 精英青年·精品 — determined, steady
        "alias": "wang", "speed": 0.97, "pitch": 0, "default_emotion": "calm",
    },
}

# ============================================================
# PER-LINE MANUAL TONE ASSIGNMENT
# emotion: happy, sad, angry, surprised, fearful, calm, whisper, fluent
# speed: 0.5-2.0, pitch: -12 to 12
# ============================================================
MANUAL_TONE = {
    # ====== hust_ch1.txt (Intro: 东九楼 → 系统空间) ======
    "ch1_lin_0001":    {"emotion": "sad"},        # 自言自语debug失败，有点沮丧
    "ch1_s1024_0001":  {"emotion": "happy", "speed": 1.12},  # 叮！活泼登场
    "ch1_lin_0002":    {"emotion": "surprised", "speed": 1.08},  # 什么情况？！幻觉？
    "ch1_s1024_0002":  {"emotion": "calm", "speed": 0.97},  # 耐心解释系统
    "ch1_s1024_0003":  {"emotion": "happy", "speed": 1.05},  # 准备好了吗？期待

    # ====== hust_ch1_1950s.txt (Chapter 1: 拓荒期) ======
    # --- 1958年 华中工学院 草棚教室 ---
    "ch1_1950s_chen_0001":  {"emotion": "happy"},       # 新同学？快进来。热情招呼
    "ch1_1950s_s1024_0004": {"emotion": "calm", "speed": 0.95},  # 旁白：全校没有计算机
    "ch1_1950s_lin_0003":   {"emotion": "surprised"},    # 没有计算机怎么学？惊讶
    "ch1_1950s_chen_0002":  {"emotion": "calm", "speed": 0.93},  # 纸，和笔。耐心说明
    "ch1_1950s_chen_0003":  {"emotion": "calm", "speed": 0.95},  # 排队上机，每人六分钟
    "ch1_1950s_chen_0004":  {"emotion": "calm"},        # 老师自己都没见过计算机
    # --- 机房 ---
    "ch1_1950s_chen_0005":  {"emotion": "calm", "speed": 0.93},  # 王老师时间段空出来了
    # Branch A: 分享
    "ch1_1950s_lin_0004":   {"emotion": "calm"},        # 把时间给学弟吧
    "ch1_1950s_chen_0006":  {"emotion": "happy", "speed": 1.05},  # 愣了，笑了
    "ch1_1950s_lin_0005":   {"emotion": "calm"},        # 我的不急，他的更重要
    "ch1_1950s_chen_0007":  {"emotion": "calm", "speed": 0.9},   # 最怕人心散了。深沉
    "ch1_1950s_chen_0008":  {"emotion": "happy", "speed": 0.95},  # 学弟后来成了CAD主程。欣慰
    # Branch B: 抓住机会
    "ch1_1950s_lin_0006":   {"emotion": "sad"},          # 还差一个bug没找到
    "ch1_1950s_chen_0009":  {"emotion": "calm"},         # 行。搞技术该专注就专注
    "ch1_1950s_lin_0007":   {"emotion": "happy", "speed": 1.1},  # 就是这个！！找到了！
    "ch1_1950s_chen_0010":  {"emotion": "calm", "speed": 0.92},  # 每个bug背后都有人探过路
    "ch1_1950s_lin_0008":   {"emotion": "calm"},         # debug好像也没那么痛苦了
    # --- 1970s 朱九思 ---
    "ch1_1950s_s1024_0005": {"emotion": "calm", "speed": 0.93},  # 旁白：朱九思改变华工
    "ch1_1950s_chen_0011":  {"emotion": "calm", "speed": 0.88, "pitch": -1},  # 牛棚外请人，庄重
    "ch1_1950s_chen_0012":  {"emotion": "calm"},         # 敢于竞争善于转化
    # --- 1973年 张江陵 DJS-112 ---
    "ch1_1950s_zhangjl_0001": {"emotion": "calm", "speed": 0.93, "pitch": -1},  # 全自主DJS-112，自豪
    "ch1_1950s_zhangjl_0002": {"emotion": "calm", "speed": 0.93, "pitch": -1},  # 自己做磁头绕线圈
    "ch1_1950s_lin_0009":   {"emotion": "calm"},         # 不是做不出来是还没开始做
    # --- 1980s 张工 ---
    "ch1_1950s_zhangg_0001": {"emotion": "calm"},         # 国产微机全自主
    "ch1_1950s_lin_0010":   {"emotion": "surprised", "speed": 1.1},  # 全自主？！80年代？！
    "ch1_1950s_zhangg_0002": {"emotion": "sad", "speed": 0.92},  # 修一次够买半年材料。沉重
    "ch1_1950s_lin_0011":   {"emotion": "angry", "speed": 1.05},  # 这不就是技术殖民？愤怒
    "ch1_1950s_zhangg_0003": {"emotion": "calm", "speed": 0.93},  # 芯片辗转买回，一颗等于一个月工资
    # Branch C: 亮剑
    "ch1_1950s_lin_0012":   {"emotion": "calm"},         # 应该先展示
    "ch1_1950s_zhangg_0004": {"emotion": "happy", "speed": 1.05},  # 好！全力备战！
    "ch1_1950s_zhangg_0005": {"emotion": "angry", "speed": 0.95},  # "没有我们的芯片..." 愤怒回忆
    "ch1_1950s_lin_0013":   {"emotion": "sad"},          # 贴牌…现在也很耳熟
    "ch1_1950s_zhangg_0006": {"emotion": "calm", "speed": 0.9},   # 敢于竞争不是为了赢谁
    # Branch D: 磨剑
    "ch1_1950s_lin_0014":   {"emotion": "calm"},         # 应该沉下来攻关
    "ch1_1950s_zhangg_0007": {"emotion": "happy", "speed": 1.08, "pitch": 1},  # 猛拍桌子，说得好！
    "ch1_1950s_lin_0015":   {"emotion": "happy", "speed": 1.05},  # 那我们就做第一个！
    "ch1_1950s_zhangg_0008": {"emotion": "sad", "speed": 0.9},   # 可惜经费断了，人才流失
    "ch1_1950s_s1024_0006": {"emotion": "calm"},         # 善于转化
    # --- 章末 ---
    "ch1_1950s_s1024_0007": {"emotion": "calm", "speed": 0.92},  # 爱国是每一个具体的选择
    "ch1_1950s_s1024_0008": {"emotion": "calm"},         # 下一站预告

    # ====== hust_ch2.txt (Chapter 2: 突围期) ======
    # --- 开场 ---
    "ch2_s1024_0009":  {"emotion": "calm", "speed": 0.93},  # 1990年代末，互联网浪潮
    "ch2_s1024_0010":  {"emotion": "calm", "speed": 0.9, "pitch": -1},  # 存储100%被垄断。严肃
    # --- 李教授登场 ---
    "ch2_li_0001":     {"emotion": "calm"},         # 帮我跑一下测试
    "ch2_lin_0016":    {"emotion": "calm"},         # 为什么还要从零做？好奇
    "ch2_li_0002":     {"emotion": "calm", "speed": 0.92},  # 不是用别人的鱼竿，是造自己的渔船
    "ch2_li_0003":     {"emotion": "calm", "speed": 0.9},   # 存储国家队历史。自豪
    # --- 冯丹 ---
    "ch2_li_0004":     {"emotion": "calm", "speed": 0.88, "pitch": -1},  # 冯丹的故事。深情讲述
    "ch2_li_0005":     {"emotion": "calm"},         # 王浩想回国，你怎么看？
    # Branch E: 回国
    "ch2_lin_0017":    {"emotion": "calm"},         # 应该回来
    "ch2_li_0006":     {"emotion": "happy", "speed": 0.95},  # 欣慰地笑
    "ch2_li_0007":     {"emotion": "calm", "speed": 0.93},  # 德国做访问学者
    "ch2_lin_0018":    {"emotion": "surprised"},     # 那您为什么回来？
    "ch2_li_0008":     {"emotion": "calm", "speed": 0.88, "pitch": -1},  # 读到美国国防部标准。震撼
    "ch2_li_0009":     {"emotion": "calm", "speed": 0.9},   # 第二天，我回复导师——我要回中国
    "ch2_lin_0019":    {"emotion": "calm", "speed": 0.92},  # 计服报国原来是这么写的。感慨
    # Branch F: 先积累
    "ch2_lin_0020":    {"emotion": "calm"},         # 可以再留几年
    "ch2_li_0010":     {"emotion": "calm", "speed": 0.9},   # 待得越久回来阻力越大
    "ch2_lin_0021":    {"emotion": "sad", "speed": 0.7},    # 沉默……
    "ch2_li_0011":     {"emotion": "calm", "speed": 0.88},  # 放弃选择的权利。意味深长
    "ch2_lin_0022":    {"emotion": "calm"},         # 什么时候以什么方式回来
    "ch2_s1024_0011":  {"emotion": "calm", "speed": 0.92},  # 爱国不是非此即彼
    # --- 2010s 华光 ---
    "ch2_li_0012":     {"emotion": "calm"},         # 华光-R技术介绍
    "ch2_li_0013":     {"emotion": "calm"},         # 国际标准选择
    # Branch G: 兼容
    "ch2_lin_0023":    {"emotion": "calm"},         # 应该先兼容
    "ch2_li_0014":     {"emotion": "calm", "speed": 0.95},  # 既在规则内又在规则外
    "ch2_lin_0024":    {"emotion": "calm"},         # 善于转化
    "ch2_li_0015":     {"emotion": "happy"},         # 这就是善于转化。肯定
    # Branch H: 自研
    "ch2_lin_0025":    {"emotion": "calm"},         # 应该走自己的路
    "ch2_li_0016":     {"emotion": "calm", "speed": 0.93},  # 前几代卖不出去
    "ch2_lin_0026":    {"emotion": "surprised"},     # 那您还选这条路？
    "ch2_li_0017":     {"emotion": "calm", "speed": 0.9},   # 选了，而且对了。坚定
    "ch2_li_0018":     {"emotion": "calm", "speed": 0.9},   # 不能只看短期市场得失
    "ch2_lin_0027":    {"emotion": "calm"},         # 敢于竞争不是口号
    # --- IO500 ---
    "ch2_li_0019":     {"emotion": "happy", "speed": 0.95},  # IO500世界第一！画外音
    "ch2_li_0020":     {"emotion": "calm", "speed": 0.9, "pitch": -1},  # 不是跟在别人后面——是领先
    # --- 章末 ---
    "ch2_s1024_0012":  {"emotion": "calm", "speed": 0.9},   # 技术从来不只是技术
    "ch2_s1024_0013":  {"emotion": "calm"},         # 下面是你自己要做选择的时代了

    # ====== hust_ch3.txt (Chapter 3: 领航期) ======
    # --- 开场 ---
    "ch3_s1024_0014":  {"emotion": "calm", "speed": 0.9},   # 你从1958走到了现在。深沉
    "ch3_lin_0028":    {"emotion": "calm", "speed": 0.93},  # 回过神来，东九楼还是东九楼
    # --- 创新班教室 ---
    "ch3_zhou_0001":   {"emotion": "calm", "speed": 1.02},  # 为什么ChatGPT不是中国做的？
    "ch3_lin_0029":    {"emotion": "calm"},         # 我们缺的不是一个点
    "ch3_su_0001":     {"emotion": "calm"},         # 别被卡脖子吓到
    "ch3_zhou_0002":   {"emotion": "calm", "speed": 1.02},  # 两个方向
    # Branch I: AI应用
    "ch3_lin_0030":    {"emotion": "calm"},         # 想做AI应用方向
    "ch3_su_0002":     {"emotion": "calm", "speed": 1.03},  # 大多数人都会这么选
    "ch3_zhou_0003":   {"emotion": "happy", "speed": 1.05},  # AI用在最卡脖子的地方
    "ch3_lin_0031":    {"emotion": "calm"},         # 做AI不是目的
    # Branch J: 底层系统
    "ch3_lin_0032":    {"emotion": "calm"},         # 想做底层基础软件
    "ch3_su_0003":     {"emotion": "happy", "speed": 1.05},  # 有眼光！
    "ch3_zhou_0004":   {"emotion": "calm"},         # 底层比较苦
    "ch3_lin_0033":    {"emotion": "calm", "speed": 0.93},  # 调页表再苦也比LED灯看寄存器幸福
    "ch3_su_0004":     {"emotion": "happy", "speed": 1.03},  # 有故事，拉你进小组
    # --- 2026年 ---
    "ch3_s1024_0015":  {"emotion": "calm", "speed": 0.9, "pitch": -1},  # 你经历了三个时代
    "ch3_su_0005":     {"emotion": "calm", "speed": 0.97},  # 第一条路：创业
    "ch3_zhou_0005":   {"emotion": "calm", "speed": 1.0},   # 第二条路：国家队
    "ch3_s1024_0016":  {"emotion": "calm", "speed": 0.93},  # 还有第三条
    # --- 喻家山1号 ---
    "ch3_wang_0001":   {"emotion": "calm", "speed": 0.93},  # 64兆比特MRAM存算一体芯片
    "ch3_s1024_0017":  {"emotion": "calm", "speed": 0.93},  # 你的选择是什么？
    # Branch K: 创业
    "ch3_lin_0034":    {"emotion": "calm", "speed": 0.95},  # 我选择创业
    "ch3_su_0006":     {"emotion": "happy", "speed": 1.05},  # 欢迎！奶茶算公司福利
    "ch3_s1024_0018":  {"emotion": "calm", "speed": 0.9},   # 四十年前也是这样开始的
    # Branch L: 国家队
    "ch3_lin_0035":    {"emotion": "calm"},         # 我选择加入国家队
    "ch3_zhou_0006":   {"emotion": "happy", "speed": 1.05},  # GPU当成一台机器用
    "ch3_lin_0036":    {"emotion": "calm"},         # 跨地域调度
    "ch3_zhou_0007":   {"emotion": "happy", "speed": 1.05},  # 这就是最有意思的挑战
    "ch3_s1024_0019":  {"emotion": "calm", "speed": 0.9},   # 不是去追风口
    # Branch M: 深造
    "ch3_lin_0037":    {"emotion": "calm"},         # 我选择读博
    "ch3_lin_0038":    {"emotion": "calm", "speed": 0.95},  # 存算一体解释
    "ch3_wang_0002":   {"emotion": "calm", "speed": 0.93},  # 你要动体系结构根基
    "ch3_wang_0003":   {"emotion": "calm", "speed": 0.93},  # 冷板凳，五年出不了大成果
    "ch3_lin_0039":    {"emotion": "calm", "speed": 0.92},  # 没关系，引李教授的话
    "ch3_s1024_0020":  {"emotion": "calm", "speed": 0.9},   # 你选的不是学位
    # --- 终章 ---
    "ch3_s1024_0021":  {"emotion": "calm", "speed": 0.85, "pitch": -1},  # 无论你选了哪条路。深情
    "ch3_s1024_0022":  {"emotion": "calm", "speed": 0.82, "pitch": -1},  # 代码为谁而写？灵魂拷问
    "ch3_li_0021":     {"emotion": "calm", "speed": 0.85, "pitch": -2},  # 画外音：AI霸权算力霸权
    # --- 主角独白 ---
    "ch3_lin_0040":    {"emotion": "calm", "speed": 0.88, "pitch": -1},  # 我曾经觉得爱国是很遥远的词
    "ch3_lin_0041":    {"emotion": "calm", "speed": 0.85, "pitch": -1},  # 每一位计算机人都是1024字节中的一个比特
}

# ============================================================
# TEXT PROCESSING
# ============================================================
def process_tts_text(text):
    """Clean and prepare text for TTS:
    - Remove parenthetical actions
    - Remove any leftover mp3 references
    - Replace em-dashes with pauses
    """
    # Strip leftover mp3 references
    text = re.sub(r'\s+-[a-zA-Z][a-zA-Z0-9_]*\.mp3', '', text)
    # Remove （...） parentheticals
    text = re.sub(r'[（(][^）)]*[）)]', '', text)
    # Replace em-dashes with Chinese comma for better pauses
    text = text.replace('——', '，')
    text = text.replace('—', '，')
    # Clean up consecutive commas and whitespace
    text = re.sub(r'，+', '，', text)
    text = re.sub(r'\s+', '', text)
    return text.strip()

DIALOGUE_RE = re.compile(r'^([^:]+):(.+)$')

def detect_action_text(text):
    """Extract parenthetical action from text."""
    m = re.match(r'^[（(]([^）)]*)[）)]', text)
    if m:
        return m.group(1), text[m.end():].strip()
    return None, text

# ============================================================
# PARSING
# ============================================================
def parse_scene_files():
    dialogues = []
    speaker_seq = defaultdict(int)

    for filename in SCENE_FILES:
        filepath = SCENE_DIR / filename
        if not filepath.exists():
            continue

        stem = filepath.stem
        ch_prefix = "_".join(stem.split("_")[1:]) if "_" in stem else stem

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

            action_text, _ = detect_action_text(raw_text)
            clean_text = process_tts_text(raw_text)
            alias = SPEAKER_CONFIG[speaker]["alias"]
            speaker_seq[alias] += 1
            seq = speaker_seq[alias]
            audio_fn = f"{ch_prefix}_{alias}_{seq:04d}.mp3"

            # Get tone override (strip .mp3 for key lookup)
            tone = MANUAL_TONE.get(audio_fn.replace('.mp3', ''), {})
            emotion = tone.get("emotion", SPEAKER_CONFIG[speaker]["default_emotion"])

            dialogues.append({
                "file": filepath, "filename": filename,
                "line_num": i, "original_line": line_text.strip(),
                "speaker": speaker, "alias": alias,
                "raw_text": raw_text, "clean_text": clean_text,
                "action": action_text, "emotion": emotion,
                "audio_filename": audio_fn, "seq": seq,
                "tone": tone,  # full override dict
            })

    return dialogues

# ============================================================
# API CALL
# ============================================================
def generate_audio(dialogue, max_retries=3):
    config = SPEAKER_CONFIG[dialogue["speaker"]]
    tone = dialogue.get("tone", {})
    emotion = tone.get("emotion", config["default_emotion"])
    speed = tone.get("speed", config["speed"])
    pitch = tone.get("pitch", config["pitch"])

    voice_setting = {
        "voice_id": config["voice_id"],
        "speed": speed,
        "vol": 1.0,
        "pitch": pitch,
        "emotion": emotion,
    }

    body = {
        "model": MODEL,
        "text": dialogue["clean_text"],
        "stream": False,
        "voice_setting": voice_setting,
        "audio_setting": {
            "sample_rate": 32000, "bitrate": 128000,
            "format": "mp3", "channel": 1,
        },
        "output_format": "hex",
        "language_boost": "Chinese",
    }

    for attempt in range(max_retries):
        try:
            resp = requests.post(
                API_URL,
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json=body, timeout=60,
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
            if attempt < max_retries - 1:
                time.sleep(3 * (attempt + 1))
            else:
                return None
        except Exception as e:
            print(f"    Error: {e}", flush=True); return None
    return None

# ============================================================
# UPDATE SCENE FILES
# ============================================================
def update_scene_file(filepath, dialogues_in_file):
    if not dialogues_in_file:
        return
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    line_updates = {d["line_num"]: d["audio_filename"] for d in dialogues_in_file}

    for line_num in sorted(line_updates.keys(), reverse=True):
        line = lines[line_num].rstrip("\n").rstrip("\r")
        fn = line_updates[line_num]
        stripped = re.sub(r'\s+-[a-zA-Z][a-zA-Z0-9_]*\.mp3', '', line)
        if stripped.endswith(";"):
            stripped = stripped.rstrip(";").rstrip()
            lines[line_num] = f"{stripped} -{fn};\n"
        else:
            lines[line_num] = f"{stripped.rstrip()} -{fn}\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)

# ============================================================
# MAIN
# ============================================================
def main():
    sample_mode = "--sample" in sys.argv

    print("=" * 60, flush=True)
    print(f"WebGAL HUST Voice Gen — {MODEL} {'(SAMPLES ONLY)' if sample_mode else '(FULL)'}", flush=True)
    print("=" * 60, flush=True)

    # Parse
    print("\n[1/3] Parsing...", flush=True)
    dialogues = parse_scene_files()
    print(f"  {len(dialogues)} dialogue lines", flush=True)

    # Sample mode: pick one per speaker
    if sample_mode:
        seen = set()
        samples = []
        for d in dialogues:
            if d["alias"] not in seen:
                seen.add(d["alias"])
                samples.append(d)
        dialogues = samples
        print(f"  Sample mode: {len(dialogues)} lines (one per speaker)", flush=True)

    # Preview tones
    print("\n[2/3] Preview:", flush=True)
    for d in dialogues[:15]:
        tone = d["tone"]
        cfg = SPEAKER_CONFIG[d["speaker"]]
        spd = tone.get("speed", cfg["speed"])
        em = tone.get("emotion", cfg["default_emotion"])
        print(f"  {d['speaker']}({d['alias']}) emo={em} spd={spd:.2f} -> {d['audio_filename']}", flush=True)
        print(f"    \"{d['clean_text'][:80]}\"", flush=True)

    # Generate
    print(f"\n[3/3] Generating {len(dialogues)} lines...", flush=True)
    success, fail = 0, 0
    CALL_DELAY = 3.5

    for idx, d in enumerate(dialogues):
        out = OUTPUT_DIR / d["audio_filename"]
        if out.exists() and out.stat().st_size > 100:
            print(f"  [{idx+1}/{len(dialogues)}] SKIP {d['audio_filename']}", flush=True)
            success += 1; continue
        elif out.exists():
            out.unlink()

        tone = d["tone"]
        cfg = SPEAKER_CONFIG[d["speaker"]]
        em = tone.get("emotion", cfg["default_emotion"])
        spd = tone.get("speed", cfg["speed"])
        print(f"  [{idx+1}/{len(dialogues)}] {d['speaker']}({em}, spd={spd:.2f}) "
              f"\"{d['clean_text'][:55]}\" -> {d['audio_filename']}", flush=True)

        audio = generate_audio(d)
        if audio:
            with open(out, "wb") as f:
                f.write(audio)
            print(f"    OK {len(audio)} bytes", flush=True)
            success += 1
        else:
            print(f"    FAILED", flush=True)
            fail += 1

        if idx < len(dialogues) - 1:
            time.sleep(CALL_DELAY)

    print(f"\n  {success} ok, {fail} failed", flush=True)

    # Update files
    if not sample_mode and fail == 0:
        print("\nUpdating scene files...", flush=True)
        by_file = defaultdict(list)
        for d in parse_scene_files():
            by_file[d["file"]].append(d)
        for fp, fds in by_file.items():
            update_scene_file(fp, fds)
            print(f"  {fp.name}: {len(fds)} refs", flush=True)

    print("\nDone.", flush=True)

if __name__ == "__main__":
    main()
