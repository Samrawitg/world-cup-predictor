import pandas as pd
import sqlite3
import os

# ─────────────────────────────────────────
#  RAW HISTORICAL DATA  (1930 – 2022)
# ─────────────────────────────────────────
world_cup_records = [
    {"year": 1930, "host": "Uruguay",      "winner": "Uruguay",      "runner_up": "Argentina",    "third_place": "USA",            "fourth_place": "Yugoslavia",  "goals_scored": 70,  "teams": 13, "matches": 18},
    {"year": 1934, "host": "Italy",        "winner": "Italy",        "runner_up": "Czechoslovakia","third_place": "Germany",        "fourth_place": "Austria",     "goals_scored": 70,  "teams": 16, "matches": 17},
    {"year": 1938, "host": "France",       "winner": "Italy",        "runner_up": "Hungary",       "third_place": "Brazil",         "fourth_place": "Sweden",      "goals_scored": 84,  "teams": 15, "matches": 18},
    {"year": 1950, "host": "Brazil",       "winner": "Uruguay",      "runner_up": "Brazil",        "third_place": "Sweden",         "fourth_place": "Spain",       "goals_scored": 88,  "teams": 13, "matches": 22},
    {"year": 1954, "host": "Switzerland",  "winner": "West Germany", "runner_up": "Hungary",       "third_place": "Austria",        "fourth_place": "Uruguay",     "goals_scored": 140, "teams": 16, "matches": 26},
    {"year": 1958, "host": "Sweden",       "winner": "Brazil",       "runner_up": "Sweden",        "third_place": "France",         "fourth_place": "West Germany","goals_scored": 126, "teams": 16, "matches": 35},
    {"year": 1962, "host": "Chile",        "winner": "Brazil",       "runner_up": "Czechoslovakia","third_place": "Chile",          "fourth_place": "Yugoslavia",  "goals_scored": 89,  "teams": 16, "matches": 32},
    {"year": 1966, "host": "England",      "winner": "England",      "runner_up": "West Germany",  "third_place": "Portugal",       "fourth_place": "USSR",        "goals_scored": 89,  "teams": 16, "matches": 32},
    {"year": 1970, "host": "Mexico",       "winner": "Brazil",       "runner_up": "Italy",         "third_place": "West Germany",   "fourth_place": "Uruguay",     "goals_scored": 95,  "teams": 16, "matches": 32},
    {"year": 1974, "host": "West Germany", "winner": "West Germany", "runner_up": "Netherlands",   "third_place": "Poland",         "fourth_place": "Brazil",      "goals_scored": 97,  "teams": 16, "matches": 38},
    {"year": 1978, "host": "Argentina",    "winner": "Argentina",    "runner_up": "Netherlands",   "third_place": "Brazil",         "fourth_place": "Italy",       "goals_scored": 102, "teams": 16, "matches": 38},
    {"year": 1982, "host": "Spain",        "winner": "Italy",        "runner_up": "West Germany",  "third_place": "Poland",         "fourth_place": "France",      "goals_scored": 146, "teams": 24, "matches": 52},
    {"year": 1986, "host": "Mexico",       "winner": "Argentina",    "runner_up": "West Germany",  "third_place": "France",         "fourth_place": "Belgium",     "goals_scored": 132, "teams": 24, "matches": 52},
    {"year": 1990, "host": "Italy",        "winner": "West Germany", "runner_up": "Argentina",     "third_place": "Italy",          "fourth_place": "England",     "goals_scored": 115, "teams": 24, "matches": 52},
    {"year": 1994, "host": "USA",          "winner": "Brazil",       "runner_up": "Italy",         "third_place": "Sweden",         "fourth_place": "Bulgaria",    "goals_scored": 141, "teams": 24, "matches": 52},
    {"year": 1998, "host": "France",       "winner": "France",       "runner_up": "Brazil",        "third_place": "Croatia",        "fourth_place": "Netherlands", "goals_scored": 171, "teams": 32, "matches": 64},
    {"year": 2002, "host": "South Korea/Japan", "winner": "Brazil",  "runner_up": "Germany",       "third_place": "Turkey",         "fourth_place": "South Korea", "goals_scored": 161, "teams": 32, "matches": 64},
    {"year": 2006, "host": "Germany",      "winner": "Italy",        "runner_up": "France",        "third_place": "Germany",        "fourth_place": "Portugal",    "goals_scored": 147, "teams": 32, "matches": 64},
    {"year": 2010, "host": "South Africa", "winner": "Spain",        "runner_up": "Netherlands",   "third_place": "Germany",        "fourth_place": "Uruguay",     "goals_scored": 145, "teams": 32, "matches": 64},
    {"year": 2014, "host": "Brazil",       "winner": "Germany",      "runner_up": "Argentina",     "third_place": "Netherlands",    "fourth_place": "Brazil",      "goals_scored": 171, "teams": 32, "matches": 64},
    {"year": 2018, "host": "Russia",       "winner": "France",       "runner_up": "Croatia",       "third_place": "Belgium",        "fourth_place": "England",     "goals_scored": 169, "teams": 32, "matches": 64},
    {"year": 2022, "host": "Qatar",        "winner": "Argentina",    "runner_up": "France",        "third_place": "Croatia",        "fourth_place": "Morocco",     "goals_scored": 172, "teams": 32, "matches": 64},
]

