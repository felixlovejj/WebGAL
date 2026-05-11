#!/usr/bin/env python3
"""Split long dialogue lines (>70 chars) into two, generate audio for new halves."""
import re, os, time, requests
from pathlib import Path
from collections import defaultdict

API_KEY = "sk-api--P3zNstAeJ8snsPs5Ie4G-dS31aTQbcxgCWouVnbcOSBWdcB_TwASDh4stf6JWx7_bbYShWVJcfMEQLdLt7hseMwfW8iAclAU_Zwy1wYHxeaBOaPlKo3-5Y"
API_URL = "https://api.minimaxi.com/v1/t2a_v2"
OUTPUT_DIR = Path("d:/project/WebGAL/packages/webgal/public/game/vocal")
SCENE_DIR = Path("d:/project/WebGAL/packages/webgal/public/game/scene")

VOICE_MAP = {
    '陈老师': ('hunyin_6', 1.02), '张江陵': ('Chinese_gravelly_storyteller_vv2', 1.00),
    '张工': ('Chinese_kind_uncle_vv1', 1.00), '李教授': ('Chinese_calm_streamer_vv1', 0.99),
    '1024': ('Arrogant_Miss', 1.07), '林知远': ('Chinese (Mandarin)_Straightforward_Boy', 1.04),
    '周师兄': ('Chinese (Mandarin)_Gentle_Youth', 1.12), '苏师姐': ('Chinese_crisp_podcaster_vv1', 1.12),
    '王学长': ('Chinese (Mandarin)_Stubborn_Friend', 1.02),
}

SPEAKER_ALIAS = {
    '林知远': 'lin', '1024': 's1024', '陈老师': 'chen', '张江陵': 'zhangjl',
    '张工': 'zhangg', '李教授': 'li', '周师兄': 'zhou', '苏师姐': 'su', '王学长': 'wang',
}
DIALOGUE_RE = re.compile(r'^([^:]+):(.+)$')
SPEAKERS = set(SPEAKER_ALIAS.keys())

