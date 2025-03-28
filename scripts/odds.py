import requests
import json

# API key and configuration setup
API_KEY = '51eabebe6fe1969d7d918926f1292a2f'
SPORT = 'upcoming'
REGIONS = 'us', 'us2'
MARKETS = 'h2h, spreads, totals, team_totals,player_points, player_rebounds, player_assists, player_blocks, player_steals, player_threes, player_turnovers, alternate_spreads, alternate_team_total, alternate_team_spreads, alternate_team_totals, player_points_assists, player_points_rebounds, player_points_assists_rebounds, player_points_assists, spreads'
#[h2h, h2h_h1,h2h_h2, h2h_q1, h2h_q2, h2h_q3, h2h_q4]
#[spreads, spreads_h1, spreads_h2, spreads_q1, spreads_q2, spreads_q3, spreads_q4]
#[totals, totals_h1, totals_h2, totals_q1, totals_q2, totals_q3, totals_q4]
#[team_totals, team_totals_h1, team_totals_h2, team_totals_q1, team_totals_q2, team_totals_q3, team_totals_q4]
#[player_points, player_rebounds, player_assists, player_blocks, player_steals, player_threes, player_turnovers]
#[alternate_spreads, alternate_team_totals]
#[player_points_assists, player_points_rebounds, player_points_assists_rebounds, player_points_assists]
ODDS_FORMAT = 'american'
DATE_FORMAT = 'iso'

# Function to save JSON response to a file
def save_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# Get list of in-season sports
sports_url = 'https://api.the-odds-api.com/v4/historical/sports/basketball_nba/events'
sports_response = requests.get(sports_url, params={'apiKey': API_KEY, 'date': '2023-05-03T12:00:00Z'})

if sports_response.status_code != 200:
    print(f'Failed to get sports: status_code {sports_response.status_code}, response body {sports_response.text}')
else:
    sports_data = sports_response.json()
    save_json(sports_data, 'sports_data.json')
    print('Saved list of in-season sports to "sports_data.json"')

# Get live & upcoming games odds
odds_url = f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds'
odds_response = requests.get(odds_url, params={
    'api_key': API_KEY,
    'regions': REGIONS,
    'markets': MARKETS,
    'oddsFormat': ODDS_FORMAT,
    'dateFormat': DATE_FORMAT,
})

if odds_response.status_code != 200:
    print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')
else:
    odds_data = odds_response.json()
    save_json(odds_data, 'odds_data.json')
    print('Saved odds data to "odds_data.json"')
    print('Remaining requests', odds_response.headers['x-requests-remaining'])
    print('Used requests', odds_response.headers['x-requests-used'])
