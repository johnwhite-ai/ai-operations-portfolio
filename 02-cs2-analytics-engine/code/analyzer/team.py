"""Team-play heuristics from event data — trade-window, solo-death, isolation proxies.

These are event-only (no tick/position data). Position-based team metrics
(real distance from teammates, util coordination by space) are the next tier.
"""
from dataclasses import dataclass
from pathlib import Path

from demoparser2 import DemoParser

from analyzer.sides import get_round_sides
from analyzer.teammates import get_teammates_per_round

TICKRATE = 64
TRADE_WINDOW_TICKS = 5 * TICKRATE  # 5 seconds
SOLO_WINDOW_TICKS = 10 * TICKRATE  # 10 seconds


@dataclass
class TeamFlags:
    demos_analyzed: int = 0
    my_kills: int = 0
    my_deaths: int = 0
    trade_kills: int = 0  # my kill within 5s after a teammate's death (cleaning up)
    traded_deaths: int = 0  # my death where a teammate avenged me within 5s
    solo_deaths: int = 0  # my death with NO teammate event within 10s (isolated)

    @property
    def trade_kill_rate(self) -> float:
        return self.trade_kills / max(self.my_kills, 1) * 100

    @property
    def traded_death_rate(self) -> float:
        """% of your deaths where a teammate killed your killer within 5s."""
        return self.traded_deaths / max(self.my_deaths, 1) * 100

    @property
    def solo_death_rate(self) -> float:
        """% of your deaths with no teammate kill/death within 10s — isolation proxy."""
        return self.solo_deaths / max(self.my_deaths, 1) * 100


def _round_index_for_tick(round_start_ticks: list, tick: int) -> int:
    for i in range(len(round_start_ticks) - 1, -1, -1):
        if round_start_ticks[i] <= tick:
            return i
    return -1


def analyze_demo_team(demo_path: Path, target_steamid: str) -> TeamFlags:
    parser = DemoParser(str(demo_path))
    kills_df = parser.parse_event("player_death")

    target_int = int(target_steamid)
    _, round_start_ticks = get_round_sides(parser, target_int)
    teammates_per_round = get_teammates_per_round(parser, target_int)

    flags = TeamFlags()
    flags.demos_analyzed = 1

    # Normalize steamid columns to int for comparison
    kills_df = kills_df.copy()
    kills_df["_attacker_int"] = kills_df["attacker_steamid"].astype("Int64", errors="ignore")
    kills_df["_user_int"] = kills_df["user_steamid"].astype("Int64", errors="ignore")

    me_kills = kills_df[kills_df["attacker_steamid"] == target_steamid]
    me_deaths = kills_df[kills_df["user_steamid"] == target_steamid]

    flags.my_kills = len(me_kills)
    flags.my_deaths = len(me_deaths)

    # Trade-kill rate — for each of John's kills, check if a teammate died
    # within the 5s preceding it
    for _, kill in me_kills.iterrows():
        kill_tick = kill["tick"]
        round_idx = _round_index_for_tick(round_start_ticks, kill_tick)
        teammates = teammates_per_round.get(round_idx, [])
        if not teammates:
            continue
        teammates_str = {str(t) for t in teammates}
        window_start = kill_tick - TRADE_WINDOW_TICKS
        teammate_deaths_in_window = kills_df[
            (kills_df["tick"] >= window_start)
            & (kills_df["tick"] < kill_tick)
            & (kills_df["user_steamid"].isin(teammates_str))
        ]
        if not teammate_deaths_in_window.empty:
            flags.trade_kills += 1

    # Traded-death rate — for each of John's deaths, check if a teammate
    # killed John's killer within 5s after
    for _, death in me_deaths.iterrows():
        death_tick = death["tick"]
        killer = death["attacker_steamid"]
        round_idx = _round_index_for_tick(round_start_ticks, death_tick)
        teammates = teammates_per_round.get(round_idx, [])
        if not teammates:
            continue
        teammates_str = {str(t) for t in teammates}
        window_end = death_tick + TRADE_WINDOW_TICKS
        avenger_kills = kills_df[
            (kills_df["tick"] > death_tick)
            & (kills_df["tick"] <= window_end)
            & (kills_df["attacker_steamid"].isin(teammates_str))
            & (kills_df["user_steamid"] == killer)
        ]
        if not avenger_kills.empty:
            flags.traded_deaths += 1

        # Solo-death check — any teammate kill or death within 10s window?
        solo_window_start = death_tick - SOLO_WINDOW_TICKS
        solo_window_end = death_tick + SOLO_WINDOW_TICKS
        teammate_events = kills_df[
            (kills_df["tick"] >= solo_window_start)
            & (kills_df["tick"] <= solo_window_end)
            & (kills_df["tick"] != death_tick)
            & (
                kills_df["attacker_steamid"].isin(teammates_str)
                | kills_df["user_steamid"].isin(teammates_str)
            )
        ]
        if teammate_events.empty:
            flags.solo_deaths += 1

    return flags


def aggregate_team_flags(flags_list: list[TeamFlags]) -> TeamFlags:
    agg = TeamFlags()
    for f in flags_list:
        agg.demos_analyzed += f.demos_analyzed
        agg.my_kills += f.my_kills
        agg.my_deaths += f.my_deaths
        agg.trade_kills += f.trade_kills
        agg.traded_deaths += f.traded_deaths
        agg.solo_deaths += f.solo_deaths
    return agg
