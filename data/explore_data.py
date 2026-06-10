import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import sqlite3
import os

# ─────────────────────────────────────────
#  LOAD DATA FROM DATABASE
# ─────────────────────────────────────────
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path  = os.path.join(base_dir, "world_cup.db")
conn     = sqlite3.connect(db_path)
df       = pd.read_sql("SELECT * FROM world_cup_history", conn)
conn.close()
print(f"✅ Loaded {len(df)} tournaments from database\n")

# ─────────────────────────────────────────
#  FEATURE: WIN COUNT PER COUNTRY
# ─────────────────────────────────────────
win_counts = df["winner"].value_counts().reset_index()
win_counts.columns = ["country", "wins"]
print("🥇 Wins per country:")
print(win_counts.to_string(index=False))

# ─────────────────────────────────────────
#  FEATURE: HOST ADVANTAGE
# ─────────────────────────────────────────
host_wins   = df["host_won"].sum()
host_total  = len(df)
print(f"\n🏠 Host country won {host_wins} out of {host_total} tournaments "
      f"({round(host_wins/host_total*100)}%)")

# ─────────────────────────────────────────
#  FEATURE: 2026 QUALIFIED TEAMS + FEATURES
# ─────────────────────────────────────────
# All 48 qualified teams with features we'll use in the ML model
teams_2026 = [
    # CONMEBOL
    {"team": "Argentina",     "confederation": "CONMEBOL", "wc_wins": 3, "wc_appearances": 18, "host_2026": 0, "fifa_rank": 1},
    {"team": "Brazil",        "confederation": "CONMEBOL", "wc_wins": 5, "wc_appearances": 22, "host_2026": 0, "fifa_rank": 5},
    {"team": "Colombia",      "confederation": "CONMEBOL", "wc_wins": 0, "wc_appearances": 7,  "host_2026": 0, "fifa_rank": 9},
    {"team": "Ecuador",       "confederation": "CONMEBOL", "wc_wins": 0, "wc_appearances": 4,  "host_2026": 0, "fifa_rank": 42},
    {"team": "Uruguay",       "confederation": "CONMEBOL", "wc_wins": 2, "wc_appearances": 14, "host_2026": 0, "fifa_rank": 16},
    {"team": "Venezuela",     "confederation": "CONMEBOL", "wc_wins": 0, "wc_appearances": 1,  "host_2026": 0, "fifa_rank": 58},
    {"team": "Paraguay",      "confederation": "CONMEBOL", "wc_wins": 0, "wc_appearances": 9,  "host_2026": 0, "fifa_rank": 64},
    {"team": "Chile",         "confederation": "CONMEBOL", "wc_wins": 0, "wc_appearances": 9,  "host_2026": 0, "fifa_rank": 37},
    {"team": "Bolivia",       "confederation": "CONMEBOL", "wc_wins": 0, "wc_appearances": 3,  "host_2026": 0, "fifa_rank": 85},
    {"team": "Peru",          "confederation": "CONMEBOL", "wc_wins": 0, "wc_appearances": 5,  "host_2026": 0, "fifa_rank": 39},
    # UEFA
    {"team": "France",        "confederation": "UEFA",     "wc_wins": 2, "wc_appearances": 16, "host_2026": 0, "fifa_rank": 2},
    {"team": "England",       "confederation": "UEFA",     "wc_wins": 1, "wc_appearances": 16, "host_2026": 0, "fifa_rank": 3},
    {"team": "Spain",         "confederation": "UEFA",     "wc_wins": 1, "wc_appearances": 16, "host_2026": 0, "fifa_rank": 6},
    {"team": "Germany",       "confederation": "UEFA",     "wc_wins": 4, "wc_appearances": 20, "host_2026": 0, "fifa_rank": 12},
    {"team": "Portugal",      "confederation": "UEFA",     "wc_wins": 0, "wc_appearances": 9,  "host_2026": 0, "fifa_rank": 6},
    {"team": "Netherlands",   "confederation": "UEFA",     "wc_wins": 0, "wc_appearances": 11, "host_2026": 0, "fifa_rank": 7},
    {"team": "Belgium",       "confederation": "UEFA",     "wc_wins": 0, "wc_appearances": 14, "host_2026": 0, "fifa_rank": 14},
    {"team": "Croatia",       "confederation": "UEFA",     "wc_wins": 0, "wc_appearances": 6,  "host_2026": 0, "fifa_rank": 10},
    {"team": "Italy",         "confederation": "UEFA",     "wc_wins": 4, "wc_appearances": 18, "host_2026": 0, "fifa_rank": 9},
    {"team": "Denmark",       "confederation": "UEFA",     "wc_wins": 0, "wc_appearances": 6,  "host_2026": 0, "fifa_rank": 13},
    {"team": "Austria",       "confederation": "UEFA",     "wc_wins": 0, "wc_appearances": 7,  "host_2026": 0, "fifa_rank": 25},
    {"team": "Switzerland",   "confederation": "UEFA",     "wc_wins": 0, "wc_appearances": 12, "host_2026": 0, "fifa_rank": 20},
    {"team": "Serbia",        "confederation": "UEFA",     "wc_wins": 0, "wc_appearances": 13, "host_2026": 0, "fifa_rank": 33},
    {"team": "Czech Republic","confederation": "UEFA",     "wc_wins": 0, "wc_appearances": 10, "host_2026": 0, "fifa_rank": 37},
    {"team": "Turkey",        "confederation": "UEFA",     "wc_wins": 0, "wc_appearances": 2,  "host_2026": 0, "fifa_rank": 29},
    {"team": "Poland",        "confederation": "UEFA",     "wc_wins": 0, "wc_appearances": 9,  "host_2026": 0, "fifa_rank": 24},
    {"team": "Hungary",       "confederation": "UEFA",     "wc_wins": 0, "wc_appearances": 9,  "host_2026": 0, "fifa_rank": 30},
    {"team": "Scotland",      "confederation": "UEFA",     "wc_wins": 0, "wc_appearances": 8,  "host_2026": 0, "fifa_rank": 39},
    {"team": "Greece",        "confederation": "UEFA",     "wc_wins": 0, "wc_appearances": 3,  "host_2026": 0, "fifa_rank": 49},
    {"team": "Romania",       "confederation": "UEFA",     "wc_wins": 0, "wc_appearances": 7,  "host_2026": 0, "fifa_rank": 46},
    {"team": "Slovakia",      "confederation": "UEFA",     "wc_wins": 0, "wc_appearances": 2,  "host_2026": 0, "fifa_rank": 55},
    {"team": "Albania",       "confederation": "UEFA",     "wc_wins": 0, "wc_appearances": 1,  "host_2026": 0, "fifa_rank": 66},
    # CONCACAF
    {"team": "USA",           "confederation": "CONCACAF", "wc_wins": 0, "wc_appearances": 11, "host_2026": 1, "fifa_rank": 11},
    {"team": "Mexico",        "confederation": "CONCACAF", "wc_wins": 0, "wc_appearances": 17, "host_2026": 1, "fifa_rank": 15},
    {"team": "Canada",        "confederation": "CONCACAF", "wc_wins": 0, "wc_appearances": 3,  "host_2026": 1, "fifa_rank": 43},
    {"team": "Costa Rica",    "confederation": "CONCACAF", "wc_wins": 0, "wc_appearances": 6,  "host_2026": 0, "fifa_rank": 51},
    {"team": "Panama",        "confederation": "CONCACAF", "wc_wins": 0, "wc_appearances": 2,  "host_2026": 0, "fifa_rank": 72},
    {"team": "Jamaica",       "confederation": "CONCACAF", "wc_wins": 0, "wc_appearances": 2,  "host_2026": 0, "fifa_rank": 47},
    {"team": "Honduras",      "confederation": "CONCACAF", "wc_wins": 0, "wc_appearances": 3,  "host_2026": 0, "fifa_rank": 82},
    # AFC
    {"team": "Japan",         "confederation": "AFC",      "wc_wins": 0, "wc_appearances": 7,  "host_2026": 0, "fifa_rank": 18},
    {"team": "South Korea",   "confederation": "AFC",      "wc_wins": 0, "wc_appearances": 11, "host_2026": 0, "fifa_rank": 23},
    {"team": "Iran",          "confederation": "AFC",      "wc_wins": 0, "wc_appearances": 6,  "host_2026": 0, "fifa_rank": 22},
    {"team": "Australia",     "confederation": "AFC",      "wc_wins": 0, "wc_appearances": 6,  "host_2026": 0, "fifa_rank": 23},
    {"team": "Saudi Arabia",  "confederation": "AFC",      "wc_wins": 0, "wc_appearances": 6,  "host_2026": 0, "fifa_rank": 56},
    {"team": "Uzbekistan",    "confederation": "AFC",      "wc_wins": 0, "wc_appearances": 1,  "host_2026": 0, "fifa_rank": 60},
    # CAF
    {"team": "Morocco",       "confederation": "CAF",      "wc_wins": 0, "wc_appearances": 6,  "host_2026": 0, "fifa_rank": 14},
    {"team": "Senegal",       "confederation": "CAF",      "wc_wins": 0, "wc_appearances": 3,  "host_2026": 0, "fifa_rank": 17},
    {"team": "Egypt",         "confederation": "CAF",      "wc_wins": 0, "wc_appearances": 3,  "host_2026": 0, "fifa_rank": 34},
    {"team": "Nigeria",       "confederation": "CAF",      "wc_wins": 0, "wc_appearances": 7,  "host_2026": 0, "fifa_rank": 40},
]

