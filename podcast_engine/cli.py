import argparse
import sys

from podcast_engine.logger import get_logger
from podcast_engine.main import process_episode

logger = get_logger("podcast_engine.cli")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Offline podcast transcription and summarisation engine for Spotify episodes.",
    )
    parser.add_argument("episode_url", help="Spotify podcast episode URL")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        process_episode(args.episode_url)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Processing failed", extra={"error": str(exc)})
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
