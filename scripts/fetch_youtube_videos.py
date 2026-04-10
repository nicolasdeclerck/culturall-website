#!/usr/bin/env python3
"""Fetch the latest videos from a YouTube channel and output structured JSON.

Requires: yt-dlp (pip install yt-dlp)

Usage:
    python scripts/fetch_youtube_videos.py                          # default channel
    python scripts/fetch_youtube_videos.py --channel @other-channel
    python scripts/fetch_youtube_videos.py --count 5
    python scripts/fetch_youtube_videos.py --output videos.json     # write to file
"""

import argparse
import json
import subprocess
import sys

DEFAULT_CHANNEL = "@cultur-all"
DEFAULT_COUNT = 10


def fetch_videos(channel: str, count: int) -> list[dict]:
    """Use yt-dlp to retrieve the latest videos from a YouTube channel."""
    url = f"https://www.youtube.com/{channel}/videos"

    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print-json",
        "--playlist-end", str(count),
        url,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"yt-dlp error:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    videos = []
    for line in result.stdout.strip().splitlines():
        entry = json.loads(line)
        video_id = entry.get("id", "")
        description = entry.get("description") or ""

        videos.append({
            "title": entry.get("title", ""),
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "description": description[:200].strip(),
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
        })

    return videos


def main():
    parser = argparse.ArgumentParser(
        description="Fetch latest YouTube videos as structured JSON."
    )
    parser.add_argument(
        "--channel",
        default=DEFAULT_CHANNEL,
        help=f"YouTube channel handle (default: {DEFAULT_CHANNEL})",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=DEFAULT_COUNT,
        help=f"Number of videos to fetch (default: {DEFAULT_COUNT})",
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: stdout)",
    )
    args = parser.parse_args()

    videos = fetch_videos(args.channel, args.count)

    json_output = json.dumps(videos, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_output + "\n")
        print(f"Wrote {len(videos)} videos to {args.output}")
    else:
        print(json_output)


if __name__ == "__main__":
    main()
