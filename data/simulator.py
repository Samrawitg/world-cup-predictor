import sqlite3
import os
import random
import json
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path  = os.path.join(base_dir, "world_cup.db")

# ─────────────────────────────────────────
#  LOAD CURRENT STANDINGS FROM DATABASE
# ─────────────────────────────────────────
def load_standings():
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("""
            SELECT group_name, position, team, played,
                   won, drawn, lost, goals_for, goals_against,
                   goal_diff, points
            FROM   live_standings
            ORDER  BY group_name, position
        """).fetchall()
    except:
        rows = []
    conn.close()

    groups = defaultdict(list)
    for r in rows:
        groups[r[0]].append({
            "team":           r[2],
            "played":         r[3],
            "won":            r[4],
            "drawn":          r[5],
            "lost":           r[6],
            "goals_for":      r[7],
            "goals_against":  r[8],
            "goal_diff":      r[9],
            "points":         r[10],
        })
    return groups

# ─────────────────────────────────────────
#  LOAD MATCHES FROM DATABASE
# ─────────────────────────────────────────
def load_matches():
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("""
            SELECT home_team, away_team, home_score,
                   away_score, status, matchday
            FROM   live_matches
            WHERE  stage = 'GROUP_STAGE'
        """).fetchall()
    except:
        rows = []
    conn.close()
    return rows

# ─────────────────────────────────────────
#  SIMULATE A SINGLE MATCH
# ─────────────────────────────────────────
def simulate_match(home_team, away_team, team_strengths):
    home_str = team_strengths.get(home_team, 1.0)
    away_str = team_strengths.get(away_team, 1.0)

    # Home advantage factor
    home_str *= 1.1

    total = home_str + away_str
    r     = random.random() * total

    if r < home_str * 0.45:
        return "home"
    elif r < home_str * 0.45 + away_str * 0.45:
        return "away"
    else:
        return "draw"

# ─────────────────────────────────────────
#  TEAM STRENGTH BASED ON FIFA RANK + WC WINS
# ─────────────────────────────────────────
team_strengths = {
    "Argentina": 3.5,   "France": 3.3,      "Brazil": 3.2,
    "England": 2.8,     "Spain": 2.8,        "Portugal": 2.7,
    "Netherlands": 2.6, "Germany": 2.6,      "Belgium": 2.4,
    "Croatia": 2.3,     "Italy": 2.3,        "Denmark": 2.2,
    "Uruguay": 2.1,     "Colombia": 2.0,     "Mexico": 1.9,
    "United States": 1.8, "Morocco": 1.8,    "Senegal": 1.7,
    "Japan": 1.7,       "Korea Republic": 1.6, "Switzerland": 1.6,
    "Poland": 1.5,      "Serbia": 1.5,       "Austria": 1.5,
    "Ecuador": 1.4,     "Canada": 1.4,       "Turkey": 1.4,
    "Australia": 1.3,   "Iran": 1.3,         "Nigeria": 1.3,
    "Egypt": 1.2,       "Saudi Arabia": 1.2, "Costa Rica": 1.2,
    "Paraguay": 1.1,    "Chile": 1.1,        "Venezuela": 1.0,
    "Bolivia": 0.9,     "Peru": 1.0,         "Jamaica": 0.9,
    "Panama": 0.9,      "Honduras": 0.9,     "Uzbekistan": 1.0,
    "Hungary": 1.2,     "Romania": 1.1,      "Albania": 0.9,
    "Slovakia": 1.0,    "Greece": 1.0,       "Scotland": 1.1,
    "Czech Republic": 1.1,
}

