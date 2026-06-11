# ⚽ World Cup 2026 Predictor

A full-stack AI-powered web app that predicts the 2026 FIFA World Cup winner and tracks live match results in real time.

🌐 **Live site:** [world-cup-predictor-rnhl.onrender.com](https://world-cup-predictor-rnhl.onrender.com)

---

## Features

### 🤖 Historical Prediction Model
- Machine learning model trained on every World Cup since 1930 (22 tournaments)
- Factors in FIFA rankings, host advantage, confederation strength, and WC experience
- Generates win probabilities for all 48 qualified teams

### 📡 Live Match Tracker
- Real-time scores and standings via football-data.org API
- Auto-refreshes every 5 minutes during the tournament
- Group standings with live results

### 🎲 Advancement Odds Simulator
- Monte Carlo simulation running 10,000 tournaments
- Calculates each team's % chance of advancing from the group stage
- Updates automatically as match results come in

### 📖 Historical Data
- Full results from every World Cup (1930–2022)
- Interactive charts: wins by country, confederation dominance, goals over time

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| ML Model | scikit-learn (Random Forest / Gradient Boosting) |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript, Chart.js |
| Live Data | football-data.org API |
| Deployment | Render |

---

## Project Structure

world-cup-predictor/
│
├── app.py                  ← Flask app + all API routes
├── scheduler.py            ← Auto-refresh background scheduler
├── requirements.txt
├── render.yaml             ← Render deployment config
│
├── data/
│   ├── world_cup_history.py   ← Historical data + SQLite setup
│   ├── explore_data.py        ← Feature engineering + charts
│   ├── live_tracker.py        ← Live scores API integration
│   ├── simulator.py           ← Monte Carlo simulator
│   └── world_cup.db           ← SQLite database
│
├── models/
│   ├── predict_winner.py      ← ML model training + predictions
│   └── wc_model.pkl           ← Saved trained model
│
├── templates/
│   ├── index.html             ← Homepage
│   ├── predictions.html       ← Predictions page
│   ├── history.html           ← History page
│   └── live.html              ← Live tracker page
│
├── static/
│   └── css/
│       └── mobile.css         ← Mobile responsive styles
│
└── tests/
└── test_setup.py          ← Environment verification

---

## Running Locally

```bash
# Clone the repo
git clone https://github.com/Samrawitg/world-cup-predictor.git
cd world-cup-predictor

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Add your API key
echo "FOOTBALL_API_KEY=your_key_here" >> .env

# Run the app
python3 app.py
```

Then open **http://127.0.0.1:5000**

---

## Data Sources

- Historical World Cup data: built-in dataset (1930–2022)
- Live match data: [football-data.org](https://www.football-data.org)
- FIFA rankings: manually sourced (June 2026)

---

Built with Python + Flask · Deployed on Render · Data updated live during the 2026 World Cup