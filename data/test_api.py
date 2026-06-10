import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FOOTBALL_API_KEY")

r = requests.get(
    "https://api.football-data.org/v4/competitions/WC",
    headers={"X-Auth-Token": API_KEY}
)

print(f"Status: {r.status_code}")
print(f"Response: {r.json()}")