# ─────────────────────────────────────────
#  SIMULATE A FULL GROUP
# ─────────────────────────────────────────
def simulate_group(group_teams, played_matches):
    # Start with current points
    standings = {}
    for t in group_teams:
        standings[t["team"]] = {
            "points":    t["points"],
            "goal_diff": t["goal_diff"],
            "goals_for": t["goals_for"],
        }

    # Find remaining matches in this group
    played_pairs = set()
    for m in played_matches:
        if m[4] == "FINISHED":
            played_pairs.add((m[0], m[1]))

    teams = [t["team"] for t in group_teams]

    # Simulate remaining matches
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            home = teams[i]
            away = teams[j]
            if (home, away) not in played_pairs and (away, home) not in played_pairs:
                result = simulate_match(home, away, team_strengths)
                if result == "home":
                    standings[home]["points"]    += 3
                    standings[home]["goal_diff"] += 1
                    standings[away]["goal_diff"] -= 1
                elif result == "away":
                    standings[away]["points"]    += 3
                    standings[home]["goal_diff"] -= 1
                    standings[away]["goal_diff"] += 1
                else:
                    standings[home]["points"] += 1
                    standings[away]["points"] += 1

    # Sort by points then goal diff
    sorted_teams = sorted(
        standings.items(),
        key=lambda x: (x[1]["points"], x[1]["goal_diff"], x[1]["goals_for"]),
        reverse=True
    )
    return [t[0] for t in sorted_teams]

# ─────────────────────────────────────────
#  RUN MONTE CARLO SIMULATION
# ─────────────────────────────────────────
def run_simulation(n=10000):
    groups        = load_standings()
    all_matches   = load_matches()
    advance_count = defaultdict(int)
    win_group     = defaultdict(int)

    print(f"🎲 Running {n:,} simulations...\n")

    for _ in range(n):
        for group_name, group_teams in groups.items():
            if not group_teams:
                continue

            group_matches = [
                m for m in all_matches
                if m[0] in [t["team"] for t in group_teams]
                or m[1] in [t["team"] for t in group_teams]
            ]

            result = simulate_group(group_teams, group_matches)

            # Top 2 advance (2026 format)
            for i, team in enumerate(result[:2]):
                advance_count[team] += 1
            win_group[result[0]] += 1

    # Convert to percentages
    results = []
    for group_name, group_teams in groups.items():
        for t in group_teams:
            team = t["team"]
            results.append({
                "group":            group_name.replace("GROUP_", "Group "),
                "team":             team,
                "points":           t["points"],
                "played":           t["played"],
                "goal_diff":        t["goal_diff"],
                "advance_pct":      round(advance_count[team] / n * 100, 1),
                "win_group_pct":    round(win_group[team]    / n * 100, 1),
            })

    return sorted(results, key=lambda x: (x["group"], -x["advance_pct"]))

# ─────────────────────────────────────────
#  SAVE + PRINT RESULTS
# ─────────────────────────────────────────
def save_simulation(results):
    conn = sqlite3.connect(db_path)
    conn.execute("DROP TABLE IF EXISTS simulation_results")
    conn.execute("""
        CREATE TABLE simulation_results (
            group_name    TEXT,
            team          TEXT,
            points        INTEGER,
            played        INTEGER,
            goal_diff     INTEGER,
            advance_pct   REAL,
            win_group_pct REAL
        )
    """)
    for r in results:
        conn.execute("""
            INSERT INTO simulation_results VALUES (?,?,?,?,?,?,?)
        """, (r["group"], r["team"], r["points"], r["played"],
              r["goal_diff"], r["advance_pct"], r["win_group_pct"]))
    conn.commit()
    conn.close()
    print("✅ Simulation results saved to database\n")

if __name__ == "__main__":
    results = run_simulation(10000)
    save_simulation(results)

    current_group = ""
    for r in results:
        if r["group"] != current_group:
            current_group = r["group"]
            print(f"\n── {current_group} ──")
            print(f"  {'Team':<25} {'Pts':>4}  {'Advance':>8}  {'Win Group':>10}")
            print(f"  {'─'*25} {'─'*4}  {'─'*8}  {'─'*10}")
        bar = "█" * int(r["advance_pct"] / 5)
        print(f"  {r['team']:<25} {r['points']:>4}  {r['advance_pct']:>7.1f}%  {r['win_group_pct']:>9.1f}%  {bar}")

    print("\n✅ Day 9 complete!")