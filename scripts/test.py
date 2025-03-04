import requests

def check_if_blocked(url):
    try:
        response = requests.get(url)
        # Check if the status code indicates a successful request
        if response.status_code == 200:
            print("Access granted, not blocked.")
            # Additional checks can be added here, such as checking for the presence of specific text
            # that indicates being blocked (e.g., "Access Denied", "You have been blocked").
        else:
            print(f"Potential block detected. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        # Handle other possible exceptions (e.g., network issues)
        print(f"Error during requests to {url}: {str(e)}")

# Replace 'http://example.com' with the URL you want to test
check_if_blocked('https://www.basketball-reference.com/leagues/NBA_2015_games-october.html')
