"""Run Tier 1 analysis across all available demos.

Usage:
    python -m analyzer.run_tier1
"""
from analyzer.discover import find_demos
from analyzer.identity import JOHN_NAME, JOHN_STEAMID
from analyzer.tier1 import aggregate_metrics, analyze_demo


def main() -> None:
    demos = find_demos()
    print(f"Found {len(demos)} demos.\n")

    metrics_list = []
    for i, demo in enumerate(demos, 1):
        try:
            print(f"[{i}/{len(demos)}] {demo.name[:60]}...")
            m = analyze_demo(demo, JOHN_STEAMID)
            metrics_list.append(m)
        except Exception as e:
            print(f"  FAILED: {type(e).__name__}: {e}")

    if not metrics_list:
        print("No demos parsed successfully.")
        return

    agg = aggregate_metrics(metrics_list)

    print()
    print("=" * 60)
    print(f"Tier 1 Aggregate: {JOHN_NAME}")
    print("=" * 60)
    print(f"  Demos:         {agg.demos_analyzed}")
    print(f"  Rounds:        {agg.rounds_played}")
    print(f"  Kills:         {agg.kills}")
    print(f"  Deaths:        {agg.deaths}")
    print(f"  Assists:       {agg.assists}")
    print(f"  K/D:           {agg.kd_ratio:.2f}")
    print(f"  Headshot %:    {agg.headshot_pct:.1f}%")
    print(f"  Kills/round:   {agg.kills_per_round:.2f}")

    print(f"\n  Top weapons (kills):")
    for w, c in sorted(agg.weapon_kill_counts.items(), key=lambda x: -x[1])[:8]:
        print(f"    {w:18} {c}")

    print(f"\n  Died most to:")
    for w, c in sorted(agg.death_weapon_counts.items(), key=lambda x: -x[1])[:5]:
        print(f"    {w:18} {c}")

    print(f"\n  Maps played:")
    for m, c in sorted(agg.map_counts.items(), key=lambda x: -x[1]):
        print(f"    {m:18} {c}")


if __name__ == "__main__":
    main()
