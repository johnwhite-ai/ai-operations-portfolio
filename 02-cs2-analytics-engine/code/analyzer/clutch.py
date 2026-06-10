"""Clutch performance — when your team dies, can you close?

A clutch attempt = at any point in a round, John was the last alive on his
team facing live enemies. A clutch win = his team won that round.
"""
from dataclasses import dataclass, field
from pathlib import Path

from demoparser2 import DemoParser

from analyzer.sides import CT_SIDE, T_SIDE, get_round_sides
from analyzer.teammates import get_teammates_per_round


def _empty_clutch_size_dict() -> dict:
    return {f"1v{n}": {"attempts": 0, "wins": 0} for n in range(1, 6)}


@dataclass
class ClutchFlags:
    demos_analyzed: int = 0
    clutch_attempts: int = 0
    clutch_wins: int = 0
    by_size: dict = field(default_factory=_empty_clutch_size_dict)

    @property
    def clutch_win_rate(self) -> float:
        return self.clutch_wins / max(self.clutch_attempts, 1) * 100


def analyze_demo_clutch(demo_path: Path, target_steamid: str) -> ClutchFlags:
    parser = DemoParser(str(demo_path))
    kills_df = parser.parse_event("player_death")
    round_starts_df = parser.parse_event("round_start")
    round_ends_df = parser.parse_event("round_end")

    target_int = int(target_steamid)
    round_sides, round_start_ticks = get_round_sides(parser, target_int)
    teammates_per_round = get_teammates_per_round(parser, target_int)

    flags = ClutchFlags()
    flags.demos_analyzed = 1

    if round_ends_df is None or round_ends_df.empty:
        return flags
    if not round_start_ticks:
        return flags

    # Build {round_idx -> end_tick} and {round_idx -> winner_side}
    round_end_info = {}
    for _, row in round_ends_df.iterrows():
        round_num = int(row["round"]) - 1  # 0-based
        round_end_info[round_num] = {
            "end_tick": int(row["tick"]),
            "winner": str(row["winner"]),
        }

    for round_idx, start_tick in enumerate(round_start_ticks):
        end_info = round_end_info.get(round_idx)
        if end_info is None:
            continue
        end_tick = end_info["end_tick"]
        winner = end_info["winner"]
        john_side = round_sides.get(round_idx)
        if john_side is None:
            continue

        teammates = teammates_per_round.get(round_idx, [])
        if not teammates:
            continue
        teammates_str = {str(t) for t in teammates}

        # All kills in this round
        round_events = kills_df[
            (kills_df["tick"] >= start_tick) & (kills_df["tick"] <= end_tick)
        ]

        # Teammate deaths in this round
        teammate_deaths = round_events[
            round_events["user_steamid"].isin(teammates_str)
        ]
        teammate_dead_ids = set(teammate_deaths["user_steamid"].unique())
        # Were all teammates dead at some point this round?
        if len(teammate_dead_ids) < len(teammates):
            continue

        last_teammate_death_tick = int(teammate_deaths["tick"].max())

        # Was John alive at last_teammate_death_tick?
        john_death_in_round = round_events[
            round_events["user_steamid"] == target_steamid
        ]
        if not john_death_in_round.empty:
            john_death_tick = int(john_death_in_round["tick"].min())
            if john_death_tick <= last_teammate_death_tick:
                continue  # John died before/with his team — not a clutch

        # How many enemies were alive at last_teammate_death_tick?
        enemy_deaths_up_to_clutch = round_events[
            (round_events["tick"] <= last_teammate_death_tick)
            & (~round_events["user_steamid"].isin(teammates_str))
            & (round_events["user_steamid"] != target_steamid)
        ]
        enemies_killed = len(enemy_deaths_up_to_clutch["user_steamid"].unique())
        enemies_alive = 5 - enemies_killed
        if enemies_alive <= 0:
            continue  # No clutch — all enemies already dead

        # Did John's team win?
        john_won = winner == john_side
        flags.clutch_attempts += 1
        if john_won:
            flags.clutch_wins += 1

        size_key = f"1v{enemies_alive}"
        if size_key in flags.by_size:
            flags.by_size[size_key]["attempts"] += 1
            if john_won:
                flags.by_size[size_key]["wins"] += 1

    return flags


def aggregate_clutch_flags(flags_list: list[ClutchFlags]) -> ClutchFlags:
    agg = ClutchFlags()
    for f in flags_list:
        agg.demos_analyzed += f.demos_analyzed
        agg.clutch_attempts += f.clutch_attempts
        agg.clutch_wins += f.clutch_wins
        for size, counts in f.by_size.items():
            if size not in agg.by_size:
                agg.by_size[size] = {"attempts": 0, "wins": 0}
            agg.by_size[size]["attempts"] += counts["attempts"]
            agg.by_size[size]["wins"] += counts["wins"]
    return agg
