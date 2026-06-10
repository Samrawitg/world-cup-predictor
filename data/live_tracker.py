import requests
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY  = os.getenv("FOOTBALL_API_KEY")
BASE_URL = "https://api.football-data.org/v4"
HEADERS  = {"X-Auth-Token": API_KEY}

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path  = os.path.join(base_dir, "world_cup.db")

# ─────────────────────────────────────────
#  FETCH LIVE STANDINGS
# ─────────────────────────────────────────
def fetch_standings():
    r = requests.get(f"{BASE_URL}/competitions/WC/standings", headers=HEADERS)
    if r.status_code != 200:
        print(f"❌ Error fetching standings: {r.status_code}")
        return None
    return r.json()

# ─────────────────────────────────────────
#  FETCH LIVE MATCHES
# ─────────────────────────────────────────
def fetch_matches():
    r = requests.get(f"{BASE_URL}/competitions/WC/matches", headers=HEADERS)
    if r.status_code != 200:
        print(f"❌ Error fetching matches: {r.status_code}")
        return None
    return r.json()

# ─────────────────────────────────────────
#  SAVE STANDINGS TO DATABASE
# ─────────────────────────────────────────
def save_standings(data):
    if not data or "standings" not in data:
        print("❌ No standings data available yet")
        return

    conn = sqlite3.connect(db_path)
    conn.execute("DROP TABLE IF EXISTS live_standings")
    conn.execute("""
        CREATE TABLE live_standings (
            group_name   TEXT,
            position     INTEGER,
            team         TEXT,
            played       INTEGER,
            won          INTEGER,
            drawn        INTEGER,
            lost         INTEGER,
            goals_for    INTEGER,
            goals_against INTEGER,
            goal_diff    INTEGER,
            points       INTEGER
        )
    """)

    for group in data["standings"]:
        group_name = group["group"]
        for entry in group["table"]:
            conn.execute("""
                INSERT INTO live_standings VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (
                group_name,
                entry["position"],
                entry["team"]["name"],
                entry["playedGames"],
                entry["won"],
                entry["draw"],
                entry["lost"],
                entry["goalsFor"],
                entry["goalsAgainst"],
                entry["goalDifference"],
                entry["points"],
            ))

    conn.commit()
    conn.close()
    print(f"✅ Standings saved to database")

# ─────────────────────────────────────────
#  SAVE MATCHES TO DATABASE
# ─────────────────────────────────────────
def save_matches(data):
    if not data or "matches" not in data:
        print("❌ No match data available yet")
        return

    conn = sqlite3.connect(db_path)
    conn.execute("DROP TABLE IF EXISTS live_matches")
    conn.execute("""
        CREATE TABLE live_matches (
            match_id     INTEGER,
            matchday     INTEGER,
            status       TEXT,
            utc_date     TEXT,
            home_team    TEXT,
            away_team    TEXT,
            home_score   INTEGER,
            away_score   INTEGER,
            stage        TEXT
        )
    """)

    for m in data["matches"]:
        home_score = m["score"]["fullTime"]["home"]
        away_score = m["score"]["fullTime"]["away"]
        conn.execute("""
            INSERT INTO live_matches VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            m["id"],
            m.get("matchday", 0),
            m["status"],
            m["utcDate"],
            m["homeTeam"]["name"],
            m["awayTeam"]["name"],
            home_score,
            away_score,
            m["stage"],
        ))

    conn.commit()
    conn.close()
    print(f"✅ {len(data['matches'])} matches saved to database")

# ─────────────────────────────────────────
#  RUN
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("📡 Fetching live World Cup data...\n")

    standings_data = fetch_standings()
    save_standings(standings_data)

    matches_data = fetch_matches()
    save_matches(matches_data)

    print("\n✅ Live data fetch complete!")