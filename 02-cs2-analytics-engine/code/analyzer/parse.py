"""Minimal CS2 demo parse — sanity-check the demoparser2 pipeline.

Run:
    python analyzer/parse.py demos/<your-demo>.dem
"""
import sys
from pathlib import Path

from demoparser2 import DemoParser


def parse_demo(demo_path: Path) -> dict:
    parser = DemoParser(str(demo_path))

    header = parser.parse_header()
    kills = parser.parse_event("player_death")
    plants = parser.parse_event("bomb_planted")
    defuses = parser.parse_event("bomb_defused")
    round_ends = parser.parse_event("round_end")

    return {
        "map": header.get("map_name"),
        "server": header.get("server_name"),
        "demo_version": header.get("demo_version_name"),
        "num_kills": len(kills) if kills is not None else 0,
        "num_plants": len(plants) if plants is not None else 0,
        "num_defuses": len(defuses) if defuses is not None else 0,
        "num_rounds": len(round_ends) if round_ends is not None else 0,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyzer/parse.py <path-to-demo.dem>")
        sys.exit(1)

    demo_path = Path(sys.argv[1])
    if not demo_path.exists():
        print(f"Demo not found: {demo_path}")
        sys.exit(1)

    summary = parse_demo(demo_path)
    print("=" * 50)
    print(f"Parsed: {demo_path.name}")
    print("=" * 50)
    for key, value in summary.items():
        print(f"  {key}: {value}")
