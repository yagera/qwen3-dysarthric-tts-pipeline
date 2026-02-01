from pathlib import Path
import re

def clean_sentences_for_tts():
    file_path = Path("/home/gera/Downloads/russian_sentences.txt")
    output_path = Path("/home/gera/Downloads/russian_sentences_cleaned.txt")

    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    sentences = [line.strip() for line in lines if line.strip()]

    cleaned = []
    removed_stats = {
        'duplicates': 0,
        'too_short': 0,
        'too_long': 0,
        'contains_digits': 0,
        'contains_latin': 0,
        'multiple_dots': 0,
        'invalid_quotes': 0,
        'special_chars': 0,
        'kept': 0
    }

    seen = set()

    for sent in sentences:
        if sent in seen:
            removed_stats['duplicates'] += 1
            continue
        seen.add(sent)

        if len(sent) < 20 or len(sent) > 100:
            removed_stats['too_short' if len(sent) < 20 else 'too_long'] += 1
            continue

        if any(c.isdigit() for c in sent):
            removed_stats['contains_digits'] += 1
            continue

        if any('a' <= c.lower() <= 'z' for c in sent):
            removed_stats['contains_latin'] += 1
            continue

        if sent.count('.') > 1:
            removed_stats['multiple_dots'] += 1
            continue

        if ('«' in sent and '»' not in sent) or ('»' in sent and '«' not in sent):
            removed_stats['invalid_quotes'] += 1
            continue

        if sent.count('"') % 2 != 0:
            removed_stats['invalid_quotes'] += 1
            continue

        if bool(re.search(r'[^\w\s\-—«»",.\?!:а-яёА-ЯЁ]', sent)):
            removed_stats['special_chars'] += 1
            continue

        cleaned.append(sent)
        removed_stats['kept'] += 1

    with open(output_path, 'w', encoding='utf-8') as f:
        for sent in cleaned:
            f.write(sent + '')

    print("Cleaning Results:")
    print(f"   Original: {len(sentences)}")
    print(f"   Kept: {removed_stats['kept']}")
    print(f"   Removed: {len(sentences) - removed_stats['kept']}")
    print(f"Removal Breakdown:")
    for reason, count in sorted(removed_stats.items(), key=lambda x: x[1], reverse=True):
        if reason != 'kept':
            print(f"   {reason}: {count}")

    print(f"Saved to: {output_path}")
    print(f"Unique preserved: {len(set(cleaned))}")

if __name__ == "__main__":
    try:
        clean_sentences_for_tts()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
