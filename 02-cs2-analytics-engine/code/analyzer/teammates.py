"""Identify teammates per round (since sides flip in CS2)."""
from demoparser2 import DemoParser


def get_teammates_per_round(parser: DemoParser, target_steamid: int) -> dict:
    """Returns dict: round_index (0-based) -> list[int] of teammate steamids."""
    round_starts = parser.parse_event("round_start")
    if round_starts is None or round_starts.empty:
        return {}

    ticks = sorted(round_starts["tick"].tolist())
    teams_df = parser.parse_ticks(["team_num"], ticks=ticks)

    teammates_per_round = {}
    for round_idx, tick in enumerate(ticks):
        tick_df = teams_df[teams_df["tick"] == tick]
        target_row = tick_df[tick_df["steamid"] == target_steamid]
        if target_row.empty:
            continue
        target_team = int(target_row["team_num"].iloc[0])
        if target_team not in (2, 3):
            continue
        teammates = tick_df[
            (tick_df["team_num"] == target_team)
            & (tick_df["steamid"] != target_steamid)
        ]["steamid"].tolist()
        teammates_per_round[round_idx] = teammates

    return teammates_per_round