# ─────────────────────────────────────────
#  BUILD DATAFRAME
# ─────────────────────────────────────────
def build_dataframe():
    df = pd.DataFrame(world_cup_records)

    # Average goals per match
    df["avg_goals_per_match"] = (df["goals_scored"] / df["matches"]).round(2)

    # Was the host country the winner?
    df["host_won"] = (df["host"] == df["winner"]).astype(int)

    # Which confederation won? (for ML feature later)
    confederation_map = {
        "Uruguay": "CONMEBOL", "Argentina": "CONMEBOL", "Brazil": "CONMEBOL",
        "Chile": "CONMEBOL", "Colombia": "CONMEBOL", "Paraguay": "CONMEBOL",
        "Italy": "UEFA", "West Germany": "UEFA", "Germany": "UEFA",
        "France": "UEFA", "England": "UEFA", "Spain": "UEFA",
        "Netherlands": "UEFA", "Czechoslovakia": "UEFA", "Hungary": "UEFA",
        "Sweden": "UEFA", "Croatia": "UEFA", "Portugal": "UEFA",
        "Belgium": "UEFA", "Poland": "UEFA", "Yugoslavia": "UEFA",
        "USSR": "UEFA", "Austria": "UEFA", "Denmark": "UEFA",
        "USA": "CONCACAF", "Mexico": "CONCACAF",
        "South Korea": "AFC", "Japan": "AFC", "Australia": "AFC",
        "Morocco": "CAF", "Senegal": "CAF", "Cameroon": "CAF",
        "South Africa": "CAF",
    }
    df["winner_confederation"] = df["winner"].map(confederation_map).fillna("UEFA")

    # Tournament era
    df["era"] = pd.cut(
        df["year"],
        bins=[1929, 1950, 1970, 1990, 2010, 2030],
        labels=["Early (1930-50)", "Classic (1954-70)", "Modern (1974-90)", "Recent (1994-2010)", "Current (2014+)"]
    )

    return df

# ─────────────────────────────────────────
#  SAVE TO CSV + SQLITE
# ─────────────────────────────────────────
def save_data(df):
    # Make sure data folder exists
    base_dir = os.path.dirname(os.path.abspath(__file__))
 
    # Save to CSV
    csv_path = os.path.join(base_dir, "world_cup_history.csv")
    df.to_csv(csv_path, index=False)
    print(f"✅ CSV saved → {csv_path}")

    # Save to SQLite
    db_path = os.path.join(base_dir, "world_cup.db")
    conn = sqlite3.connect(db_path)
    df.to_sql("world_cup_history", conn, if_exists="replace", index=False)
    conn.close()
    print(f"✅ Database saved → {db_path}")

    return csv_path, db_path


# ─────────────────────────────────────────
#  QUICK STATS SUMMARY
# ─────────────────────────────────────────
def print_summary(df):
    print("\n🏆  WORLD CUP HISTORICAL DATA SUMMARY")
    print("=" * 45)
    print(f" Tournaments loaded : {len(df)}")
    print(f" Years covered : {df['year'].min()} – {df['year'].max()}")
    print(f" Total goals scored : {df['goals_scored'].sum()}")
    print(f" Most successful : {df['winner'].value_counts().index[0]} "
          f"({df['winner'].value_counts().iloc[0]} titles)")
    print(f"  Host advantage wins: {df['host_won'].sum()} / {len(df)}")
    print(f"\n  🥇 Winners by confederation:")
    print(df["winner_confederation"].value_counts().to_string())
    print(f"\n  📅 All winners:")
    for _, row in df.iterrows():
        print(f"    {row['year']} {row['host']:<20} →  {row['winner']}")
    print("=" * 45)


# ─────────────────────────────────────────
#  RUN
# ─────────────────────────────────────────
if __name__ == "__main__":
    df = build_dataframe()
    save_data(df)
    print_summary(df)