teams_df = pd.DataFrame(teams_2026)

# Save teams to database
conn = sqlite3.connect(db_path)
teams_df.to_sql("teams_2026", conn, if_exists="replace", index=False)
conn.close()
print(f"\n✅ Saved {len(teams_df)} qualified teams to database")

# ─────────────────────────────────────────
#  VISUALIZATIONS
# ─────────────────────────────────────────
sns.set_theme(style="darkgrid")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("FIFA World Cup Historical Analysis (1930–2022)", fontsize=16, fontweight="bold")

# Chart 1 — Wins per country
ax1 = axes[0, 0]
colors = sns.color_palette("husl", len(win_counts))
ax1.barh(win_counts["country"], win_counts["wins"], color=colors)
ax1.set_title("🥇 World Cup Wins by Country")
ax1.set_xlabel("Number of Wins")
ax1.invert_yaxis()

# Chart 2 — Goals per tournament
ax2 = axes[0, 1]
ax2.plot(df["year"], df["avg_goals_per_match"], marker="o", color="orange", linewidth=2)
ax2.set_title("⚽ Average Goals per Match Over Time")
ax2.set_xlabel("Year")
ax2.set_ylabel("Avg Goals / Match")

# Chart 3 — Wins by confederation
ax3 = axes[1, 0]
conf_wins = df["winner_confederation"].value_counts()
ax3.pie(conf_wins, labels=conf_wins.index, autopct="%1.0f%%",
        colors=sns.color_palette("Set2", len(conf_wins)))
ax3.set_title("🌍 Wins by Confederation")

# Chart 4 — 2026 Teams: FIFA rank vs WC appearances
ax4 = axes[1, 1]
conf_colors = {"UEFA": "#4C72B0", "CONMEBOL": "#DD8452",
               "CONCACAF": "#55A868", "AFC": "#C44E52", "CAF": "#8172B2"}
for conf, group in teams_df.groupby("confederation"):
    ax4.scatter(group["wc_appearances"], group["fifa_rank"],
                label=conf, color=conf_colors.get(conf, "gray"),
                s=80, alpha=0.8)
ax4.set_title("2026 Teams: Appearances vs FIFA Rank")
ax4.set_xlabel("World Cup Appearances")
ax4.set_ylabel("FIFA Rank (lower = better)")
ax4.invert_yaxis()
ax4.legend(fontsize=8)

plt.tight_layout()

# Save the chart
chart_path = os.path.join(base_dir, "wc_analysis.png")
plt.savefig(chart_path, dpi=150, bbox_inches="tight")
print(f"\n✅ Chart saved → {chart_path}")
plt.show()
print("\n🎉 Day 3 complete! Database has historical data + 48 qualified teams.")
