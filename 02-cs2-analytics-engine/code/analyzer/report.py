"""Weekly markdown report generator. Also writes a JSON sidecar for the dashboard."""
import json
from datetime import datetime
from pathlib import Path

from analyzer.clutch import ClutchFlags
from analyzer.enemy_context import STATIONARY_VELOCITY_THRESHOLD, EnemyContextFlags
from analyzer.positioning import (
    CLOSE_SUPPORT_THRESHOLD,
    LONE_WOLF_THRESHOLD,
    PositionFlags,
)
from analyzer.sides import CT_SIDE, T_SIDE
from analyzer.team import TeamFlags
from analyzer.tier1 import Tier1Metrics
from analyzer.tier2 import SNIPER_WEAPONS, Tier2Flags


def _hs_meaningful(weapon: str) -> bool:
    """Snipers 1-shot bodies — HS% isn't a meaningful aim signal."""
    return weapon not in SNIPER_WEAPONS


def generate_report(
    t1: Tier1Metrics,
    t2: Tier2Flags,
    team: TeamFlags,
    pos: PositionFlags,
    enemy: EnemyContextFlags,
    clutch: ClutchFlags,
    player_name: str,
    output_path: Path,
) -> Path:
    today = datetime.now().strftime("%Y-%m-%d")

    lines = [
        f"# Weekly Report — {player_name}",
        "",
        f"**Date:** {today}",
        f"**Demos analyzed:** {t1.demos_analyzed}",
        f"**Rounds:** {t1.rounds_played}",
        "",
        "---",
        "",
        "## Overall — Mechanical",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| K/D ratio | {t1.kd_ratio:.2f} |",
        f"| Headshot % | {t1.headshot_pct:.1f}% |",
        f"| Kills/round | {t1.kills_per_round:.2f} |",
        f"| Total kills | {t1.kills} |",
        f"| Total deaths | {t1.deaths} |",
        f"| Total assists | {t1.assists} |",
        "",
        "## Per-Side Breakdown",
        "",
        "| Side | Rounds | Kills | Deaths | K/D | HS % |",
        "|------|--------|-------|--------|-----|------|",
        f"| **T** | {t1.rounds_by_side[T_SIDE]} | {t1.kills_by_side[T_SIDE]} | {t1.deaths_by_side[T_SIDE]} | {t1.kd_by_side(T_SIDE):.2f} | {t1.hs_pct_by_side(T_SIDE):.1f}% |",
        f"| **CT** | {t1.rounds_by_side[CT_SIDE]} | {t1.kills_by_side[CT_SIDE]} | {t1.deaths_by_side[CT_SIDE]} | {t1.kd_by_side(CT_SIDE):.2f} | {t1.hs_pct_by_side(CT_SIDE):.1f}% |",
        "",
        "### Weapon HS% breakdown — overall (min 3 kills, snipers excluded)",
        "",
        "| Weapon | Kills | HS % |",
        "|--------|-------|------|",
    ]
    for w in sorted(
        t2.weapon_total_kills.keys(), key=lambda x: -t2.weapon_total_kills[x]
    ):
        kills = t2.weapon_total_kills[w]
        if kills < 3 or not _hs_meaningful(w):
            continue
        hs = t2.weapon_hs_pct(w)
        lines.append(f"| {w} | {kills} | {hs:.1f}% |")

    # Per-side weapon breakdown
    lines += [
        "",
        "### Weapon HS% — T side (min 3 kills, snipers excluded)",
        "",
        "| Weapon | Kills | HS % |",
        "|--------|-------|------|",
    ]
    t_weapons = t2.weapon_total_kills_by_side.get(T_SIDE, {})
    for w in sorted(t_weapons.keys(), key=lambda x: -t_weapons[x]):
        if t_weapons[w] < 3 or not _hs_meaningful(w):
            continue
        lines.append(f"| {w} | {t_weapons[w]} | {t2.weapon_hs_pct_side(w, T_SIDE):.1f}% |")

    lines += [
        "",
        "### Weapon HS% — CT side (min 3 kills, snipers excluded)",
        "",
        "| Weapon | Kills | HS % |",
        "|--------|-------|------|",
    ]
    ct_weapons = t2.weapon_total_kills_by_side.get(CT_SIDE, {})
    for w in sorted(ct_weapons.keys(), key=lambda x: -ct_weapons[x]):
        if ct_weapons[w] < 3 or not _hs_meaningful(w):
            continue
        lines.append(f"| {w} | {ct_weapons[w]} | {t2.weapon_hs_pct_side(w, CT_SIDE):.1f}% |")

    lines += [
        "",
        "## Position-Based Team-Play (tick data)",
        "",
        "Distance is in CS units. ~64 units = player height. <500 = tight support, >2000 = effectively alone.",
        "",
        "| Flag | Value | Interpretation |",
        "|------|-------|----------------|",
        f"| Engagements analyzed | {pos.engagements_analyzed} | Kills + deaths with valid teammate positions |",
        f"| Median nearest-teammate dist | {pos.median_nearest_teammate_dist:.0f} | The middle of your engagement distances |",
        f"| Mean nearest-teammate dist | {pos.mean_nearest_teammate_dist:.0f} | Average distance — skewed by outliers |",
        f"| Close-support rate | {pos.close_support_rate:.1f}% | % engagements with a teammate within {CLOSE_SUPPORT_THRESHOLD} units (tight support) |",
        f"| Lone-wolf rate | {pos.lone_wolf_rate:.1f}% | % engagements with nearest teammate >{LONE_WOLF_THRESHOLD} units (effectively alone) |",
        "",
        "## Individual Behavioral Heuristics",
        "",
        "| Flag | Value | Interpretation |",
        "|------|-------|----------------|",
        f"| Survival rate | {t2.survival_rate:.1f}% | % of rounds you ended alive |",
        f"| First-death rate | {t2.first_death_rate:.1f}% | % of your deaths that were the first death in the round (high = over-peeking) |",
        "",
        "## Team-Play Heuristics",
        "",
        "Event-only metrics for now — positional (real distance from teammates, util coordination by space) are the next-tier enrichment.",
        "",
        "| Flag | Value | Interpretation |",
        "|------|-------|----------------|",
        f"| Trade-kill rate | {team.trade_kill_rate:.1f}% | % of your kills that came within 5s after a teammate's death (you cleaning up trades) |",
        f"| Got-traded rate | {team.traded_death_rate:.1f}% | % of your deaths where a teammate killed your killer within 5s (team trades *for* you) |",
        f"| Solo-death rate | {team.solo_death_rate:.1f}% | % of your deaths with NO teammate event within 10s either way (isolation proxy) |",
        "",
        "## Enemy-Context Heuristics",
        "",
        "How you performed conditioned on the enemy's state at engagement.",
        "",
        "| Flag | Value | Interpretation |",
        "|------|-------|----------------|",
        f"| Trade-cleanup rate | {enemy.trade_cleanup_rate:.1f}% | % of your kills against an enemy who was already in an engagement within 5s prior (clean trades vs fresh duels) |",
        f"| Pre-aimed death rate | {enemy.pre_aimed_death_rate:.1f}% | % of deaths to a stationary killer (<{STATIONARY_VELOCITY_THRESHOLD} units/sec). High = you peeked into pre-aimed angles |",
        f"| Mean killer speed | {enemy.mean_killer_speed:.0f} u/s | Average movement of your killers. Low = anchor-style holders. High = duelists pushing you. |",
        f"| Median killer speed | {enemy.median_killer_speed:.0f} u/s | The middle — less skewed by outliers |",
        "",
        "## Clutch Performance",
        "",
        f"You attempted **{clutch.clutch_attempts}** clutches and won **{clutch.clutch_wins}** — a **{clutch.clutch_win_rate:.1f}%** win rate.",
        "",
        "| Scenario | Attempts | Wins | Win Rate |",
        "|----------|----------|------|----------|",
    ]
    for size in ("1v1", "1v2", "1v3", "1v4", "1v5"):
        c = clutch.by_size.get(size, {"attempts": 0, "wins": 0})
        att = c["attempts"]
        wins = c["wins"]
        rate = wins / att * 100 if att else 0.0
        lines.append(f"| {size} | {att} | {wins} | {rate:.1f}% |")
    lines += [
        "",
        "## Drill Recommendations",
        "",
    ]

    recs = []
    if t1.headshot_pct < 40:
        recs.append(
            f"- **Aim priority HIGH** — overall HS% at {t1.headshot_pct:.0f}% (under 40%). Use aim_treeni_fps Warmup preset."
        )
    elif t1.headshot_pct < 50:
        recs.append(
            f"- **Aim refinement** — HS% at {t1.headshot_pct:.0f}% (room to grow toward 55%+). AK Burst preset in aim_treeni_fps."
        )

    # Side imbalance check
    t_kd = t1.kd_by_side(T_SIDE)
    ct_kd = t1.kd_by_side(CT_SIDE)
    if abs(t_kd - ct_kd) > 0.25 and t1.rounds_by_side[T_SIDE] >= 10 and t1.rounds_by_side[CT_SIDE] >= 10:
        weak_side = T_SIDE if t_kd < ct_kd else CT_SIDE
        weak_kd = min(t_kd, ct_kd)
        strong_kd = max(t_kd, ct_kd)
        recs.append(
            f"- **Side imbalance** — {weak_side} K/D {weak_kd:.2f} vs opposite {strong_kd:.2f}. Bias practice toward {weak_side}-side scenarios."
        )

    if t2.first_death_rate > 35:
        recs.append(
            f"- **Over-peek tendency** — {t2.first_death_rate:.0f}% of deaths are first deaths of the round. Practice angle-holding patience and pre-aim discipline."
        )

    if t1.kd_ratio < 1.0:
        recs.append(
            f"- **K/D below 1.0** ({t1.kd_ratio:.2f}) — focus: survive more rounds. Crosshair placement + prefire drills."
        )

    if t2.survival_rate < 30:
        recs.append(
            f"- **Survival rate low** at {t2.survival_rate:.0f}%. Bias gameplan toward survival over fragging."
        )

    # Side-specific weapon weakness (excludes snipers via _hs_meaningful)
    for side in (T_SIDE, CT_SIDE):
        side_weapons = t2.weapon_total_kills_by_side.get(side, {})
        candidates = [
            (w, t2.weapon_hs_pct_side(w, side))
            for w, c in side_weapons.items()
            if c >= 5 and _hs_meaningful(w)
        ]
        if not candidates:
            continue
        weakest = min(candidates, key=lambda x: x[1])
        w, pct = weakest
        if pct < 40:
            recs.append(
                f"- **{side}-side weapon weakness:** `{w}` at {pct:.0f}% HS (worst non-sniper weapon, min 5 kills). Drill in aim_treeni_fps."
            )

    # Team-play recs
    if team.solo_death_rate > 25:
        recs.append(
            f"- **Isolation pattern** — {team.solo_death_rate:.0f}% of your deaths happen with no nearby teammate event. Stay closer to teammates on entries; avoid lone pushes."
        )
    if team.traded_death_rate < 30 and team.my_deaths > 20:
        recs.append(
            f"- **Low got-traded rate** ({team.traded_death_rate:.0f}%) — your team trades for you in less than 30% of deaths. Either your team has trade-discipline gaps, or you're pushing too far ahead of support."
        )
    if team.trade_kill_rate > 30:
        recs.append(
            f"- **Trade-fragging strength** ({team.trade_kill_rate:.0f}%) — you clean up well after teammate deaths. Maintain this; consider playing slower trade roles."
        )

    # Position-based recs
    if pos.lone_wolf_rate > 30 and pos.engagements_analyzed > 30:
        recs.append(
            f"- **Spatial isolation** — {pos.lone_wolf_rate:.0f}% of engagements happen >{LONE_WOLF_THRESHOLD} units from your nearest teammate. You're playing too far from support."
        )
    if pos.close_support_rate < 15 and pos.engagements_analyzed > 30:
        recs.append(
            f"- **Low close-support rate** ({pos.close_support_rate:.0f}%) — only {pos.close_support_rate:.0f}% of engagements have a teammate within {CLOSE_SUPPORT_THRESHOLD} units. Consider tighter team spacing on entries."
        )

    # Per-map weakness — flag worst map with sample size
    map_candidates = [
        (m, t1.kd_by_map(m))
        for m in t1.kills_by_map
        if t1.rounds_by_map.get(m, 0) >= 30  # min ~1 game
    ]
    if map_candidates:
        weakest_map = min(map_candidates, key=lambda x: x[1])
        m, kd = weakest_map
        if kd < 0.85:
            recs.append(
                f"- **Map-specific weakness:** `{m}` K/D {kd:.2f} (worst with sufficient sample). Bias practice time toward this map."
            )

    # Enemy-context recs
    if enemy.pre_aimed_death_rate > 50 and len(enemy.killer_speeds) > 20:
        recs.append(
            f"- **Pre-aimed angle deaths** — {enemy.pre_aimed_death_rate:.0f}% of your deaths come from stationary holders. You're peeking into angles that were already aimed at you. Practice crosshair placement + slower default peeks."
        )
    elif enemy.pre_aimed_death_rate < 30 and len(enemy.killer_speeds) > 20:
        recs.append(
            f"- **Low pre-aimed death rate** ({enemy.pre_aimed_death_rate:.0f}%) — most kills against you are dynamic. Your crosshair placement is solid; the problem is duel mechanics, not info."
        )
    if enemy.trade_cleanup_rate < 20 and enemy.my_kills > 30:
        recs.append(
            f"- **Low trade-cleanup** ({enemy.trade_cleanup_rate:.0f}%) — only {enemy.trade_cleanup_rate:.0f}% of kills are vs already-engaged enemies. You're initiating fresh duels more than supporting trades. Could mean entry role, or could mean over-aggression."
        )
    elif enemy.trade_cleanup_rate > 40 and enemy.my_kills > 30:
        recs.append(
            f"- **Strong trade-cleanup** ({enemy.trade_cleanup_rate:.0f}%) — you frag against already-engaged enemies a lot. Confirms support / trader playstyle."
        )

    # Clutch recs
    if clutch.clutch_attempts >= 5:
        if clutch.clutch_win_rate < 20:
            recs.append(
                f"- **Clutch weakness** — {clutch.clutch_win_rate:.0f}% win rate across {clutch.clutch_attempts} attempts. Practice 1vX scenarios specifically."
            )
        elif clutch.clutch_win_rate > 40:
            recs.append(
                f"- **Strong clutch player** — {clutch.clutch_win_rate:.0f}% win rate across {clutch.clutch_attempts} attempts. Maintain this; consider taking more entry roles since you can close late-round."
            )

    # Per-map aim weakness
    for m in list(t1.kills_by_map.keys()):
        kills = t1.kills_by_map.get(m, 0)
        if kills < 25:
            continue
        hs = t1.hs_pct_by_map(m)
        if hs < t1.headshot_pct - 7:
            recs.append(
                f"- **Map aim weakness:** `{m}` HS% {hs:.0f}% vs your overall {t1.headshot_pct:.0f}% ({t1.headshot_pct - hs:.0f}pt drop). Aim mechanics struggle specifically on this map."
            )

    if not recs:
        recs.append(
            "- No critical flags. Continue current practice. Consider expanding Tier 2 enrichment for deeper signals."
        )

    lines.extend(recs)

    lines += [
        "",
        "---",
        "",
        "## Per-Map Breakdown",
        "",
        "| Map | Games | Rounds | Kills | Deaths | K/D | HS % |",
        "|-----|-------|--------|-------|--------|-----|------|",
    ]
    for m, c in sorted(t1.map_counts.items(), key=lambda x: -x[1]):
        rounds = t1.rounds_by_map.get(m, 0)
        kills = t1.kills_by_map.get(m, 0)
        deaths = t1.deaths_by_map.get(m, 0)
        kd = t1.kd_by_map(m)
        hs = t1.hs_pct_by_map(m)
        lines.append(
            f"| {m} | {c} | {rounds} | {kills} | {deaths} | {kd:.2f} | {hs:.1f}% |"
        )

    lines += [
        "",
        "---",
        "",
        f"_Generated by cs2-training-companion at {today}_",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")

    # JSON sidecar for the dashboard
    json_data = {
        "generated_at": today,
        "player": player_name,
        "demos_analyzed": t1.demos_analyzed,
        "rounds": t1.rounds_played,
        "top_metrics": {
            "kd": round(t1.kd_ratio, 2),
            "hs_pct": round(t1.headshot_pct, 1),
            "t_kd": round(t1.kd_by_side(T_SIDE), 2),
            "ct_kd": round(t1.kd_by_side(CT_SIDE), 2),
            "survival_rate": round(t2.survival_rate, 1),
            "first_death_rate": round(t2.first_death_rate, 1),
            "pre_aimed_death_rate": round(enemy.pre_aimed_death_rate, 1),
            "got_traded_rate": round(team.traded_death_rate, 1),
            "clutch_win_rate": round(clutch.clutch_win_rate, 1),
            "clutch_attempts": clutch.clutch_attempts,
        },
        "recommendations": recs,
    }
    json_path = output_path.with_suffix(".json")
    json_path.write_text(json.dumps(json_data, indent=2), encoding="utf-8")

    return output_path
