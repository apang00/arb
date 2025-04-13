import requests
import json
import os
from datetime import datetime
import sys

class OddsAPI:
    def __init__(self, api_key='51eabebe6fe1969d7d918926f1292a2f'):
        self.api_key = api_key
        self.regions = 'us,us2'
        self.sport = 'basketball_nba'
        self.odds_format = 'american'
        self.date_format = 'iso'
        self.markets = (
            "h2h,h2h_h1,h2h_h2,h2h_q1,h2h_q2,h2h_q3,h2h_q4,"
            "spreads,spreads_h1,spreads_h2,spreads_q1,spreads_q2,spreads_q3,spreads_q4,"
            "totals,totals_h1,totals_h2,totals_q1,totals_q2,totals_q3,totals_q4,"
            "team_totals,team_totals_h1,team_totals_h2,team_totals_q1,team_totals_q2,team_totals_q3,team_totals_q4,"
            "player_points,player_rebounds,player_assists,player_blocks,player_steals,player_threes,player_turnovers,"
            "alternate_spreads,alternate_team_totals,"
            "player_points_assists,player_points_rebounds,player_points_rebounds_assists,player_points_assists"
        )
        # For testing in the sandbox environment
        self.output_dir = os.path.join(os.getcwd(), 'data_output')
        # Production path - uncomment this when using in the actual environment
        # self.output_dir = '/Users/p/Desktop/Projects/arb/arb/data/input'
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Store event data
        self.events = []
        
    def format_date(self, date_str=None):
        """Format the date to ISO 8601 format with T00:00:00Z timestamp."""
        if date_str:
            try:
                # Try to parse with various formats
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y', '%Y/%m/%d']:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    raise ValueError(f"Could not parse date: {date_str}")
            except Exception as e:
                print(f"Error parsing date: {e}")
                date_obj = datetime.now()
        else:
            date_obj = datetime.now()
        
        # Format to ISO 8601 with T00:00:00Z
        formatted_date = date_obj.strftime('%Y-%m-%dT00:00:00Z')
        return formatted_date
    
    def get_events(self, date_str=None):
        """Retrieve events for the given date and extract IDs and commence times."""
        formatted_date = self.format_date(date_str)
        print(f"Retrieving events for date: {formatted_date}")
        
        # API URL for sports events
        sports_url = f'https://api.the-odds-api.com/v4/historical/sports/{self.sport}/events'
        params = {
            'apiKey': self.api_key,
            'date': formatted_date
        }
        
        try:
            response = requests.get(sports_url, params=params)
            
            if response.status_code != 200:
                print(f'Failed to get events: status_code {response.status_code}, response body {response.text}')
                return []
            
            # Parse the response
            events_data = response.json()
            
            # Extract and store event data
            self.events = []
            
            # Check if the response is a list or if it has a 'data' field
            if isinstance(events_data, list):
                # Direct list of events
                event_list = events_data
            elif isinstance(events_data, dict) and 'data' in events_data:
                # Data is nested under 'data' key
                event_list = events_data['data']
            else:
                print(f"Unexpected API response format: {type(events_data)}")
                return []
            
            for event in event_list:
                self.events.append({
                    'id': event['id'],
                    'sport_key': event['sport_key'],
                    'commence_time': event['commence_time'],
                    'home_team': event.get('home_team', 'Unknown'),
                    'away_team': event.get('away_team', 'Unknown')
                })
            
            return self.events
            
        except Exception as e:
            print(f"Error retrieving events: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def display_events(self):
        """Display the events with their IDs and commence times."""
        if not self.events:
            print("No events available. Run get_events() first.")
            return
        
        print("\n=== Available Events ===")
        print(f"{'#':<3} {'ID':<34} {'Commence Time':<25} {'Teams'}")
        print("-" * 100)
        
        for i, event in enumerate(self.events, 1):
            teams = f"{event['away_team']} @ {event['home_team']}"
            print(f"{i:<3} {event['id']:<34} {event['commence_time']:<25} {teams}")
    
    def get_odds_for_event(self, event):
        """
        Get odds data for a specific event.
        """
        event_id = event['id']
        sport_key = event['sport_key']
        commence_time = event['commence_time']
        home_team = event['home_team']
        away_team = event['away_team']
        
        # Use commence_time as the DATE parameter
        date_param = commence_time
        
        print(f"\nRetrieving odds for event: {away_team} @ {home_team}")
        print(f"  ID: {event_id}")
        print(f"  Sport Key: {sport_key}")
        print(f"  Commence Time: {commence_time}")
        
        # API URL for odds
        url = f"https://api.the-odds-api.com/v4/historical/sports/{sport_key}/events/{event_id}/odds"
        params = {
            'apiKey': self.api_key,
            'regions': self.regions,
            'markets': self.markets,
            'oddsFormat': self.odds_format,
            'dateFormat': self.date_format
        }
        
        # Add date parameter if available
        if date_param:
            params['date'] = date_param
        
        try:
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                print(f'Failed to get odds: status_code {response.status_code}, response body {response.text}')
                return None
            
            # Parse the response
            odds_data = response.json()
            
            # Create filename based on teams or event ID
            if home_team != "Unknown" and away_team != "Unknown":
                filename = f"{away_team} @ {home_team}.json"
                # Remove any characters that might be problematic in filenames
                filename = filename.replace('/', '_').replace('\\', '_').replace(':', '_')
            else:
                filename = f"odds_data_{event_id}.json"
            
            # Save to file
            file_path = os.path.join(self.output_dir, filename)
            self.save_json(odds_data, file_path)
            print(f'Saved odds data to "{file_path}"')
            
            return odds_data
            
        except Exception as e:
            print(f"Error retrieving odds data: {e}")
            return None
    
    def process_all_events(self, date_str):
        """
        Process all events for the given date:
        1. Get events data
        2. For each event, get odds data
        """
        # Get events for the specified date
        events = self.get_events(date_str)
        
        if not events:
            print(f"No events found for the specified date: {date_str}")
            return
        
        # Display events for informational purposes
        self.display_events()
        
        # Process each event
        for event in events:
            self.get_odds_for_event(event)
    
    def save_json(self, data, filename):
        """Save JSON data to a file."""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

def main():
    # Create the API client
    api = OddsAPI()
    
    # Parse command line arguments
    date_str = None
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--date' and i + 1 < len(sys.argv):
            date_str = sys.argv[i + 1]
            i += 2
        else:
            # Assume it's a date if it doesn't start with --
            if not arg.startswith('--'):
                date_str = arg
            i += 1
    
    # Default date if not provided
    if not date_str:
        date_str = '2023-05-03'
    
    # Process all events for the specified date
    api.process_all_events(date_str)

if __name__ == "__main__":
    main()
