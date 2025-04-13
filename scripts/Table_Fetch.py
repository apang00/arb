import json
import time
import os
import sys
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd

class TableFetch:
    def __init__(self, url):
        self.url = url
        try:
            response = requests.get(url)
            if response.status_code == 200:
                self.soup = BeautifulSoup(response.content, 'html.parser')
            else:
                print(f"Error: Received status code {response.status_code} for URL: {url}")
                self.soup = None
        except Exception as e:
            print(f"Error fetching URL {url}: {str(e)}")
            self.soup = None

    def _get_team_xpaths(self):
        if self.soup is None:
            return [], []
            
        comments = self.soup.find_all(string=lambda text: isinstance(text, Comment))
        try:
            line_score_html = next(c for c in comments if 'id="line_score"' in c)
            table = pd.read_html(line_score_html, header=[0, 1])[0]
            teams = table.iloc[:, 0].tolist()
            return teams, [f'//*[@id="box-{team}-game-basic"]' for team in teams]
        except (StopIteration, Exception) as e:
            print(f"Error extracting team XPaths: {str(e)}")
            return [], []
    
    # New helper function to extract points from a specific period table (quarter or half)
    def _extract_points_from_period(self, team, period_type, period_num):
        """
        Extract points data from a specific period table for a team.
        
        Args:
            team: Team abbreviation (e.g., 'ORL', 'NOP')
            period_type: 'q' for quarter or 'h' for half
            period_num: Period number (1-4 for quarters, 1-2 for halves)
            
        Returns:
            Dictionary mapping player names to their points in the specified period
        """
        if self.soup is None:
            return {}
            
        # Construct the XPath for the period table using the pattern provided by the user
        xpath = f'//*[@id="box-{team}-{period_type}{period_num}-basic"]'
        css_selector = xpath.replace('//*[@id="', '#').replace('"]', '')
        
        # Find the table in the HTML
        table = self.soup.select_one(css_selector)
        
        # Initialize empty dictionary to store player points
        player_points = {}
        
        if table:
            try:
                # Parse the table
                df = pd.read_html(str(table), header=[0, 1])[0]
                
                # Extract player names and points
                df.columns = ['Names'] + [col[1] for col in df.columns[1:]]
                
                # Filter out non-player rows
                df = df[~df['Names'].str.contains("Reserves", na=False)]
                df = df[~df['MP'].str.contains("Did Not Play", na=False)]
                
                # Create dictionary mapping player names to points
                for _, row in df.iterrows():
                    player_points[row['Names']] = row['PTS']
            except Exception as e:
                print(f"Error extracting points from period {period_type}{period_num} for team {team}: {str(e)}")
        
        return player_points

    def fetch_and_save_tables(self, base_path="/Users/p/Desktop/Projects/arb/arb/data/output"):
        if self.soup is None:
            print(f"Cannot fetch tables: No valid soup object for URL {self.url}")
            return None
            
        teams, xpaths = self._get_team_xpaths()
        
        if not teams:
            print(f"No teams found for URL {self.url}")
            return None

        # Extract date from URL for file organization
        date_part = self.url.split('/')[-1][:8]
        year, month, day = date_part[:4], date_part[4:6], date_part[6:8]

        # Create directory structure
        year_path = os.path.join(base_path, year)
        month_path = os.path.join(year_path, month)
        day_path = os.path.join(month_path, day)
        os.makedirs(day_path, exist_ok=True)

        # Initialize empty DataFrame for combined data
        combined_df = pd.DataFrame()
        
        # Initialize dictionaries to store period points for all players
        # These will be used to add the new columns to the final DataFrame
        q1_points = {}  # Dictionary for Q1 points
        q2_points = {}  # Dictionary for Q2 points
        q3_points = {}  # Dictionary for Q3 points
        q4_points = {}  # Dictionary for Q4 points
        h1_points = {}  # Dictionary for H1 points
        h2_points = {}  # Dictionary for H2 points

        # Process each team's data
        for team, xpath in zip(teams, xpaths):
            css_selector = xpath.replace('//*[@id="', '#').replace('"]', '')
            table = self.soup.select_one(css_selector)

            if table:
                try:
                    # Extract full game stats (original code)
                    df = pd.read_html(str(table), header=[0, 1])[0]

                    df.columns = ['Names'] + [col[1] for col in df.columns[1:]]
                    df.drop(columns=['ORB', 'DRB', 'GmSc'], inplace=True, errors='ignore')
                    df = df[~df['Names'].str.contains("Reserves", na=False)]
                    df = df[~df['MP'].str.contains("Did Not Play", na=False)]

                    # Insert team abbreviation
                    df.insert(0, 'Teams', team)
                    
                    # Extract quarter and half points for this team using the new helper function
                    # For each period, get a dictionary mapping player names to points
                    team_q1_points = self._extract_points_from_period(team, 'q', 1)  # Q1 points
                    team_q2_points = self._extract_points_from_period(team, 'q', 2)  # Q2 points
                    team_q3_points = self._extract_points_from_period(team, 'q', 3)  # Q3 points
                    team_q4_points = self._extract_points_from_period(team, 'q', 4)  # Q4 points
                    team_h1_points = self._extract_points_from_period(team, 'h', 1)  # H1 points
                    team_h2_points = self._extract_points_from_period(team, 'h', 2)  # H2 points
                    
                    # Update the combined dictionaries with this team's data
                    # Use team as prefix to ensure unique keys across teams (prevents player name collisions)
                    for player in df['Names']:
                        player_key = f"{team}_{player}"  # Create unique key for each player
                        # Store points in dictionaries with default value of 0 if not found
                        q1_points[player_key] = team_q1_points.get(player, 0)
                        q2_points[player_key] = team_q2_points.get(player, 0)
                        q3_points[player_key] = team_q3_points.get(player, 0)
                        q4_points[player_key] = team_q4_points.get(player, 0)
                        h1_points[player_key] = team_h1_points.get(player, 0)
                        h2_points[player_key] = team_h2_points.get(player, 0)

                    # Add to combined DataFrame
                    combined_df = pd.concat([combined_df, df], ignore_index=True)
                except Exception as e:
                    print(f"Error processing team {team}: {str(e)}")
            else:
                print(f"Table not found for {css_selector}.")

        if combined_df.empty:
            print(f"No data extracted for URL {self.url}")
            return None

        # Extract game ID components for future joins with odds data
        home_team = self.url.split('/')[-1][-8:-5]  # Extract home team from URL
        away_team = [team for team in teams if team != home_team][0] if len(teams) > 1 else "Unknown"  # Find away team
        game_date = f"{year}-{month}-{day}"  # Format date as YYYY-MM-DD
        game_id = f"{away_team}_{home_team}_{year}{month}{day}"  # Create unique game ID
        
        # Add game identifier columns for future joins with odds data
        # Note: These will be moved to the beginning of the DataFrame later
        combined_df['game_id'] = game_id
        combined_df['date'] = game_date
        
        # Add quarter and half points columns (Option 1 approach)
        # Initialize with zeros to handle missing data
        combined_df['PTS_Q1'] = 0
        combined_df['PTS_Q2'] = 0
        combined_df['PTS_Q3'] = 0
        combined_df['PTS_Q4'] = 0
        combined_df['PTS_H1'] = 0
        combined_df['PTS_H2'] = 0
        
        # Fill in the period points data for each player
        for idx, row in combined_df.iterrows():
            team = row['Teams']
            player = row['Names']
            player_key = f"{team}_{player}"  # Recreate the unique key
            
            # Set period points from our collected dictionaries
            combined_df.at[idx, 'PTS_Q1'] = q1_points.get(player_key, 0)
            combined_df.at[idx, 'PTS_Q2'] = q2_points.get(player_key, 0)
            combined_df.at[idx, 'PTS_Q3'] = q3_points.get(player_key, 0)
            combined_df.at[idx, 'PTS_Q4'] = q4_points.get(player_key, 0)
            combined_df.at[idx, 'PTS_H1'] = h1_points.get(player_key, 0)
            combined_df.at[idx, 'PTS_H2'] = h2_points.get(player_key, 0)
            
            # Data consistency check: Validate half points against quarter points
            # If half points are missing but quarter points are available, calculate them
            if combined_df.at[idx, 'PTS_H1'] == 0 and (combined_df.at[idx, 'PTS_Q1'] > 0 or combined_df.at[idx, 'PTS_Q2'] > 0):
                combined_df.at[idx, 'PTS_H1'] = combined_df.at[idx, 'PTS_Q1'] + combined_df.at[idx, 'PTS_Q2']
                
            if combined_df.at[idx, 'PTS_H2'] == 0 and (combined_df.at[idx, 'PTS_Q3'] > 0 or combined_df.at[idx, 'PTS_Q4'] > 0):
                combined_df.at[idx, 'PTS_H2'] = combined_df.at[idx, 'PTS_Q3'] + combined_df.at[idx, 'PTS_Q4']
        
        # Reorder columns to move game_id and date to the beginning
        # First get all column names
        cols = combined_df.columns.tolist()
        # Remove game_id and date from their current positions
        cols.remove('game_id')
        cols.remove('date')
        # Add them at the beginning
        cols = ['game_id', 'date'] + cols
        # Reorder the DataFrame
        combined_df = combined_df[cols]

        # Save the enhanced DataFrame to parquet
        filename = f"{away_team} @ {home_team}.parquet"
        file_path = os.path.join(day_path, filename)

        combined_df.to_parquet(file_path)
        print(f"Combined data with quarter and half stats saved to '{file_path}'.")

        # Return the DataFrame for inspection or further processing
        return combined_df


