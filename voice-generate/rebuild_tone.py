#!/usr/bin/env python3
"""Rebuild MANUAL_TONE for generate_all.py after scene file changes."""
import re, sys, json
from collections import defaultdict

# ===== Read current MANUAL_TONE =====
with open('generate_all.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract MANUAL_TONE block
start = content.find('MANUAL_TONE = {')
end_str = '\n\n# ============================================================\n# TEXT PROCESSING'
end = content.find(end_str, start)
tone_section = content[start:end]

# Parse entries
old_tones = {}
current_key = None
current_val = {}
for line in tone_section.split('\n'):
    key_m = re.match(r'\s*"((?:ch\d[^"]+))"\s*:\s*\{', line)
    if key_m:
        if current_key:
            old_tones[current_key] = current_val
        current_key = key_m.group(1)
        current_val = {}
        continue
    if current_key:
        em = re.search(r'"emotion":\s*"(\w+)"', line)
        if em: current_val['emotion'] = em.group(1)
        sp = re.search(r'"speed":\s*([\d.]+)', line)
        if sp: current_val['speed'] = float(sp.group(1))
        pt = re.search(r'"pitch":\s*(-?\d+)', line)
        if pt: current_val['pitch'] = int(pt.group(1))
        tx = re.search(r'"text":\s*"(.+)"', line)
        if tx and 'text' not in current_val:
            current_val['text'] = tx.group(1)
if current_key:
    old_tones[current_key] = current_val

print(f"Parsed {len(old_tones)} old MANUAL_TONE entries")

# Build text-to-tone
def strip_tags(t):
    t = re.sub(r'<#[\d.]+#>', '', t)
    t = re.sub(r'\([a-z-]+\)', '', t)
    return t.strip()

text_to_old = {}
for key, val in old_tones.items():
    if 'text' in val:
        clean = strip_tags(val['text'])
        text_to_old[clean] = val

# ===== Parse new scene files =====
SCENE_DIR = 'd:/project/WebGAL/packages/webgal/public/game/scene'
SCENE_FILES = ['hust_ch1.txt', 'hust_ch1_1950s.txt', 'hust_ch2.txt', 'hust_ch3.txt']
SPEAKER_ALIAS = {
    '林知远': 'lin', '1024': 's1024', '陈老师': 'chen',
    '张江陵': 'zhangjl', '张工': 'zhangg', '李教授': 'li',
    '周师兄': 'zhou', '苏师姐': 'su', '王学长': 'wang',
}
DIALOGUE_RE = re.compile(r'^([^:]+):(.+)$')

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

            raw = m.group(2).strip()
            raw = re.sub(r'\s+-[a-zA-Z][a-zA-Z0-9_]*\.mp3', '', raw)
            # Remove parenthetical actions
            raw = re.sub(r'[（(][^）)]*[）)]', '', raw)

            # Try to match with old tone
            found = None
            clean_raw = strip_tags(raw)
            for old_text, old_val in text_to_old.items():
                if clean_raw == old_text:
                    found = old_val
                    break
                # Partial match for long texts
                if len(clean_raw) > 30 and len(old_text) > 30:
                    if clean_raw[:40] == old_text[:40]:
                        found = old_val
                        break

            new_entries.append({
                'key': audio_fn,
                'speaker': speaker,
                'raw_text': raw,
                'old': found,
            })

def update_pauses(t):
    def repl(m):
        val = float(m.group(1))
        if val >= 0.5: return '<#0.35#>'
        if val >= 0.3: return '<#0.2#>'
        if val >= 0.25: return '<#0.2#>'
        if val >= 0.2: return '<#0.15#>'
        return m.group(0)
    return re.sub(r'<#([\d.]+)#>', repl, t)

# Character defaults (boosted +0.07)
char_defaults = {
    '林知远': ('calm', 1.04),
    '1024': ('calm', 1.07),
    '陈老师': ('calm', 1.02),
    '张江陵': ('calm', 1.00),
    '张工': ('calm', 1.00),
    '李教授': ('calm', 0.99),
    '周师兄': ('calm', 1.12),
    '苏师姐': ('calm', 1.12),
    '王学长': ('calm', 1.02),
}

matched = 0
new_count = 0

print(f'\nTotal lines: {len(new_entries)}')
for e in new_entries:
    if e['old']: matched += 1
    else: new_count += 1
print(f'Matched: {matched}, New: {new_count}')

# Print unmatched for manual review
print('\n=== UNMATCHED (will use character defaults) ===')
for e in new_entries:
    if not e['old']:
        print(f"  {e['key']} | {e['speaker']} | {e['raw_text'][:70]}")

# ===== Generate new MANUAL_TONE code =====
print('\n\n=== GENERATING NEW MANUAL_TONE ===\n')

# Output grouped by scene file
current_file = None
for e in new_entries:
    # Determine which scene file this belongs to
    ch_prefix = e['key'].split('_')[0]
    if '1950s' in e['key']:
        scene = 'hust_ch1_1950s.txt'
    elif ch_prefix == 'ch1':
        scene = 'hust_ch1.txt'
    elif ch_prefix == 'ch2':
        scene = 'hust_ch2.txt'
    elif ch_prefix == 'ch3':
        scene = 'hust_ch3.txt'

    if scene != current_file:
        current_file = scene
        scene_names = {
            'hust_ch1.txt': '==== hust_ch1.txt (Intro: 东九楼 → 系统空间) ====',
            'hust_ch1_1950s.txt': '==== hust_ch1_1950s.txt (Chapter 1: 拓荒期) ====',
            'hust_ch2.txt': '==== hust_ch2.txt (Chapter 2: 突围期) ====',
            'hust_ch3.txt': '==== hust_ch3.txt (Chapter 3: 领航期) ====',
        }
        print(f'\n    # {scene_names[scene]}')

    tone = e['old']
    if tone and 'text' in tone:
        text = update_pauses(tone['text'])
        # Also boost speed
        old_speed = tone.get('speed', char_defaults[e['speaker']][1])
        new_speed = round(old_speed + 0.07, 2)
        if new_speed > 2.0: new_speed = 2.0
        emotion = tone.get('emotion', char_defaults[e['speaker']][0])
        print(f'    "{e["key"]}": {{')
        print(f'        "emotion": "{emotion}", "speed": {new_speed}, "pitch": 0,')
        print(f'        "text": "{text}",')
        print(f'    }},')
    else:
        # Use character defaults, create basic text
        emotion, speed = char_defaults[e['speaker']]
        text = e['raw_text'].replace('——', '，<#0.2#>').replace('—', '，<#0.15#>').replace('……', '<#0.2#>').replace('…', '<#0.15#>')
        print(f'    "{e["key"]}": {{')
        print(f'        "emotion": "{emotion}", "speed": {speed}, "pitch": 0,')
        print(f'        "text": "{text}",')
        print(f'    }},')