# ===== STEP 1: Find current max sequence per speaker =====
max_seq = defaultdict(int)
for fn in ['hust_ch1.txt','hust_ch1_1950s.txt','hust_ch2.txt','hust_ch3.txt']:
    fp = SCENE_DIR / fn
    if not fp.exists(): continue
    with open(fp, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            m = DIALOGUE_RE.match(line) if line and not line.startswith(';') else None
            if not m: continue
            speaker = m.group(1).strip()
            if speaker not in SPEAKERS: continue
            alias = SPEAKER_ALIAS[speaker]
            # Find all audio refs in line
            for af_m in re.finditer(r'(\w+)_(\d+)\.mp3', line):
                if af_m.group(1) == alias:
                    num = int(af_m.group(2))
                    if num > max_seq[alias]:
                        max_seq[alias] = num

print("=== Current max seq ===")
for a, n in sorted(max_seq.items()):
    print(f"  {a}: {n}")

# ===== STEP 2: Define splits =====
# Format: (filename, line_number, speaker, split_point_pattern)
# split_point: regex pattern - split AFTER this match, part1 includes the match
SPLITS = [
    # ch1_1950s
    ("hust_ch1_1950s.txt", 61, "陈老师",
     "踩了三个月的坑。", "不低级。苏联专家撤走时连M-3的手册都没留下。你这个边界错误，我们当年踩了三个月的坑。",
     "珍惜每一次debug的机会——每个bug背后，都有人替你探过路。"),
    ("hust_ch1_1950s.txt", 77, "陈老师",
     '国家需要你。"', "你听说过朱九思吗？华工之父。文革刚结束，他等在关押知识分子的牛棚外面，一个一个地请——来华工吧。我们需要你。国家需要你。",
     "从1972到1979，他从全国二十多个省份招揽了六百多位老师。没有朱九思，就没有后来的华工。"),
    ("hust_ch1_1950s.txt", 102, "张工",
     "一个月工资。", "对，技术殖民。所以我们才要自己干。我们写了操作系统叫HUST-DOS，存储模块64KB——芯片从香港辗转买回，一颗等于普通人一个月工资。",
     "但现在到了一个关口——经费有限。是亮剑还是磨剑？完善系统出去展示，还是沉下心攻关32位架构？"),
    ("hust_ch1_1950s.txt", 117, "张工",
     "我们贴牌。", "HUST-DOS引起了轰动，科学院当场批了经费。但有家美国公司说可以合作——用他们的芯片和系统，我们贴牌。",
     '我拒绝了。对方走时说："没有我们的芯片，你们什么都做不出来。"'),
    ("hust_ch1_1950s.txt", 130, "张工",
     "全是无人区。", '说得好！朱九思老校长也说过——"华工要做别人做不了的事"。32位从指令集到内存管理，全是无人区。',
     "这有一本刚从国外复印回来的架构白皮书——用最简洁的设计实现最高效的计算。"),

    # ch2
    ("hust_ch2.txt", 27, "李教授",
     "从零开始做。", "我认识一位师姐。她读博时发现——国内所有的存储设备，全是进口的，没有一件Made in China。毕业后她留校，拒绝了国外高薪，从零开始做。",
     "二十年。从一个人到一个国家实验室，国产存储从不到5%做到60%以上。她的名字叫冯丹——现在是我们华科计算机学院的院长。"),
    ("hust_ch2.txt", 45, "李教授",
     '技术领先国家制定。"', '有一天读到美国国防部的《可信计算机系统评估标准》，里面说："计算机安全标准，应由技术领先国家制定。"',
     "我突然明白——标准不只是技术问题，是话语权，是规则制定权。如果我们永远跟在别人后面，就永远只能做规则的服从者。"),
    ("hust_ch2.txt", 58, "李教授",
     "好学区。", '有道理。但你知道最大的风险吗？"等一等"容易变成"回不来"。硅谷那地方——高薪、好房、好学区。',
     "待得越久，回来的阻力越大。到那时候，不是不想回来，是回不来了。"),

    # ch3
    ("hust_ch3.txt", 24, "周师兄",
     '都有"卡脖子"。', "你们想过没有——为什么ChatGPT不是中国公司做出来的？从芯片到AI框架，每一层都有卡脖子。",
     '底层全捏在别人手里，你在上面写再多应用，不是沙上建塔吗？'),
    ("hust_ch3.txt", 53, "苏师姐",
     "严重断代。", "有眼光！过去十年大家都搞AI，做系统的人严重断代。",
     "国家推自主可控，突然发现——人呢？开源RISC-V要人移植内核，国产数据库要人优化查询引擎，哪里都缺人。"),
    ("hust_ch3.txt", 87, "王学长",
     '28纳米全自主。', "2024年，我们做出了全球最大容量的MRAM存算一体芯片——64兆比特，28纳米全自主。",
     '叫喻家山1号。童薇老师说："我们不敢停，也不能停。"喻家山2号已经进入流片阶段了。'),
    ("hust_ch3.txt", 148, "林知远",
     "浪费在路上。", "现在的计算机，计算和存储是分开的。数据在处理器和存储器之间搬来搬去——功耗的七成浪费在路上。",
     "如果把计算直接做在存储芯片上，效率能提升几十上百倍。"),
    ("hust_ch3.txt", 150, "王学长",
     "不一样了。", "你要动计算机体系结构的根基啊。但是真正的卡脖子破局点——芯片制造我们短期追不上，如果在新架构上换道超车，局面就不一样了。",
     "华科是这个方向全国最好的——喻家山1号已经证明我们能做出来。"),
    ("hust_ch3.txt", 191, "林知远",
     "二十年的坚持。", "我曾经觉得爱国是很遥远的词——直到我看见了草棚教室、DJS-112、牛棚外等人的朱九思、冯丹老师二十年的坚持。",
     "我才真正明白——爱国，就是把你写的每一行代码，都当成国家未来的一部分。"),
]

print(f"\nTotal splits: {len(SPLITS)}")

# ===== STEP 3: Update scene files =====
new_audio_jobs = []  # (fn, speaker, text, emotion)

# Group splits by file
from collections import OrderedDict
file_splits = OrderedDict()
for s in SPLITS:
    fn = s[0]
    if fn not in file_splits:
        file_splits[fn] = []
    file_splits[fn].append(s)

for fn, splits in file_splits.items():
    fp = SCENE_DIR / fn
    with open(fp, 'r', encoding='utf-8') as f:
        file_lines = f.readlines()

    # Process splits in reverse line order to preserve line numbers
    for s in reversed(splits):
        fn_, lineno, speaker, split_pt, part1, part2 = s
        lineno = lineno - 1  # convert to 0-indexed

        orig_line = file_lines[lineno].rstrip('\n').rstrip('\r')
        # Extract old audio filename
        alias = SPEAKER_ALIAS[speaker]
        old_af = re.search(r'-((?:ch\w+_)?' + alias + r'_\d+\.mp3)', orig_line)
        old_fn = old_af.group(1) if old_af else None

        # New audio filename
        max_seq[alias] += 1
        new_num = max_seq[alias]
        # Extract chapter prefix from old filename
        if old_fn:
            ch_prefix = '_'.join(old_fn.split('_')[:-2]) if '_' in old_fn else ''
            new_fn = f'{ch_prefix}_{alias}_{new_num:04d}.mp3'
        else:
            new_fn = f'{alias}_{new_num:04d}.mp3'

        # New line 1 (original position, keeps old audio)
        new_line1 = f'{speaker}:{part1} -{old_fn}'
        # New line 2 (inserted after, gets new audio)
        new_line2 = f'{speaker}:{part2} -{new_fn}'

        # Make sure line endings match
        if not new_line1.endswith('\n'):
            new_line1 += '\n'
        if not new_line2.endswith('\n'):
            new_line2 += '\n'

        file_lines[lineno] = new_line1
        file_lines.insert(lineno + 1, new_line2)

        # Queue audio generation for part 2
        new_audio_jobs.append((new_fn, speaker, part2, 'calm'))

        print(f'  {fn}:{lineno+1} split [{speaker}]')
        print(f'    keep: {old_fn} -> "{part1[:60]}..."')
        print(f'    new:  {new_fn} -> "{part2[:60]}..."')

    # Write updated file
    with open(fp, 'w', encoding='utf-8') as f:
        f.writelines(file_lines)

print(f"\nScene files updated. {len(new_audio_jobs)} new audio files needed.")

# ===== STEP 4: Generate new audio =====
print("\n=== Generating new audio ===")
for i, (fn, speaker, text, emotion) in enumerate(new_audio_jobs):
    out = OUTPUT_DIR / fn
    if out.exists() and out.stat().st_size > 100:
        print(f'  [{i+1}/{len(new_audio_jobs)}] SKIP {fn} (exists)')
        continue

    voice_id, speed = VOICE_MAP[speaker]
    # Process text for TTS: add pauses
    tts_text = text.replace('——', '，<#0.2#>').replace('—', '，<#0.15#>')

    body = {
        'model': 'speech-2.8-hd', 'text': tts_text, 'stream': False,
        'voice_setting': {'voice_id': voice_id, 'speed': speed, 'vol': 1.0, 'pitch': 0, 'emotion': emotion},
        'audio_setting': {'sample_rate': 32000, 'bitrate': 128000, 'format': 'mp3', 'channel': 1},
        'output_format': 'hex',
    }

    for attempt in range(3):
        try:
            resp = requests.post(API_URL, headers={
                'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'
            }, json=body, timeout=90)
            if resp.status_code == 429:
                time.sleep(5 * (attempt + 1)); continue
            resp.raise_for_status()
            data = resp.json()
            sc = data.get('base_resp', {}).get('status_code', 0)
            if sc == 1002:
                time.sleep(3 * (attempt + 1)); continue
            if sc != 0:
                print(f'  [{i+1}/{len(new_audio_jobs)}] {speaker} API error {sc}: {data.get("base_resp",{}).get("status_msg","")}')
                break
            audio = bytes.fromhex(data.get('data', {}).get('audio', ''))
            with open(out, 'wb') as f: f.write(audio)
            print(f'  [{i+1}/{len(new_audio_jobs)}] OK {fn} [{speaker}] ({len(audio)} bytes)')
            break
        except Exception as e:
            print(f'  [{i+1}/{len(new_audio_jobs)}] {speaker} Error: {e}')
            if attempt < 2: time.sleep(3 * (attempt + 1))

    if i < len(new_audio_jobs) - 1:
        time.sleep(3.5)

print("\nDone.")
