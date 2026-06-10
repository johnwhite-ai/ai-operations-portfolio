"""Find CS2 demos on disk."""
from pathlib import Path

DEFAULT_REPLAYS_DIR = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\replays"
)


def find_demos(replays_dir: Path = DEFAULT_REPLAYS_DIR) -> list[Path]:
    if not replays_dir.exists():
        return []
    return sorted(replays_dir.glob("*.dem"))
