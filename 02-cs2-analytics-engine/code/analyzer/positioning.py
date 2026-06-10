"""Position-based team-play heuristics (tick-data driven).

Distance is measured in CS units. ~64 units = player height. Rough mental model:
- <500   = tight support / adjacent
- 500-1500 = same area / coordinated
- >2000  = effectively alone, different room/zone
"""
import math
from dataclasses import dataclass, field
from pathlib import Path

from demoparser2 import DemoParser

from analyzer.sides import get_round_sides
from analyzer.teammates import get_teammates_per_round

CLOSE_SUPPORT_THRESHOLD = 500
LONE_WOLF_THRESHOLD = 2000


@dataclass
class PositionFlags:
    demos_analyzed: int = 0
    engagements_analyzed: int = 0
    distances: list = field(default_factory=list)  # nearest-teammate dist per engagement
    close_support_count: int = 0
    lone_wolf_count: int = 0

    @property
    def median_nearest_teammate_dist(self) -> float:
        if not self.distances:
            return 0.0
        s = sorted(self.distances)
        n = len(s)
        return s[n // 2] if n % 2 == 1 else (s[n // 2 - 1] + s[n // 2]) / 2

    @property
    def mean_nearest_teammate_dist(self) -> float:
        return sum(self.distances) / max(len(self.distances), 1)

    @property
    def close_support_rate(self) -> float:
        return self.close_support_count / max(self.engagements_analyzed, 1) * 100

    @property
    def lone_wolf_rate(self) -> float:
        return self.lone_wolf_count / max(self.engagements_analyzed, 1) * 100


def _euclidean(p1, p2) -> float:
    return math.sqrt(
        (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2
    )


def _round_index_for_tick(round_start_ticks: list, tick: int) -> int:
    for i in range(len(round_start_ticks) - 1, -1, -1):
        if round_start_ticks[i] <= tick:
            return i
    return -1


def analyze_demo_positioning(demo_path: Path, target_steamid: str) -> PositionFlags:
    parser = DemoParser(str(demo_path))
    kills_df = parser.parse_event("player_death")

    target_int = int(target_steamid)
    _, round_start_ticks = get_round_sides(parser, target_int)
    teammates_per_round = get_teammates_per_round(parser, target_int)

    flags = PositionFlags()
    flags.demos_analyzed = 1

    me_kills = kills_df[kills_df["attacker_steamid"] == target_steamid]
    me_deaths = kills_df[kills_df["user_steamid"] == target_steamid]

    engagements = []  # (tick, kind)
    for _, row in me_kills.iterrows():
        engagements.append((int(row["tick"]), "kill"))
    for _, row in me_deaths.iterrows():
        engagements.append((int(row["tick"]), "death"))

    if not engagements:
        return flags

    engagement_ticks = sorted({t for t, _ in engagements})
    positions_df = parser.parse_ticks(["X", "Y", "Z"], ticks=engagement_ticks)

    # Index positions by tick for fast lookup
    pos_by_tick = {}
    for _, row in positions_df.iterrows():
        tick = int(row["tick"])
        sid = int(row["steamid"])
        pos_by_tick.setdefault(tick, {})[sid] = (
            float(row["X"]),
            float(row["Y"]),
            float(row["Z"]),
        )

    for tick, _ in engagements:
        round_idx = _round_index_for_tick(round_start_ticks, tick)
        teammates = teammates_per_round.get(round_idx, [])
        if not teammates:
            continue
        positions_at_tick = pos_by_tick.get(tick, {})
        john_pos = positions_at_tick.get(target_int)
        if john_pos is None:
            continue
        teammate_dists = [
            _euclidean(john_pos, positions_at_tick[tm])
            for tm in teammates
            if tm in positions_at_tick
        ]
        if not teammate_dists:
            continue
        nearest = min(teammate_dists)
        flags.distances.append(nearest)
        flags.engagements_analyzed += 1
        if nearest < CLOSE_SUPPORT_THRESHOLD:
            flags.close_support_count += 1
        elif nearest > LONE_WOLF_THRESHOLD:
            flags.lone_wolf_count += 1

    return flags


def aggregate_position_flags(flags_list: list[PositionFlags]) -> PositionFlags:
    agg = PositionFlags()
    for f in flags_list:
        agg.demos_analyzed += f.demos_analyzed
        agg.engagements_analyzed += f.engagements_analyzed
        agg.distances.extend(f.distances)
        agg.close_support_count += f.close_support_count
        agg.lone_wolf_count += f.lone_wolf_count
    return agg
