import datetime
from bs4 import BeautifulSoup

class SeasonGenerator:
    def __init__(self, start_year=2015):
        self.start_year = start_year
        self.current_year = datetime.datetime.now().year
        self.current_month = datetime.datetime.now().month

    def generate_urls(self):
        urls = []
        # Common months for NBA seasons
        months = ["october", "november", "december", "january", "february", "march", "april", "may", "june"]
        # Additional months for the 2020 season
        extra_2020_months = ["july", "august", "september"]

        for year in range(self.start_year, self.current_year + 1):
            if year == 2020:
                # Special case for 2020, including extension months
                urls.append(f"https://www.basketball-reference.com/leagues/NBA_{year}_games-october-2019.html")
                for month in months[1:6]:  # only until March for 2020
                    urls.append(f"https://www.basketball-reference.com/leagues/NBA_{year}_games-{month}.html")
                for month in extra_2020_months:  # adding July to September for 2020
                    urls.append(f"https://www.basketball-reference.com/leagues/NBA_{year}_games-{month}.html")
            elif year == 2021:
                # Special case for 2021
                for month in months[2:]:  # starting from December
                    urls.append(f"https://www.basketball-reference.com/leagues/NBA_{year}_games-{month}.html")
            else:
                # General case for other years
                current_months = months[:months.index('june')+1] if year < self.current_year else months[:months.index(self.get_current_month_name())+1]
                for month in current_months:
                    urls.append(f"https://www.basketball-reference.com/leagues/NBA_{year}_games-{month}.html")

        return urls

    def get_current_month_name(self):
        # Returns the name of the current month, correctly handles indexing into the months list
        month_number = datetime.datetime.now().month
        month_names = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
        return month_names[month_number - 1]


# Usage
if __name__ == "__main__":
    generator = SeasonGenerator()
    season_urls = generator.generate_urls()
    
    # Writing URLs to a file named 'SeasonMonths.txt' in the same directory as the script
    with open('SeasonMonths.txt', 'w') as file:
        for url in season_urls:
            file.write(url + '\n')  # Write each URL on a new line

    print("URLs have been written to 'SeasonMonths.txt'")
