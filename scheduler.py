import threading
import time
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "data"))

from live_tracker import fetch_standings, fetch_matches, save_standings, save_matches
from simulator    import run_simulation, save_simulation

def refresh_all():
    print("⏰ Auto-refresh triggered...")
    try:
        save_standings(fetch_standings())
        save_matches(fetch_matches())
        results = run_simulation(10000)
        save_simulation(results)
        print("✅ Auto-refresh complete")
    except Exception as e:
        print(f"❌ Auto-refresh error: {e}")

def start_scheduler(interval_minutes=5):
    def loop():
        while True:
            time.sleep(interval_minutes * 60)
            refresh_all()
    t = threading.Thread(target=loop, daemon=True)
    t.start()
    print(f"⏰ Scheduler started — refreshing every {interval_minutes} minutes")
