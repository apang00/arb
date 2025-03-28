import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd
import os

class TableFetch:
    def __init__(self, url):
        self.url = url
        self.soup = BeautifulSoup(requests.get(url).content, 'html.parser')

    def _get_team_xpaths(self):
        comments = self.soup.find_all(string=lambda text: isinstance(text, Comment))
        line_score_html = next(c for c in comments if 'id="line_score"' in c)
        table = pd.read_html(line_score_html, header=[0, 1])[0]
        teams = table.iloc[:, 0].tolist()
        return [f'//*[@id="box-{team}-game-basic"]' for team in teams]

    def fetch_and_save_tables(self, base_path="/Users/p/Desktop/Projects/arb/arb/data/output"):
        xpaths = self._get_team_xpaths()

        # Extract date from URL to create nested folders
        date_part = self.url.split('/')[-1][:8]
        year, month, day = date_part[:4], date_part[4:6], date_part[6:8]

        # Create nested directory structure
        year_path = os.path.join(base_path, year)
        month_path = os.path.join(year_path, month)
        day_path = os.path.join(month_path, day)
        os.makedirs(day_path, exist_ok=True)

        for xpath in xpaths:
            css_selector = xpath.replace('//*[@id="', '#').replace('"]', '')
            table = self.soup.select_one(css_selector)

            if table:
                df = pd.read_html(str(table), header=[0, 1])[0]

                # Rename columns
                df.columns = ['Names'] + [col[1] for col in df.columns[1:]]

                # Remove specified columns
                df.drop(columns=['ORB', 'DRB', 'GmSc'], inplace=True, errors='ignore')

                # File name and save path
                filename = css_selector.strip('#') + '.parquet'
                file_path = os.path.join(day_path, filename)

                df.to_parquet(file_path)
                print(f"Data saved to '{file_path}'.")
            else:
                print(f"Table not found for {css_selector}.")

        print("\nGenerated XPaths:")
        print(xpaths)

# Example Usage
url = 'https://www.basketball-reference.com/boxscores/201411020NYK.html'
table_fetcher = TableFetch(url)
table_fetcher.fetch_and_save_tables()