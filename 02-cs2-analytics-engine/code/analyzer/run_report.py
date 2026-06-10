"""Generate the weekly report from all available demos.

Usage:
    python -m analyzer.run_report
"""
from datetime import datetime
from pathlib import Path

from analyzer.clutch import aggregate_clutch_flags, analyze_demo_clutch
from analyzer.discover import find_demos
from analyzer.enemy_context import aggregate_enemy_flags, analyze_demo_enemy_context
from analyzer.identity import JOHN_NAME, JOHN_STEAMID
from analyzer.positioning import aggregate_position_flags, analyze_demo_positioning
from analyzer.report import generate_report
from analyzer.team import aggregate_team_flags, analyze_demo_team
from analyzer.tier1 import aggregate_metrics, analyze_demo
from analyzer.tier2 import aggregate_flags, analyze_demo_tier2


def main() -> None:
    demos = find_demos()
    print(f"Found {len(demos)} demos.\n")

    t1_list = []
    t2_list = []
    team_list = []
    pos_list = []
    enemy_list = []
    clutch_list = []
    for i, demo in enumerate(demos, 1):
        try:
            print(f"[{i}/{len(demos)}] {demo.name[:60]}...")
            t1_list.append(analyze_demo(demo, JOHN_STEAMID))
            t2_list.append(analyze_demo_tier2(demo, JOHN_STEAMID))
            team_list.append(analyze_demo_team(demo, JOHN_STEAMID))
            pos_list.append(analyze_demo_positioning(demo, JOHN_STEAMID))
            enemy_list.append(analyze_demo_enemy_context(demo, JOHN_STEAMID))
            clutch_list.append(analyze_demo_clutch(demo, JOHN_STEAMID))
        except Exception as e:
            print(f"  FAILED: {type(e).__name__}: {e}")

    if not t1_list:
        print("No demos parsed successfully.")
        return

    t1_agg = aggregate_metrics(t1_list)
    t2_agg = aggregate_flags(t2_list)
    team_agg = aggregate_team_flags(team_list)
    pos_agg = aggregate_position_flags(pos_list)
    enemy_agg = aggregate_enemy_flags(enemy_list)
    clutch_agg = aggregate_clutch_flags(clutch_list)

    today = datetime.now().strftime("%Y-%m-%d")
    reports_dir = Path(__file__).resolve().parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    report_path = reports_dir / f"weekly-report-{today}.md"

    generate_report(
        t1_agg,
        t2_agg,
        team_agg,
        pos_agg,
        enemy_agg,
        clutch_agg,
        JOHN_NAME,
        report_path,
    )
    print(f"\nReport saved: {report_path}")


if __name__ == "__main__":
    main()
