from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Protocol
import contextlib
import logging
import shutil
import sys
import wave

import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AudioMetadata:
    file_id: str
    filename: str
    duration_sec: float
    transcription: str
    text_length: int
    original_path: Path
    new_path: Path


@dataclass(frozen=True)
class FilterConfig:
    audio_dir: Path
    excel_file: Path
    output_dir: Path
    min_duration: float = 10.0
    max_duration: float = 15.0
    target_duration: float = 12.0


class AudioReader(Protocol):
    def get_duration(self, path: Path) -> Optional[float]: ...


class WaveAudioReader:
    def get_duration(self, path: Path) -> Optional[float]:
        try:
            with contextlib.closing(wave.open(str(path), 'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                return frames / float(rate)
        except Exception as e:
            logger.error(f"Failed to read audio {path.name}: {e}")
            return None


class TranscriptionLoader:
    def __init__(self, excel_path: Path):
        self._excel_path = excel_path

    def load(self) -> dict[str, str]:
        df = pd.read_excel(self._excel_path)
        return {
            str(int(row['Число'])): row['Русская речь']
            for _, row in df.iterrows()
        }


class AudioFilter:
    def __init__(
        self,
        config: FilterConfig,
        audio_reader: AudioReader,
        transcription_loader: TranscriptionLoader
    ):
        self._config = config
        self._audio_reader = audio_reader
        self._transcription_loader = transcription_loader

    def execute(self) -> list[AudioMetadata]:
        self._validate_paths()
        self._setup_output_directories()

        transcriptions = self._transcription_loader.load()
        logger.info(f"Loaded {len(transcriptions)} transcriptions")

        audio_files = list(self._config.audio_dir.glob("*.wav"))
        logger.info(f"Found {len(audio_files)} audio files")

        return self._filter_and_copy(audio_files, transcriptions)

    def _validate_paths(self) -> None:
        if not self._config.audio_dir.exists():
            raise FileNotFoundError(f"Audio directory not found: {self._config.audio_dir}")
        if not self._config.excel_file.exists():
            raise FileNotFoundError(f"Excel file not found: {self._config.excel_file}")

    def _setup_output_directories(self) -> None:
        self._config.output_dir.mkdir(parents=True, exist_ok=True)
        self._audio_output_dir.mkdir(exist_ok=True)

    @property
    def _audio_output_dir(self) -> Path:
        return self._config.output_dir / "audio"

    def _filter_and_copy(
        self,
        audio_files: list[Path],
        transcriptions: dict[str, str]
    ) -> list[AudioMetadata]:
        filtered = []

        for audio_file in audio_files:
            duration = self._audio_reader.get_duration(audio_file)

            if duration is None:
                continue

            if not self._is_within_duration_range(duration):
                continue

            metadata = self._process_audio_file(audio_file, duration, transcriptions)
            filtered.append(metadata)

        logger.info(f"Filtered {len(filtered)} audio files")
        return filtered

    def _is_within_duration_range(self, duration: float) -> bool:
        return self._config.min_duration <= duration <= self._config.max_duration

    def _process_audio_file(
        self,
        audio_file: Path,
        duration: float,
        transcriptions: dict[str, str]
    ) -> AudioMetadata:
        file_id = audio_file.stem
        transcription = transcriptions.get(file_id, "")

        if not transcription:
            logger.warning(f"Missing transcription for {audio_file.name}")

        dest_path = self._audio_output_dir / audio_file.name
        shutil.copy2(audio_file, dest_path)

        return AudioMetadata(
            file_id=file_id,
            filename=audio_file.name,
            duration_sec=round(duration, 2),
            transcription=transcription,
            text_length=len(transcription),
            original_path=audio_file,
            new_path=dest_path
        )


class DatasetExporter:
    def __init__(self, output_dir: Path, target_duration: float):
        self._output_dir = output_dir
        self._target_duration = target_duration

    def export(self, metadata: list[AudioMetadata]) -> Path:
        df = pd.DataFrame([
            {
                'file_id': m.file_id,
                'filename': m.filename,
                'duration_sec': m.duration_sec,
                'transcription': m.transcription,
                'text_length': m.text_length,
                'original_path': str(m.original_path),
                'new_path': str(m.new_path)
            }
            for m in metadata
        ])

        df['distance_from_target'] = abs(df['duration_sec'] - self._target_duration)
        df = df.sort_values('distance_from_target').drop('distance_from_target', axis=1)

        csv_path = self._output_dir / "filtered_dataset.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')

        self._log_statistics(df)
        return csv_path

    def _log_statistics(self, df: pd.DataFrame) -> None:
        logger.info(f"Total filtered records: {len(df)}")
        logger.info(f"Duration stats - Min: {df['duration_sec'].min():.2f}s, "
                   f"Max: {df['duration_sec'].max():.2f}s, "
                   f"Mean: {df['duration_sec'].mean():.2f}s, "
                   f"Median: {df['duration_sec'].median():.2f}s")

        with_transcription = df['transcription'].notna().sum()
        logger.info(f"Transcription coverage: {with_transcription}/{len(df)}")

        if with_transcription > 0:
            logger.info(f"Avg text length: {df['text_length'].mean():.0f} chars")


def main() -> None:
    config = FilterConfig(
        audio_dir=Path("/home/gera/Downloads/archive/Disorder Voices/Disorder Voices"),
        excel_file=Path("/home/gera/Downloads/archive/Speeches.xlsx"),
        output_dir=Path("/home/gera/Downloads/filtered_dysarthric_dataset")
    )

    audio_reader = WaveAudioReader()
    transcription_loader = TranscriptionLoader(config.excel_file)

    audio_filter = AudioFilter(config, audio_reader, transcription_loader)
    metadata = audio_filter.execute()

    exporter = DatasetExporter(config.output_dir, config.target_duration)
    csv_path = exporter.export(metadata)

    logger.info(f"Pipeline completed successfully. CSV saved to: {csv_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        sys.exit(1)