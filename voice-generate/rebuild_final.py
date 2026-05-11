#!/usr/bin/env python3
"""Complete rebuild: parse scene files, match old MANUAL_TONE, generate new generate_all.py"""

import re, json
from collections import defaultdict, OrderedDict

# ===== Parse old MANUAL_TONE from gen_tone_final.py =====
old_tones = OrderedDict()  # key -> {emotion, text}
with open('gen_tone_final.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract add() calls
for m in re.finditer(r'add\("([^"]+)",\s*"([^"]+)",\s*"((?:[^"\\]|\\.)*)"\s*\)', content):
    key, emotion, text = m.groups()
    old_tones[key] = {'emotion': emotion, 'text': text}

print(f"Parsed {len(old_tones)} old MANUAL_TONE entries")

# ===== Parse scene files =====
SCENE_DIR = 'd:/project/WebGAL/packages/webgal/public/game/scene'
SCENE_FILES = ['hust_ch1.txt', 'hust_ch1_1950s.txt', 'hust_ch2.txt', 'hust_ch3.txt']
SPEAKER_ALIAS = {
    '林知远': 'lin', '1024': 's1024', '陈老师': 'chen',
    '张江陵': 'zhangjl', '张工': 'zhangg', '李教授': 'li',
    '周师兄': 'zhou', '苏师姐': 'su', '王学长': 'wang',
}
DIALOGUE_RE = re.compile(r'^([^:]+):(.+)$')

def strip_refs(t):
    t = re.sub(r'\s+-[a-zA-Z][a-zA-Z0-9_]*\.mp3', '', t)
    t = re.sub(r'[（(][^）)]*[）)]', '', t)
    return t.strip()

# Build text -> old_tone mapping (strip pause tags for matching)
def strip_all(t):
    t = re.sub(r'<#[\d.]+#>', '', t)
    t = re.sub(r'\([a-z-]+\)', '', t)
    return t.strip()

text_to_old = {}
for key, val in old_tones.items():
    clean = strip_all(val['text'])
    text_to_old[clean] = val

seq = defaultdict(int)
new_entries = []

for fn in SCENE_FILES:
    fp = f'{SCENE_DIR}/{fn}'
    stem = fn.replace('.txt', '')
    ch_prefix = '_'.join(stem.split('_')[1:]) if '_' in stem else stem

    with open(fp, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(';'): continue
            m = DIALOGUE_RE.match(line)
            if not m: continue
            speaker = m.group(1).strip()
            if speaker not in SPEAKER_ALIAS: continue

            alias = SPEAKER_ALIAS[speaker]
            seq[alias] += 1
            audio_fn = f'{ch_prefix}_{alias}_{seq[alias]:04d}'

            raw = strip_refs(m.group(2).strip())

            # Try to match with old tone
            matched = None
            clean_raw = strip_all(raw)
            for old_text, old_val in text_to_old.items():
                if clean_raw == old_text:
                    matched = old_val
                    break
                if len(clean_raw) > 20 and len(old_text) > 20:
                    if clean_raw[:40] == old_text[:40]:
                        matched = old_val
                        break

            new_entries.append({
                'key': audio_fn,
                'speaker': speaker,
                'raw_text': raw,
                'matched': matched,
            })

print(f"New entries: {len(new_entries)}")
matched_count = sum(1 for e in new_entries if e['matched'])
print(f"Matched: {matched_count}, Unmatched: {len(new_entries) - matched_count}")

# Print unmatched for manual check
unmatched = [e for e in new_entries if not e['matched']]
if unmatched:
    print("\n=== UNMATCHED ===")
    for e in unmatched:
        print(f"  {e['key']} | {e['speaker']} | {e['raw_text'][:70]}")

# ===== Generate new MANUAL_TONE section =====
print("\n\n=== GENERATING MANUAL_TONE ===")
print(f"# Total entries: {len(new_entries)}")
print("MANUAL_TONE = {")

last_scene = None
for e in new_entries:
    key = e['key']
    if '1950s' in key:
        scene = 'ch1_1950s'
    elif key.startswith('ch1_'):
        scene = 'ch1'
    elif key.startswith('ch2_'):
        scene = 'ch2'
    else:
        scene = 'ch3'

    if scene != last_scene:
        last_scene = scene
        names = {
            'ch1': 'hust_ch1.txt (序章)',
            'ch1_1950s': 'hust_ch1_1950s.txt (拓荒期)',
            'ch2': 'hust_ch2.txt (突围期)',
            'ch3': 'hust_ch3.txt (领航期)',
        }
        print(f"\n    # {names[scene]}")

    if e['matched']:
        emotion = e['matched']['emotion']
        text = e['matched']['text']
    else:
        # Default based on speaker
        defaults = {'林知远': 'calm', '1024': 'calm', '陈老师': 'calm',
                    '张江陵': 'calm', '张工': 'calm', '李教授': 'calm',
                    '周师兄': 'calm', '苏师姐': 'calm', '王学长': 'calm'}
        emotion = defaults.get(e['speaker'], 'calm')
        text = e['raw_text'].replace('——', '，<#0.2#>').replace('—', '，<#0.15#>').replace('……', '<#0.2#>')

    # Escape for Python string
    text_escaped = text.replace('\\', '\\\\').replace('"', '\\"')
    print(f'    "{key}": {{')
    print(f'        "emotion": "{emotion}",')
    print(f'        "text": "{text_escaped}",')
    print(f'    }},')

print("}")
print(f"\n# Total: {len(new_entries)} entries")
