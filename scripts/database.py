import os

def create_folder_structure(base_path, date_game_list):
    """
    Create a nested folder structure within the 'data' directory based on a list of date_game entries.
    Each entry is in the format 'yyyy/mm/dd/xxx' where 'xxx' is the game ID.
    """
    for date_game in date_game_list:
        year, month, day, game_id = date_game.split('/')
        # Construct the path for the current date_game entry within the 'data' directory
        path = os.path.join(base_path, 'DB', year, month, day, game_id)
        # Create the directory if it does not exist
        os.makedirs(path, exist_ok=True)
        print(f"Created folder: {path}")

# Example usage
if __name__ == "__main__":
    # Define the root directory of your repository where the 'data' folder exists
    root_directory = "/Users/p/Desktop/Projects/arb/arb/data"  # Adjust this path to your actual repository path
    
    # List of date_game entries
    date_games = [
        '2025/03/15/abc123',
        '2025/03/15/def456',
        '2025/03/16/xyz789',
        '2024/12/24/zzz000',
        '2024/12/25/aaa111',
        '2023/01/01/bbb222',
        '2023/02/02/ccc333',
        '2023/02/02/ddd444',
        '2025/01/01/eee555',
        '2025/12/31/fff666'
    ]
    
    # Create the folder structure within the 'data' folder
    create_folder_structure(root_directory, date_games)
