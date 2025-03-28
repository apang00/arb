import requests
import json

# API key and configuration setup
API_KEY = '51eabebe6fe1969d7d918926f1292a2f'
EVENT_ID = 'f68297ad59b106aaf5970a0a385f539f'
REGIONS = 'us,us2'
SPORT = 'basketball_nba'
MARKETS = (
    "h2h,h2h_h1,h2h_h2,h2h_q1,h2h_q2,h2h_q3,h2h_q4,"
    "spreads,spreads_h1,spreads_h2,spreads_q1,spreads_q2,spreads_q3,spreads_q4,"
    "totals,totals_h1,totals_h2,totals_q1,totals_q2,totals_q3,totals_q4,"
    "team_totals,team_totals_h1,team_totals_h2,team_totals_q1,team_totals_q2,team_totals_q3,team_totals_q4,"
    "player_points,player_rebounds,player_assists,player_blocks,player_steals,player_threes,player_turnovers,"
    "alternate_spreads,alternate_team_totals,"
    "player_points_assists,player_points_rebounds,player_points_rebounds_assists,player_points_assists"
)
ODDS_FORMAT = 'american'
DATE_FORMAT = 'iso'
DATE = '2023-05-03T12:00:00Z'

# Function to save JSON response to a file
def save_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# API URL setup
url = f"https://api.the-odds-api.com/v4/historical/sports/{SPORT}/events/{EVENT_ID}/odds"
params = {
    'apiKey': API_KEY,
    'regions': REGIONS,
    'markets': MARKETS,
    'oddsFormat': ODDS_FORMAT,
    'dateFormat': DATE_FORMAT,
    'date': DATE
}

# Make the API request
response = requests.get(url, params=params)

if response.status_code != 200:
    print(f'Failed to get odds: status_code {response.status_code}, response body {response.text}')
else:
    data = response.json()
    save_json(data, 'odds_data.json')
    print('Saved odds data to "odds_data.json"')
    print('Remaining requests:', response.headers.get('x-requests-remaining', 'N/A'))
    print('Used requests:', response.headers.get('x-requests-used', 'N/A'))
