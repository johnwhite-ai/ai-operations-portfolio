"""Determine player side (T or CT) per round in a CS2 demo."""
from demoparser2 import DemoParser

T_SIDE = "T"
CT_SIDE = "CT"


def get_round_sides(parser: DemoParser, target_steamid: int) -> tuple[dict, list]:
    """Returns (round_sides, round_start_ticks).

    round_sides maps round_index (0-based) -> 'T' | 'CT'.
    round_start_ticks is the sorted list of round_start tick values.
    """
    round_starts = parser.parse_event("round_start")
    if round_starts is None or round_starts.empty:
        return {}, []

    ticks = sorted(round_starts["tick"].tolist())
    teams_df = parser.parse_ticks(["team_num"], ticks=ticks, players=[target_steamid])

    sides = {}
    for round_idx, tick in enumerate(ticks):
        row = teams_df[teams_df["tick"] == tick]
        if not row.empty:
            tn = int(row["team_num"].iloc[0])
            if tn == 2:
                sides[round_idx] = T_SIDE
            elif tn == 3:
                sides[round_idx] = CT_SIDE
    return sides, ticks


def side_for_tick(round_start_ticks: list, round_sides: dict, tick: int) -> str | None:
    """Return 'T' / 'CT' / None for an event tick."""
    for i in range(len(round_start_ticks) - 1, -1, -1):
        if round_start_ticks[i] <= tick:
            return round_sides.get(i)
    return None
