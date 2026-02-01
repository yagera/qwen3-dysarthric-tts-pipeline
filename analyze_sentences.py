from pathlib import Path
from collections import Counter
import re

def analyze_russian_sentences():
    file_path = Path("/home/gera/Downloads/russian_sentences.txt")

    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    sentences = [line.strip() for line in lines if line.strip()]

    print(f"\nBASIC STATS:")
    print(f"   Total lines in file: {len(lines)}")
    print(f"   Non-empty sentences: {len(sentences)}")
    print(f"   Empty lines: {len(lines) - len(sentences)}")

    duplicates = len(sentences) - len(set(sentences))
    unique_sentences = len(set(sentences))
    print(f"   Unique sentences: {unique_sentences}")
    print(f"   Duplicate sentences: {duplicates}")

    all_text = '\n'.join(sentences)

    print(f"\nTEXT STATS:")
    print(f"   Total characters: {len(all_text)}")
    print(f"   Total words (approx): {len(all_text.split())}")
    print(f"   Avg sentence length: {len(all_text) / len(sentences):.1f} chars")
    print(f"   Avg words per sentence: {len(all_text.split()) / len(sentences):.1f} words")

    word_lengths = [len(w) for w in all_text.split()]
    if word_lengths:
        print(f"   Min word length: {min(word_lengths)} chars")
        print(f"   Max word length: {max(word_lengths)} chars")
        print(f"   Avg word length: {sum(word_lengths) / len(word_lengths):.1f} chars")

    print(f"\nCHARACTER ANALYSIS:")
    all_chars = list(all_text)
    unique_chars = set(all_chars)
    print(f"   Total unique characters: {len(unique_chars)}")

    char_freq = Counter(all_chars)
    most_common = char_freq.most_common(10)
    print(f"\n   Top 10 most common characters:")
    for char, count in most_common:
        if char == '\n':
            display_char = "\\n"
        elif char == ' ':
            display_char = "SPACE"
        else:
            display_char = char
        percentage = (count / len(all_chars)) * 100
        print(f"      '{display_char}': {count:7d} ({percentage:5.2f}%)")

    punctuation = Counter(c for c in all_text if c in '.,;:!?-–—«»"\'()[]{}…')
    print(f"\n   Punctuation marks:")
    if punctuation:
        for char, count in sorted(punctuation.items(), key=lambda x: x[1], reverse=True):
            print(f"      '{char}': {count}")
    else:
        print("      None found")

    cyrillic = sum(1 for c in all_text if '\u0400' <= c <= '\u04FF')
    latin = sum(1 for c in all_text if 'a' <= c.lower() <= 'z')
    digits = sum(1 for c in all_text if c.isdigit())
    spaces = sum(1 for c in all_text if c.isspace())

    print(f"\n   Character categories:")
    print(f"      Cyrillic: {cyrillic} ({(cyrillic/len(all_text))*100:.1f}%)")
    print(f"      Latin: {latin} ({(latin/len(all_text))*100:.1f}%)")
    print(f"      Digits: {digits} ({(digits/len(all_text))*100:.1f}%)")
    print(f"      Spaces: {spaces} ({(spaces/len(all_text))*100:.1f}%)")

    special = len(all_text) - cyrillic - latin - digits - spaces
    print(f"      Special chars: {special} ({(special/len(all_text))*100:.1f}%)")

    print(f"\nSENTENCE LENGTH DISTRIBUTION:")
    sentence_lengths = [len(s) for s in sentences]
    length_buckets = Counter(l // 10 * 10 for l in sentence_lengths)

    for bucket in sorted(length_buckets.keys()):
        count = length_buckets[bucket]
        percentage = (count / len(sentences)) * 100
        bar = '█' * int(percentage / 2)
        print(f"   {bucket:3d}-{bucket+9:3d} chars: {count:5d} ({percentage:5.1f}%) {bar}")

    print(f"\n   Min sentence: {min(sentence_lengths)} chars")
    print(f"   Max sentence: {max(sentence_lengths)} chars")
    print(f"   Median: {sorted(sentence_lengths)[len(sentence_lengths)//2]} chars")

    print(f"\nSAMPLE SENTENCES (first 5):")
    for i, sent in enumerate(sentences[:5], 1):
        display = sent[:80] + "..." if len(sent) > 80 else sent
        print(f"   {i}. {display}")


if __name__ == "__main__":
    try:
        analyze_russian_sentences()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()