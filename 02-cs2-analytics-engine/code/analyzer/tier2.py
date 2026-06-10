"""Tier 2 heuristic flags — behavioral patterns from event data with per-side breakdown."""
from dataclasses import dataclass, field
from pathlib import Path

from demoparser2 import DemoParser

from analyzer.sides import CT_SIDE, T_SIDE, get_round_sides, side_for_tick

# Snipers — HS% isn't a meaningful aim signal (1-shot bodies)
SNIPER_WEAPONS = {"awp", "ssg08", "scar20", "g3sg1"}


def _empty_side_dict() -> dict:
    return {T_SIDE: 0, CT_SIDE: 0}


def _empty_side_weapon_dict() -> dict:
    return {T_SIDE: {}, CT_SIDE: {}}


@dataclass
class Tier2Flags:
    demos_analyzed: int = 0
    rounds_total: int = 0
    rounds_survived: int = 0
    first_deaths: int = 0
    total_deaths: int = 0
    weapon_hs_kills: dict = field(default_factory=dict)
    weapon_total_kills: dict = field(default_factory=dict)
    # per-side breakdowns
    weapon_hs_kills_by_side: dict = field(default_factory=_empty_side_weapon_dict)
    weapon_total_kills_by_side: dict = field(default_factory=_empty_side_weapon_dict)

    @property
    def survival_rate(self) -> float:
        return self.rounds_survived / max(self.rounds_total, 1) * 100

    @property
    def first_death_rate(self) -> float:
        return self.first_deaths / max(self.total_deaths, 1) * 100

    def weapon_hs_pct(self, weapon: str) -> float:
        total = self.weapon_total_kills.get(weapon, 0)
        hs = self.weapon_hs_kills.get(weapon, 0)
        return hs / max(total, 1) * 100

    def weapon_hs_pct_side(self, weapon: str, side: str) -> float:
        total = self.weapon_total_kills_by_side.get(side, {}).get(weapon, 0)
        hs = self.weapon_hs_kills_by_side.get(side, {}).get(weapon, 0)
        return hs / max(total, 1) * 100


def analyze_demo_tier2(demo_path: Path, target_steamid: str) -> Tier2Flags:
    parser = DemoParser(str(demo_path))
    kills_df = parser.parse_event("player_death")
    round_starts_df = parser.parse_event("round_start")
    round_ends_df = parser.parse_event("round_end")

    target_int = int(target_steamid)
    round_sides, round_start_ticks = get_round_sides(parser, target_int)

    me_kills = kills_df[kills_df["attacker_steamid"] == target_steamid]
    me_deaths = kills_df[kills_df["user_steamid"] == target_steamid]

    flags = Tier2Flags()
    flags.demos_analyzed = 1
    flags.rounds_total = len(round_ends_df) if round_ends_df is not None else 0
    flags.total_deaths = len(me_deaths)
    flags.rounds_survived = max(0, flags.rounds_total - flags.total_deaths)

    # First-death detection
    if round_start_ticks and not me_deaths.empty:
        first_count = 0
        for _, death_row in me_deaths.iterrows():
            death_tick = death_row["tick"]
            round_start = max(
                (t for t in round_start_ticks if t <= death_tick), default=0
            )
            round_deaths = kills_df[
                (kills_df["tick"] >= round_start) & (kills_df["tick"] <= death_tick)
            ]
            if round_deaths["tick"].min() == death_tick:
                first_count += 1
        flags.first_deaths = first_count

    # Per-weapon HS% (overall + per-side)
    for _, row in me_kills.iterrows():
        weapon = row["weapon"]
        is_hs = bool(row["headshot"])
        flags.weapon_total_kills[weapon] = flags.weapon_total_kills.get(weapon, 0) + 1
        if is_hs:
            flags.weapon_hs_kills[weapon] = flags.weapon_hs_kills.get(weapon, 0) + 1

        side = side_for_tick(round_start_ticks, round_sides, row["tick"])
        if side in flags.weapon_total_kills_by_side:
            side_totals = flags.weapon_total_kills_by_side[side]
            side_totals[weapon] = side_totals.get(weapon, 0) + 1
            if is_hs:
                side_hs = flags.weapon_hs_kills_by_side[side]
                side_hs[weapon] = side_hs.get(weapon, 0) + 1

    return flags


def aggregate_flags(flags_list: list[Tier2Flags]) -> Tier2Flags:
    agg = Tier2Flags()
    for f in flags_list:
        agg.demos_analyzed += f.demos_analyzed
        agg.rounds_total += f.rounds_total
        agg.rounds_survived += f.rounds_survived
        agg.first_deaths += f.first_deaths
        agg.total_deaths += f.total_deaths
        for weapon, count in f.weapon_total_kills.items():
            agg.weapon_total_kills[weapon] = agg.weapon_total_kills.get(weapon, 0) + count
        for weapon, count in f.weapon_hs_kills.items():
            agg.weapon_hs_kills[weapon] = agg.weapon_hs_kills.get(weapon, 0) + count
        for side in (T_SIDE, CT_SIDE):
            for weapon, count in f.weapon_total_kills_by_side.get(side, {}).items():
                agg.weapon_total_kills_by_side[side][weapon] = (
                    agg.weapon_total_kills_by_side[side].get(weapon, 0) + count
                )
            for weapon, count in f.weapon_hs_kills_by_side.get(side, {}).items():
                agg.weapon_hs_kills_by_side[side][weapon] = (
                    agg.weapon_hs_kills_by_side[side].get(weapon, 0) + count
                )
    return agg
