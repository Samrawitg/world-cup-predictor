from flask import Flask, render_template, jsonify
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# ─────────────────────────────────────────
#  DATABASE HELPER
# ─────────────────────────────────────────
def get_db():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path  = os.path.join(base_dir, "data", "world_cup.db")
    conn     = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# ─────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predictions")
def predictions():
    return render_template("predictions.html")

@app.route("/history")
def history():
    return render_template("history.html")

@app.route("/live")
def live():
    return render_template("live.html")

# ─────────────────────────────────────────
#  PREDICTIONS API
# ─────────────────────────────────────────
@app.route("/api/predictions")
def api_predictions():
    conn = get_db()
    rows = conn.execute("""
        SELECT team, confederation, wc_wins, wc_appearances,
               fifa_rank, host_2026, win_probability
        FROM   predictions_2026
        ORDER  BY win_probability DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ─────────────────────────────────────────
#  HISTORY API
# ─────────────────────────────────────────
@app.route("/api/history")
def api_history():
    conn = get_db()
    rows = conn.execute("""
        SELECT year, host, winner, runner_up, third_place,
               goals_scored, matches, avg_goals_per_match,
               host_won, winner_confederation
        FROM   world_cup_history
        ORDER  BY year ASC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/stats")
def api_stats():
    conn = get_db()
    rows = conn.execute("""
        SELECT winner, COUNT(*) as wins
        FROM   world_cup_history
        GROUP  BY winner
        ORDER  BY wins DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ─────────────────────────────────────────
#  LIVE API
# ─────────────────────────────────────────
@app.route("/api/live/standings")
def api_live_standings():
    conn = get_db()
    try:
        rows = conn.execute("""
            SELECT group_name, position, team, played,
                   won, drawn, lost, goals_for, goals_against,
                   goal_diff, points
            FROM   live_standings
            ORDER  BY group_name, position
        """).fetchall()
        return jsonify([dict(r) for r in rows])
    except:
        return jsonify([])
    finally:
        conn.close()

@app.route("/api/live/matches")
def api_live_matches():
    conn = get_db()
    try:
        rows = conn.execute("""
            SELECT match_id, matchday, status, utc_date,
                   home_team, away_team, home_score, away_score, stage
            FROM   live_matches
            ORDER  BY utc_date ASC
        """).fetchall()
        return jsonify([dict(r) for r in rows])
    except:
        return jsonify([])
    finally:
        conn.close()

@app.route("/api/live/simulation")
def api_simulation():
    conn = get_db()
    try:
        rows = conn.execute("""
            SELECT group_name, team, points, played,
                   goal_diff, advance_pct, win_group_pct
            FROM   simulation_results
            ORDER  BY group_name, advance_pct DESC
        """).fetchall()
        return jsonify([dict(r) for r in rows])
    except:
        return jsonify([])
    finally:
        conn.close()

@app.route("/api/live/refresh")
def api_live_refresh():
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "data"))
    from live_tracker import fetch_standings, fetch_matches, save_standings, save_matches
    save_standings(fetch_standings())
    save_matches(fetch_matches())
    return jsonify({"status": "refreshed"})

@app.route("/api/live/simulate")
def api_run_simulation():
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "data"))
    from simulator import run_simulation, save_simulation
    results = run_simulation(10000)
    save_simulation(results)
    return jsonify({"status": "done", "teams": len(results)})

# ─────────────────────────────────────────
#  START SCHEDULER + RUN
# ─────────────────────────────────────────
if __name__ == "__main__":
    from scheduler import start_scheduler, refresh_all

    # Do one immediate refresh on startup
    print("🔄 Running initial data refresh...")
    refresh_all()

    # Then refresh every 5 minutes in background
    start_scheduler(interval_minutes=5)

    app.run(debug=False)
