import pandas as pd
import numpy as np
import sqlite3
import os
import pickle
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────
#  LOAD DATA
# ─────────────────────────────────────────
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "..", "data")
db_path = os.path.join(data_dir, "world_cup.db")

conn = sqlite3.connect(db_path)
history_df = pd.read_sql("SELECT * FROM world_cup_history", conn)
teams_df = pd.read_sql("SELECT * FROM teams_2026", conn)
conn.close()
print(f"✅ Loaded {len(history_df)} tournaments + {len(teams_df)} teams")

# ─────────────────────────────────────────
#  BUILD TRAINING DATA
# ─────────────────────────────────────────
# For each tournament, every team that appeared gets a row.
# The winner gets label = 1, everyone else = 0.

def build_training_data(history_df):
    rows = []

    for _, row in history_df.iterrows():
        year = row["year"]
        winner = row["winner"]
        runner_up = row["runner_up"]
        third = row["third_place"]
        fourth = row["fourth_place"]
        host        = row["host"]
        teams_count = row["teams"]

        # All four finalists as training examples
        finalists = [
            (winner, 1, 1), # (team, is_winner, finish_position_score)
            (runner_up, 0, 0.6),
            (third, 0, 0.3),
            (fourth, 0, 0.1),
        ]

        conf_map = {
            "Uruguay": "CONMEBOL", "Argentina": "CONMEBOL", "Brazil": "CONMEBOL",
            "Chile": "CONMEBOL", "Colombia": "CONMEBOL", "Paraguay": "CONMEBOL",
            "Italy": "UEFA", "West Germany": "UEFA", "Germany": "UEFA",
            "France": "UEFA", "England": "UEFA", "Spain": "UEFA",
            "Netherlands": "UEFA", "Czechoslovakia": "UEFA","Hungary": "UEFA",
            "Sweden": "UEFA", "Croatia": "UEFA", "Portugal": "UEFA",
            "Belgium": "UEFA", "Poland": "UEFA", "Yugoslavia": "UEFA",
            "USSR": "UEFA", "Austria": "UEFA", "Denmark": "UEFA",
            "USA": "CONCACAF", "Mexico": "CONCACAF",
            "South Korea": "AFC", "Japan": "AFC", "Turkey": "UEFA",
            "Morocco": "CAF", "Senegal": "CAF", "Bulgaria": "UEFA",
        }

        for team, is_winner, _ in finalists:
            conf = conf_map.get(team, "UEFA")
            is_host = 1 if (team == host or team in host) else 0
            is_uefa = 1 if conf == "UEFA" else 0
            is_conmebol = 1 if conf == "CONMEBOL" else 0
            is_concacaf = 1 if conf == "CONCACAF" else 0
            is_afc = 1 if conf == "AFC" else 0
            is_caf  = 1 if conf == "CAF" else 0

            rows.append({
                "year": year,
                "team": team,
                "is_host": is_host,
                "is_uefa": is_uefa,
                "is_conmebol": is_conmebol,
                "is_concacaf": is_concacaf,
                "is_afc": is_afc,
                "is_caf": is_caf,
                "teams_count": teams_count,
                "is_winner": is_winner,
            })

    return pd.DataFrame(rows)

train_df = build_training_data(history_df)
print(f"✅ Training data built — {len(train_df)} rows")
print(f" Winners in dataset: {train_df['is_winner'].sum()}")

# ─────────────────────────────────────────
#  TRAIN THE MODEL
# ─────────────────────────────────────────
features = ["is_host", "is_uefa", "is_conmebol", "is_concacaf",
            "is_afc", "is_caf", "teams_count"]

X = train_df[features]
y = train_df["is_winner"]

# Train two models and pick the best one
rf_model = RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")
gb_model= GradientBoostingClassifier(n_estimators=200, random_state=42)

rf_scores = cross_val_score(rf_model, X, y, cv=5, scoring="roc_auc")
gb_scores = cross_val_score(gb_model, X, y, cv=5, scoring="roc_auc")

print(f"\n📊 Model Evaluation (Cross-Validation AUC):")
print(f"   Random Forest : {rf_scores.mean():.3f} ± {rf_scores.std():.3f}")
print(f"   Gradient Boosting : {gb_scores.mean():.3f} ± {gb_scores.std():.3f}")

# Use the better model
if rf_scores.mean() >= gb_scores.mean():
    best_model = rf_model
    print(f"\n  ✅ Using: Random Forest")
else:
    best_model = gb_model
    print(f"\n  ✅ Using: Gradient Boosting")

# Train on full dataset
best_model.fit(X, y)

# Save the model
model_path = os.path.join(base_dir, "wc_model.pkl")
with open(model_path, "wb") as f:
    pickle.dump(best_model, f)
print(f"  ✅ Model saved → {model_path}")

# ─────────────────────────────────────────
#  PREDICT 2026 WINNERS
# ─────────────────────────────────────────
def predict_2026(teams_df, model):
    conf_dummies = pd.get_dummies(teams_df["confederation"])

    teams_df["is_host"]  = teams_df["host_2026"]
    teams_df["is_uefa"]  = (teams_df["confederation"] == "UEFA").astype(int)
    teams_df["is_conmebol"] = (teams_df["confederation"] == "CONMEBOL").astype(int)
    teams_df["is_concacaf"] = (teams_df["confederation"] == "CONCACAF").astype(int)
    teams_df["is_afc"]  = (teams_df["confederation"] == "AFC").astype(int)
    teams_df["is_caf"] = (teams_df["confederation"] == "CAF").astype(int)
    teams_df["teams_count"] = 48 # 2026 has 48 teams

    X_2026 = teams_df[features]
    probs = model.predict_proba(X_2026)[:, 1]

    # Boost by WC wins and FIFA rank
    teams_df["raw_prob"]  = probs
    teams_df["rank_boost"] = 1 + (1 / teams_df["fifa_rank"]) * 10
    teams_df["win_boost"]  = 1 + (teams_df["wc_wins"] * 0.15)
    teams_df["final_prob"] = teams_df["raw_prob"] * teams_df["rank_boost"] * teams_df["win_boost"]

    # Normalise to 100%
    total = teams_df["final_prob"].sum()
    teams_df["win_probability"] = ((teams_df["final_prob"] / total) * 100).round(2)

    return teams_df.sort_values("win_probability", ascending=False)

results = predict_2026(teams_df.copy(), best_model)

# Save predictions to database
conn = sqlite3.connect(db_path)
results[["team", "confederation", "wc_wins", "wc_appearances",
         "fifa_rank", "host_2026", "win_probability"]].to_sql(
    "predictions_2026", conn, if_exists="replace", index=False)
conn.close()

# ─────────────────────────────────────────
#  PRINT RESULTS
# ─────────────────────────────────────────
print(f"\n🏆  2026 WORLD CUP WIN PROBABILITIES — TOP 20")
print("=" * 50)
for i, (_, row) in enumerate(results.head(20).iterrows(), 1):
    bar = "█" * int(row["win_probability"] / 0.5)
    host = " 🏠" if row["host_2026"] else ""
    print(f" {i:>2}. {row['team']:<20} {row['win_probability']:>5.2f}% {bar}{host}")
print("=" * 50)
print(f"\n✅ Predictions saved to database. Day 4 complete!")