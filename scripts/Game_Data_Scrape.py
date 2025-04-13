import datetime
import requests
import json
from bs4 import BeautifulSoup
import time

class SeasonGenerator:
    def __init__(self, start_year=2025):
        self.start_year = start_year
        self.current_year = datetime.datetime.now().year
        self.current_month = datetime.datetime.now().month

    def generate_urls(self):
        urls = []
        months = ["october", "november", "december", "january", "february", "march", "april", "may", "june"]
        extra_2020_months = ["july", "august", "september"]

        for year in range(self.start_year, self.current_year + 1):
            if year == 2020:
                urls.append(f"https://www.basketball-reference.com/leagues/NBA_{year}_games-october-2019.html")
                for month in months[1:6]:
                    urls.append(f"https://www.basketball-reference.com/leagues/NBA_{year}_games-{month}.html")
                for month in extra_2020_months:
                    urls.append(f"https://www.basketball-reference.com/leagues/NBA_{year}_games-{month}.html")
            elif year == 2021:
                for month in months[2:]:
                    urls.append(f"https://www.basketball-reference.com/leagues/NBA_{year}_games-{month}.html")
            else:
                current_months = months[:months.index('june')+1] if year < self.current_year else months[:months.index(self.get_current_month_name())+1]
                for month in current_months:
                    urls.append(f"https://www.basketball-reference.com/leagues/NBA_{year}_games-{month}.html")

        return urls

    def get_current_month_name(self):
        month_number = datetime.datetime.now().month
        month_names = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
        return month_names[month_number - 1]

class GameDataFetcher:
    def __init__(self, urls):
        self.urls = urls
        self.team_abbreviations = {
            "Atlanta Hawks": "ATL",
            "Boston Celtics": "BOS",
            "Brooklyn Nets": "BRK",
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
            "Phoenix Suns": "PHO",
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
                        date_obj = datetime.datetime.strptime(date_str, "%a, %b %d, %Y")
                        formatted_date = date_obj.strftime("%Y%m%d")
                        teams = event.get("name", "").split('@')
                        if len(teams) > 1:
                            home_team = teams[1].strip()
                            team_code = self.team_abbreviations.get(home_team, "Unknown")
                            full_url = f"https://www.basketball-reference.com/boxscores/{formatted_date}0{team_code}.html"
                            game_urls.append(full_url)

                game_data[url] = game_urls
            else:
                print(f"No game data found in the HTML for URL: {url}")

        self.write_to_file(game_data)

    def write_to_file(self, game_data):
        with open('game_data.json', 'w') as f:
            json.dump(game_data, f, indent=4)
        print("Game data has been written to 'game_data.json'")

if __name__ == "__main__":
    generator = SeasonGenerator()
    urls = generator.generate_urls()
    fetcher = GameDataFetcher(urls)
    fetcher.fetch_game_data()

