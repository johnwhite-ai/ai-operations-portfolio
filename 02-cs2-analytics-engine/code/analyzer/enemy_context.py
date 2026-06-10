"""Enemy-context heuristics — your behavior conditioned on enemy state.

demoparser2 doesn't expose velocity directly via parse_ticks, so killer speed
is computed from position deltas across a small tick window.
"""
import math
from dataclasses import dataclass, field
from pathlib import Path

from demoparser2 import DemoParser

TICKRATE = 64
ENGAGEMENT_LOOKBACK_TICKS = 5 * TICKRATE  # 5 seconds
VELOCITY_SAMPLE_TICKS = 16  # 0.25s window for momentary speed
STATIONARY_VELOCITY_THRESHOLD = 50  # units/sec — below this = anchoring/pre-aimed


@dataclass
class EnemyContextFlags:
    demos_analyzed: int = 0
    my_kills: int = 0
    my_deaths: int = 0
    trade_cleanup_kills: int = 0
    pre_aimed_deaths: int = 0
    killer_speeds: list = field(default_factory=list)

    @property
    def trade_cleanup_rate(self) -> float:
        return self.trade_cleanup_kills / max(self.my_kills, 1) * 100

    @property
    def pre_aimed_death_rate(self) -> float:
        return self.pre_aimed_deaths / max(len(self.killer_speeds), 1) * 100

    @property
    def mean_killer_speed(self) -> float:
        return sum(self.killer_speeds) / max(len(self.killer_speeds), 1)

    @property
    def median_killer_speed(self) -> float:
        if not self.killer_speeds:
            return 0.0
        s = sorted(self.killer_speeds)
        n = len(s)
        return s[n // 2] if n % 2 == 1 else (s[n // 2 - 1] + s[n // 2]) / 2


def analyze_demo_enemy_context(demo_path: Path, target_steamid: str) -> EnemyContextFlags:
    parser = DemoParser(str(demo_path))
    kills_df = parser.parse_event("player_death")

    me_kills = kills_df[kills_df["attacker_steamid"] == target_steamid]
    me_deaths = kills_df[kills_df["user_steamid"] == target_steamid]

    flags = EnemyContextFlags()
    flags.demos_analyzed = 1
    flags.my_kills = len(me_kills)
    flags.my_deaths = len(me_deaths)

    # 1. Trade-cleanup — was the killed enemy already in an event within 5s prior?
    for _, kill in me_kills.iterrows():
        kill_tick = kill["tick"]
        killed_enemy = kill["user_steamid"]
        window_start = kill_tick - ENGAGEMENT_LOOKBACK_TICKS
        prior = kills_df[
            (kills_df["tick"] >= window_start)
            & (kills_df["tick"] < kill_tick)
            & (
                (kills_df["attacker_steamid"] == killed_enemy)
                | (kills_df["user_steamid"] == killed_enemy)
            )
        ]
        if not prior.empty:
            flags.trade_cleanup_kills += 1

    # 2. Killer speed — sample positions at death_tick and death_tick - 16
    death_pairs = []  # (death_tick, killer_sid_int)
    for _, death in me_deaths.iterrows():
        try:
            killer_sid = int(death["attacker_steamid"])
            death_pairs.append((int(death["tick"]), killer_sid))
        except (ValueError, TypeError):
            pass  # No killer (world / suicide)

    if death_pairs:
        all_ticks = set()
        for death_tick, _ in death_pairs:
            all_ticks.add(death_tick)
            if death_tick - VELOCITY_SAMPLE_TICKS > 0:
                all_ticks.add(death_tick - VELOCITY_SAMPLE_TICKS)
        ticks_sorted = sorted(all_ticks)
        pos_df = parser.parse_ticks(["X", "Y", "Z"], ticks=ticks_sorted)

        pos_by_key = {}
        for _, row in pos_df.iterrows():
            key = (int(row["tick"]), int(row["steamid"]))
            pos_by_key[key] = (
                float(row["X"]),
                float(row["Y"]),
                float(row["Z"]),
            )

        for death_tick, killer_sid in death_pairs:
            pre_tick = death_tick - VELOCITY_SAMPLE_TICKS
            if pre_tick <= 0:
                continue
            pos_now = pos_by_key.get((death_tick, killer_sid))
            pos_pre = pos_by_key.get((pre_tick, killer_sid))
            if pos_now is None or pos_pre is None:
                continue
            dx = pos_now[0] - pos_pre[0]
            dy = pos_now[1] - pos_pre[1]
            dz = pos_now[2] - pos_pre[2]
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
            # Velocity in units/sec
            speed = distance * (TICKRATE / VELOCITY_SAMPLE_TICKS)
            # Filter clearly-invalid huge jumps (e.g., respawns)
            if speed > 5000:
                continue
            flags.killer_speeds.append(speed)
            if speed < STATIONARY_VELOCITY_THRESHOLD:
                flags.pre_aimed_deaths += 1

    return flags


def aggregate_enemy_flags(flags_list: list[EnemyContextFlags]) -> EnemyContextFlags:
    agg = EnemyContextFlags()
    for f in flags_list:
        agg.demos_analyzed += f.demos_analyzed
        agg.my_kills += f.my_kills
        agg.my_deaths += f.my_deaths
        agg.trade_cleanup_kills += f.trade_cleanup_kills
        agg.pre_aimed_deaths += f.pre_aimed_deaths
        agg.killer_speeds.extend(f.killer_speeds)
    return agg
