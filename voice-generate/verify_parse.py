#!/usr/bin/env python3
"""Quick verification of generate_all.py parsing"""
import sys
sys.path.insert(0, '.')

# Import the necessary parts
exec(compile(open('generate_all.py', encoding='utf-8').read(), 'generate_all.py', 'exec'))

if __name__ == '__main__':
    dialogues = parse_scene_files()
    print(f'Parsed {len(dialogues)} dialogues')

    # Check first and last
    print(f'First: {dialogues[0]["audio_filename"]} | {dialogues[0]["clean_text"][:60]}')
    print(f'Last:  {dialogues[-1]["audio_filename"]} | {dialogues[-1]["clean_text"][:60]}')

    # Check for empty text
    missing = [d for d in dialogues if not d['clean_text']]
    print(f'Empty text: {len(missing)}')

    # Check tone coverage
    from collections import Counter
    emotions = Counter(d['emotion'] for d in dialogues)
    print(f'Emotions: {dict(emotions)}')

    # Speakers
    speakers = Counter(d['speaker'] for d in dialogues)
    print(f'Speakers: {dict(speakers)}')

    # Check that all MANUAL_TONE keys have entries
    no_tone = [d for d in dialogues if not d['tone']]
    print(f'No tone override: {len(no_tone)}')
    for d in no_tone:
        print(f'  {d["audio_filename"]} | {d["speaker"]}')

    # Verify scene files will get correct refs
    print('\nScene file audio refs:')
    for d in dialogues[:3]:
        print(f'  {d["filename"]}:{d["line_num"]} -> {d["audio_filename"]}')
