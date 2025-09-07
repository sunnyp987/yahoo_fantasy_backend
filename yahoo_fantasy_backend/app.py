from flask import Flask, jsonify
import requests
import time

app = Flask(__name__)

# --- Configuration ---
CLIENT_ID = "dj0yJmk9WUo5TlFGSDZUSFBPJmQ9WVdrOWNUaFliR3Q1U2pFbWNHbzlNQT09"
CLIENT_SECRET = "36739b02d7b5306a4d0e246f94f205a911047861"
LEAGUE_KEY = "461.l.234838"
TEAM_KEY = "461.l.234838.t.10"
REDIRECT_URI = "https://localhost/callback"
REFRESH_TOKEN = "YOUR_REFRESH_TOKEN"  # Replace with your actual refresh token
MY_TEAM_NAME = "Bhoserina"

BASE_URL = "https://fantasysports.yahooapis.com/fantasy/v2"

# --- Globals ---
ACCESS_TOKEN = None
TOKEN_EXPIRES_AT = 0

# --- Functions ---
def refresh_access_token():
    global ACCESS_TOKEN, TOKEN_EXPIRES_AT
    url = "https://api.login.yahoo.com/oauth2/get_token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "redirect_uri": REDIRECT_URI
    }
    response = requests.post(url, data=data, auth=(CLIENT_ID, CLIENT_SECRET))
    token_data = response.json()
    ACCESS_TOKEN = token_data.get("access_token")
    expires_in = token_data.get("expires_in", 3600)
    TOKEN_EXPIRES_AT = time.time() + expires_in - 60
    print(f"Access token refreshed, expires in {expires_in} seconds.")

def yahoo_api(endpoint):
    global ACCESS_TOKEN, TOKEN_EXPIRES_AT
    if ACCESS_TOKEN is None or time.time() > TOKEN_EXPIRES_AT:
        refresh_access_token()
    url = f"{BASE_URL}/{endpoint}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": response.text}
    return response.json()

# --- API Endpoints ---
@app.route("/players")
def get_players():
    data = yahoo_api(f"team/{TEAM_KEY}/roster/players;out=stats?format=json")
    players = []
    try:
        for p in data["fantasy_content"]["team"][1]["roster"]["players"]:
            player = p["player"][0]
            players.append({
                "Player": player[2]["name"]["full"],
                "Position": player[1]["display_position"],
                "Team": player[1]["editorial_team_abbr"],
                "Status": player[1]["status"],
                "Projected Points": player[1].get("projected_points", 0),
                "Actual Points": player[1].get("total_points", 0)
            })
    except:
        return {"error": "Failed to parse player data"}
    return jsonify(players)

@app.route("/teams")
def get_teams():
    data = yahoo_api(f"league/{LEAGUE_KEY}/teams?format=json")
    teams = []
    try:
        for t in data["fantasy_content"]["league"][1]["teams"]:
            team = t["team"][0]
            teams.append({
                "Team Name": team["name"],
                "Team Key": team["team_key"],
                "Manager": team["managers"][0]["manager"]["nickname"]
            })
    except:
        return {"error": "Failed to parse teams"}
    return jsonify(teams)

@app.route("/matchups")
def get_matchups():
    data = yahoo_api(f"league/{LEAGUE_KEY}/scoreboard;week=1?format=json")
    matchups = []
    try:
        for m in data["fantasy_content"]["league"][1]["scoreboard"]["matchups"]:
            matchup = m["matchup"][0]
            matchups.append({
                "Team A": matchup["teams"]["0"]["team"][0]["name"],
                "Team B": matchup["teams"]["1"]["team"][0]["name"],
                "Team A Points": matchup["teams"]["0"]["team"][1]["team_points"]["total"],
                "Team B Points": matchup["teams"]["1"]["team"][1]["team_points"]["total"]
            })
    except:
        return {"error": "Failed to parse matchups"}
    return jsonify(matchups)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