def load_game_links(json_file):
    """Load boxscore links from the Game Links JSON file."""
    with open(json_file, 'r') as f:
        game_links_dict = json.load(f)
    
    # Extract all boxscore links (values) from the dictionary
    all_boxscore_links = []
    for month_links in game_links_dict.values():
        all_boxscore_links.extend(month_links)
    
    return all_boxscore_links


def process_boxscore_links(links, output_path, max_retries=3, retry_delay=5, block_pause=43200):  # 12 hours = 43200 seconds
    """
    Process a list of boxscore links, with retry logic and pause mechanism for scraping blocks.
    
    Args:
        links: List of boxscore URLs to process
        output_path: Base path for saving output files
        max_retries: Maximum number of retry attempts per URL
        retry_delay: Delay in seconds between retry attempts
        block_pause: Pause duration in seconds when a scraping block is detected
    """
    # Create a log file to track progress
    log_file = os.path.join(os.path.dirname(output_path), "scraping_log.txt")
    
    # Track processed URLs to avoid duplicates
    processed_urls = set()
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            for line in f:
                if "Successfully processed:" in line:
                    url = line.split("Successfully processed:")[1].strip()
                    processed_urls.add(url)
    
    # Initialize counters
    total_links = len(links)
    processed_count = len(processed_urls)
    failed_count = 0
    block_count = 0
    
    print(f"Starting to process {total_links} boxscore links. {processed_count} already processed.")
    
    # Process each link
    for i, url in enumerate(links):
        # Skip if already processed
        if url in processed_urls:
            print(f"Skipping already processed URL ({i+1}/{total_links}): {url}")
            continue
        
        print(f"Processing URL ({i+1}/{total_links}): {url}")
        
        # Try to process the URL with retries
        success = False
        for attempt in range(max_retries):
            try:
                # Create TableFetch instance and process the URL
                table_fetcher = TableFetch(url)
                if table_fetcher.soup is None:
                    print(f"Failed to fetch URL (attempt {attempt+1}/{max_retries}): {url}")
                    time.sleep(retry_delay)
                    continue
                
                result = table_fetcher.fetch_and_save_tables(output_path)
                
                if result is not None:
                    # Successfully processed
                    with open(log_file, 'a') as f:
                        f.write(f"{datetime.now()}: Successfully processed: {url}\n")
                    processed_urls.add(url)
                    processed_count += 1
                    success = True
                    break
                else:
                    print(f"No data extracted (attempt {attempt+1}/{max_retries}): {url}")
            except Exception as e:
                error_msg = str(e).lower()
                # Check if this might be a scraping block
                if "403" in error_msg or "forbidden" in error_msg or "blocked" in error_msg or "too many requests" in error_msg:
                    block_count += 1
                    with open(log_file, 'a') as f:
                        f.write(f"{datetime.now()}: Possible scraping block detected: {url} - {str(e)}\n")
                    
                    if block_count >= 3:  # If we detect multiple blocks in succession
                        print(f"Multiple scraping blocks detected. Pausing for {block_pause/3600} hours...")
                        with open(log_file, 'a') as f:
                            f.write(f"{datetime.now()}: Pausing for {block_pause/3600} hours due to multiple blocks\n")
                        
                        # Calculate resume time for user information
                        resume_time = datetime.now() + timedelta(seconds=block_pause)
                        print(f"Will resume at approximately: {resume_time}")
                        
                        time.sleep(block_pause)
                        block_count = 0  # Reset block counter after pause
                        
                        # Try this URL again after the pause
                        continue
                else:
                    print(f"Error processing URL (attempt {attempt+1}/{max_retries}): {url} - {str(e)}")
                
                time.sleep(retry_delay)
        
        if not success:
            failed_count += 1
            with open(log_file, 'a') as f:
                f.write(f"{datetime.now()}: Failed after {max_retries} attempts: {url}\n")
        
        # Add a small delay between requests to avoid overloading the server
        time.sleep(2)
        
        # Print progress update
        print(f"Progress: {processed_count}/{total_links} processed, {failed_count} failed")
        
        # Save progress summary
        with open(log_file, 'a') as f:
            f.write(f"{datetime.now()}: Progress summary - {processed_count}/{total_links} processed, {failed_count} failed\n")
    
    # Final summary
    print(f"Completed processing {total_links} boxscore links.")
    print(f"Successfully processed: {processed_count}")
    print(f"Failed: {failed_count}")
    
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now()}: Completed processing all links. Success: {processed_count}, Failed: {failed_count}\n")


if __name__ == "__main__":
    # Define paths - FIXED: Updated path for Game Links.json
    game_links_file = "/Users/p/Desktop/Projects/arb/arb/data/input/Game Links.json"
    output_path = "/Users/p/Desktop/Projects/arb/arb/data/output"
    
    # Check if the files exist
    if not os.path.exists(game_links_file):
        print(f"Error: Game Links file not found at {game_links_file}")
        sys.exit(1)
        
    if not os.path.exists(output_path):
        print(f"Warning: Output path {output_path} does not exist. Creating it now.")
        os.makedirs(output_path, exist_ok=True)
    
    # Load boxscore links
    print(f"Loading boxscore links from {game_links_file}")
    boxscore_links = load_game_links(game_links_file)
    print(f"Loaded {len(boxscore_links)} boxscore links")
    
    # Process the links
    process_boxscore_links(boxscore_links, output_path)
