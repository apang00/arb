import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime

class GameDataFetcher:
    def __init__(self, urls):
        self.urls = urls
        self.team_abbreviations = {
            "Atlanta Hawks": "ATL",
            "Boston Celtics": "BOS",
            "Brooklyn Nets": "BKN",
            "Charlotte Hornets": "CHO",
            "Chicago Bulls": "CHI",
            "Cleveland Cavaliers": "CLE",
            "Dallas Mavericks": "DAL",
            "Denver Nuggets": "DEN",
            "Detroit Pistons": "DET",
            "Golden State Warriors": "GSW",
            "Houston Rockets": "HOU",
            "Indiana Pacers": "IND",
            "Los Angeles Clippers": "LAC",
            "Los Angeles Lakers": "LAL",
            "Memphis Grizzlies": "MEM",
            "Miami Heat": "MIA",
            "Milwaukee Bucks": "MIL",
            "Minnesota Timberwolves": "MIN",
            "New Orleans Pelicans": "NOP",
            "New York Knicks": "NYK",
            "Oklahoma City Thunder": "OKC",
            "Orlando Magic": "ORL",
            "Philadelphia 76ers": "PHI",
            "Phoenix Suns": "PHX",
            "Portland Trail Blazers": "POR",
            "Sacramento Kings": "SAC",
            "San Antonio Spurs": "SAS",
            "Toronto Raptors": "TOR",
            "Utah Jazz": "UTA",
            "Washington Wizards": "WAS"
        }

    def fetch_game_data(self):
        game_data = {}
        for url in self.urls:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            script = soup.find('script', {'type': 'application/ld+json'})
            game_urls = []

            if script:
                data = json.loads(script.string)
                for event in data:
                    date_str = event.get("startDate", "")
                    if date_str:
                        date_obj = datetime.strptime(date_str, "%a, %b %d, %Y")
                        formatted_date = date_obj.strftime("%Y%m%d")
                    else:
                        formatted_date = "No date provided"

                    teams = event.get("name", "").split('@')
                    if len(teams) > 1:
                        home_team = teams[1].strip()
                        team_code = self.team_abbreviations.get(home_team, "Unknown")
                    else:
                        team_code = "Unknown"

                    url_prefix = "https://www.basketball-reference.com/boxscores/"
                    url_suffix = ".html"
                    full_url = f"{url_prefix}{formatted_date}0{team_code}{url_suffix}"
                    game_urls.append(full_url)

                game_data[url] = game_urls
            else:
                print(f"No game data found in the HTML for URL: {url}")

        self.write_to_file(game_data)

    def write_to_file(self, game_data):
        with open('game_data.json', 'w') as f:
            json.dump(game_data, f, indent=4)
        print("Game data has been written to 'game_data.json'")

# Usage
urls = [
    "https://www.basketball-reference.com/leagues/NBA_2015_games-october.html",
    "https://www.basketball-reference.com/leagues/NBA_2015_games-november.html"
]
fetcher = GameDataFetcher(urls)
fetcher.fetch_game_data()
