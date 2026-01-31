from pathlib import Path
from typing import Optional
import contextlib
import logging
import sys
import wave
from collections import defaultdict

import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def get_audio_duration(audio_path: Path) -> Optional[float]:
    try:
        with contextlib.closing(wave.open(str(audio_path), 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            return frames / float(rate)
    except Exception as e:
        logger.error(f"Failed to read {audio_path.name}: {e}")
        return None


def analyze_durations() -> None:
    audio_dir = Path("/home/gera/Downloads/archive/Disorder Voices/Disorder Voices")

    if not audio_dir.exists():
        logger.error(f"Audio directory not found: {audio_dir}")
        return

    audio_files = list(audio_dir.glob("*.wav"))
    logger.info(f"Found {len(audio_files)} audio files")

    durations = []
    duration_buckets = defaultdict(int)

    for audio_file in audio_files:
        duration = get_audio_duration(audio_file)
        if duration is not None:
            durations.append(duration)
            bucket = int(duration)
            duration_buckets[bucket] += 1

    if not durations:
        logger.error("No valid audio files found")
        return

    logger.info("" + "="*60)
    logger.info("DURATION ANALYSIS")
    logger.info("="*60)

    for sec in sorted(duration_buckets.keys()):
        count = duration_buckets[sec]
        percentage = (count / len(durations)) * 100
        logger.info(f"{sec} sec: {count:4d} files ({percentage:5.1f}%)")

    logger.info("="*60)
    logger.info(f"Total: {len(durations)} files")
    logger.info(f"Min: {min(durations):.2f}s")
    logger.info(f"Max: {max(durations):.2f}s")
    logger.info(f"Mean: {sum(durations)/len(durations):.2f}s")

    df = pd.DataFrame({'duration': durations})
    logger.info(f"Median: {df['duration'].median():.2f}s")
    logger.info(f"Std Dev: {df['duration'].std():.2f}s")


if __name__ == "__main__":
    try:
        analyze_durations()
    except Exception as e:
        logger.exception(f"Error: {e}")
        sys.exit(1)