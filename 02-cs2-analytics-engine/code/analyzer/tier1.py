"""Tier 1 mechanical metrics — per-player aggregates with per-side breakdown."""
from dataclasses import dataclass, field
from pathlib import Path

from demoparser2 import DemoParser

from analyzer.sides import CT_SIDE, T_SIDE, get_round_sides, side_for_tick


def _empty_side_dict() -> dict:
    return {T_SIDE: 0, CT_SIDE: 0}


@dataclass
class Tier1Metrics:
    demos_analyzed: int = 0
    rounds_played: int = 0
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    headshot_kills: int = 0
    weapon_kill_counts: dict = field(default_factory=dict)
    death_weapon_counts: dict = field(default_factory=dict)
    map_counts: dict = field(default_factory=dict)
    # per-side breakdown
    kills_by_side: dict = field(default_factory=_empty_side_dict)
    deaths_by_side: dict = field(default_factory=_empty_side_dict)
    rounds_by_side: dict = field(default_factory=_empty_side_dict)
    headshot_kills_by_side: dict = field(default_factory=_empty_side_dict)
    # per-map breakdown
    kills_by_map: dict = field(default_factory=dict)
    deaths_by_map: dict = field(default_factory=dict)
    hs_kills_by_map: dict = field(default_factory=dict)
    rounds_by_map: dict = field(default_factory=dict)

    @property
    def kd_ratio(self) -> float:
        return self.kills / max(self.deaths, 1)

    @property
    def headshot_pct(self) -> float:
        return self.headshot_kills / max(self.kills, 1) * 100

    @property
    def kills_per_round(self) -> float:
        return self.kills / max(self.rounds_played, 1)

    def kd_by_side(self, side: str) -> float:
        return self.kills_by_side.get(side, 0) / max(self.deaths_by_side.get(side, 0), 1)

    def hs_pct_by_side(self, side: str) -> float:
        return (
            self.headshot_kills_by_side.get(side, 0)
            / max(self.kills_by_side.get(side, 0), 1)
            * 100
        )

    def kd_by_map(self, map_name: str) -> float:
        return self.kills_by_map.get(map_name, 0) / max(self.deaths_by_map.get(map_name, 0), 1)

    def hs_pct_by_map(self, map_name: str) -> float:
        return (
            self.hs_kills_by_map.get(map_name, 0)
            / max(self.kills_by_map.get(map_name, 0), 1)
            * 100
        )


def analyze_demo(demo_path: Path, target_steamid: str) -> Tier1Metrics:
    parser = DemoParser(str(demo_path))
    header = parser.parse_header()
    kills_df = parser.parse_event("player_death")
    round_ends = parser.parse_event("round_end")

    target_int = int(target_steamid)
    round_sides, round_start_ticks = get_round_sides(parser, target_int)

    me_kills = kills_df[kills_df["attacker_steamid"] == target_steamid]
    me_deaths = kills_df[kills_df["user_steamid"] == target_steamid]

    if "assister_steamid" in kills_df.columns:
        me_assists = kills_df[kills_df["assister_steamid"] == target_steamid]
        assist_count = len(me_assists)
    else:
        assist_count = 0

    m = Tier1Metrics()
    m.demos_analyzed = 1
    m.rounds_played = len(round_ends) if round_ends is not None else 0
    m.kills = len(me_kills)
    m.deaths = len(me_deaths)
    m.assists = assist_count
    m.headshot_kills = int(me_kills["headshot"].sum()) if len(me_kills) > 0 else 0
    m.weapon_kill_counts = (
        me_kills["weapon"].value_counts().to_dict() if len(me_kills) > 0 else {}
    )
    m.death_weapon_counts = (
        me_deaths["weapon"].value_counts().to_dict() if len(me_deaths) > 0 else {}
    )
    map_name = header.get("map_name", "unknown")
    m.map_counts[map_name] = 1
    # per-map (one demo has one map)
    m.kills_by_map[map_name] = m.kills
    m.deaths_by_map[map_name] = m.deaths
    m.hs_kills_by_map[map_name] = m.headshot_kills
    m.rounds_by_map[map_name] = m.rounds_played

    # per-side breakdown
    for side in round_sides.values():
        if side in m.rounds_by_side:
            m.rounds_by_side[side] += 1

    for _, row in me_kills.iterrows():
        side = side_for_tick(round_start_ticks, round_sides, row["tick"])
        if side in m.kills_by_side:
            m.kills_by_side[side] += 1
            if row["headshot"]:
                m.headshot_kills_by_side[side] += 1

    for _, row in me_deaths.iterrows():
        side = side_for_tick(round_start_ticks, round_sides, row["tick"])
        if side in m.deaths_by_side:
            m.deaths_by_side[side] += 1

    return m


def aggregate_metrics(metrics_list: list[Tier1Metrics]) -> Tier1Metrics:
    agg = Tier1Metrics()
    for m in metrics_list:
        agg.demos_analyzed += m.demos_analyzed
        agg.rounds_played += m.rounds_played
        agg.kills += m.kills
        agg.deaths += m.deaths
        agg.assists += m.assists
        agg.headshot_kills += m.headshot_kills
        for w, c in m.weapon_kill_counts.items():
            agg.weapon_kill_counts[w] = agg.weapon_kill_counts.get(w, 0) + c
        for w, c in m.death_weapon_counts.items():
            agg.death_weapon_counts[w] = agg.death_weapon_counts.get(w, 0) + c
        for map_name, count in m.map_counts.items():
            agg.map_counts[map_name] = agg.map_counts.get(map_name, 0) + count
        for side in (T_SIDE, CT_SIDE):
            agg.kills_by_side[side] += m.kills_by_side.get(side, 0)
            agg.deaths_by_side[side] += m.deaths_by_side.get(side, 0)
            agg.rounds_by_side[side] += m.rounds_by_side.get(side, 0)
            agg.headshot_kills_by_side[side] += m.headshot_kills_by_side.get(side, 0)
        for map_name, c in m.kills_by_map.items():
            agg.kills_by_map[map_name] = agg.kills_by_map.get(map_name, 0) + c
        for map_name, c in m.deaths_by_map.items():
            agg.deaths_by_map[map_name] = agg.deaths_by_map.get(map_name, 0) + c
        for map_name, c in m.hs_kills_by_map.items():
            agg.hs_kills_by_map[map_name] = agg.hs_kills_by_map.get(map_name, 0) + c
        for map_name, c in m.rounds_by_map.items():
            agg.rounds_by_map[map_name] = agg.rounds_by_map.get(map_name, 0) + c
    return agg
