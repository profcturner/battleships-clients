# A simple Battleships Client
# See https://github.com/profcturner/battleships for more information

# Import requests to do most of the heavy lifting
import requests

# Some of the results we will get are encoded with JSON
import json

# Use some regular expressions to sanity check input
import re

# A global variable with the root of the Battleships API (from the project above)
API_BASE_URL = '<your server name here>/battleships/api/'
# A global variable to set how much debug information to print
VERBOSITY = 3

# This function is intended to do most of the work in making the API calls

def battleships_api(api_call, api_version="1.0"):
    """This function performs a call to the battleships API

    api_call        this is the call (without the version number)
                    do not add the trailing slash
    api_version     the api version, which defaults to 1.0

    it returns the output from the call."""

    # API adds the BASE URL, version number, and what is passed in
    url = f"{API_BASE_URL}{api_version}/{api_call}/"

    if VERBOSITY > 2:
        print(f"DEBUG: API call {url}")

    # Get the response
    r = requests.get(url)

    # A code of 200 usually indicates all is well
    if r.status_code != 200:
        # So if not, offer some DEBUG info if VERBOSITY is set
        if VERBOSITY > 1:
            print("DEBUG: API returned error.")
            print(f"DEBUG: {r.status_code}:{r.text}")
        # Raise an exception
        raise Exception(f"API ERROR: {r.status_code}:{r.text}")
        
    return r.text

# These functions are intended to use battleships_api to get raw data
# and return it in usable form for Python

def games_index():
    """Call the API to get the list of games"""

    # The API encodes this is JSON
    games_json = battleships_api("games/index")

    # So decode it before returning    
    games = json.loads(games_json)

    return games


def games_register(name):
    """Add a new game to the server

    name    a name with only alphabetical or numeric values"""

    secret = battleships_api(f"games/register/{name}/")

    if VERBOSITY > 2:
        print(f"DEBUG: game_register returns {secret}")

    return secret

    
def players_index():
    """Call the API to get the list of players"""

    # The API encodes this is JSON
    players_json = battleships_api("players/index")

    # So decode it before returning    
    players = json.loads(players_json)

    return players


def player_register(name):
    """Add a new player to the game

    name    a name with only alphabetical or numeric values"""

    secret = battleships_api(f"players/register/{name}/")

    if VERBOSITY > 2:
        print(f"DEBUG: player_register returns {secret}")

    return secret


def games_winner(game_name):
    """Check for a winner in a game"""

    winner = battleships_api(f"games/getwinner/{game_name}/")

    return winner



# These functions are more distant from the API and try to produce more
# human centred output


def print_games():
    """Print the list of player names only"""

    print(
        """Here is a list of current games.\n""")

    # Fetch the list of players
    games = games_index()

    for game in games:
        # Each player is a "dict" which means we can look up a value
        # For each key
        print(f"{game['name']}")


def add_game():
    """Adds a new game to the server"""

    game_name = input("Specify a name for the game: ")

    try:
        # Attempt to add the new game
        secret = games_register(game_name)

        print("Your secret for the game is {secret} which you should note.")

        return secret

    except Exception as error:
        print(f"Something went wrong: {error}")
    

def print_players():
    """Print the list of player names only"""

    print(
        """Here is a list of current players.\n""")

    # Fetch the list of players
    players = players_index()

    for player in players:
        # Each player is a "dict" which means we can look up a value
        # For each key
        print(f"{player['name']}")


def display_ships_for_player(game, player, secret):
    """Print the list of ships for the current player"""

    try:
        # Attempt to get the ships from the server
        ships_json = battleships_api(f"games/getships/{game}/{player}/{secret}")
        # Convert them from JSON
        ships = json.loads(ships_json)

        print(f"In game {game}, player {player} has {len(ships)} ships.")

        # Print the details
        for ship in ships:
            print(ship['name'])

            for location in ship['locations']:
                print(location)

    except Exception as error:
        print(f"Something went wrong: {error}")


def display_history(game_name):
    """Print the history for a game"""

    try:
        # Attempt to get the ships from the server
        actions_json = battleships_api(f"games/history/{game_name}")
        # Convert them from JSON
        actions = json.loads(actions_json)

        print(f"In game {game_name}, there have been {len(actions)} actions.")

        # Print the details
        for action in actions:
            print(f"{action['player']}: {action['location']} - {action['result']}")

    except Exception as error:
        print(f"Something went wrong: {error}")


def display_strike(game_name, player_name, location, player_secret):
    """Attempts to process a user strike and displays the outcome"""

    # Extract the x and y coordinates from the tuple so we have total control over how to print
    (x,y) = location
    try:
        result = battleships_api(f"strike/{game_name}/{player_name}/({x},{y})/{player_secret}")
        print(f"Strike attempt by {player_name} at {location}.\nResult: {result}")

    except Exception as error:
        print(f"Something went wrong: {error}")



def print_banner(player_name, game_name):
    """Print the banner

    game    if there is an active game, print its name
    player  if there is a selected player, print its name"""

    print(f"Welcome to Battleships!")
    #if GAME_NAME:
    print(f"You are playing the game: {game_name}")
    #if PLAYER_NAME:
    print(f"You are player: {player_name}")

    # Some whitespace
    print("\n\n")


def select_or_create_player():
    """Allows the user to select a player, or create a new one

    returns a tuple with (player name, player secret) or None if nothing is selected

    """

    print("List of current players:\n")
    # First of all get the players
    players = players_index()
    for x in range(0, len(players_index())):
        print(f"{x}. {players[x]['name']}")

    user_choice = input("\nEnter a number to select a player, or 'C' to create or 'Q' to quit:")

    # If the user quits
    if user_choice in ['Q', 'q']:
        return None

    if user_choice in ['C', 'c']:
        player_name = input("\nPlease enter the new player name: ")
        # Let's see if we can create this
        try:
            player_secret = player_register(player_name)
            print("\nNew user created, PLEASE NOTE the secret {player_secret}.")
            return(player_name, player_secret)
        except Exception as e:
            # It didn't go well.
            print(f"Error: {e}")
            return None

    # Ok, try to get the integer the user hopefully entered
    try:
        player_index = int(user_choice)
        player_name = players[player_index]['name']
        # But they will need to enter their secret
        player_secret = input(f"\nPlease enter the secret for your player {player_name}: ")
        return(player_name, player_secret)
    except Exception as e:
        # It didn't go well.
        print(f"Error: {e}")
        return None


def select_or_create_game():
    """Allows the user to select a game, or create a new one

    returns a tuple with (game name, game secret) or None if nothing is selected

    """

    print("List of current games:\n")
    # First of all get the games
    games = games_index()
    for x in range(0, len(games_index())):
        print(f"{x}. {games[x]['name']}")

    user_choice = input("\nEnter a number to select a game, or 'C' to create or 'Q' to quit:")

    # If the user quits
    if user_choice in ['Q', 'q']:
        return None

    if user_choice in ['C', 'c']:
        game_name = input("\nPlease enter the new game name: ")
        # Let's see if we can create this
        try:
            game_secret = game_register(game_name)
            print("\nNew game created, PLEASE NOTE the secret {game_secret}.")
            return(game_name, game_secret)
        except Exception as e:
            # It didn't go well.
            print(f"Error: {e}")
            return None

    # Ok, try to get the integer the user hopefully entered
    try:
        game_index = int(user_choice)
        game_name = games[game_index]['name']
        # But they will need to enter their secret
        game_secret = input("\nPlease enter the secret for your game (if known, enter otherwise): ")
        return(game_name, game_secret)
    except Exception as e:
        # It didn't go well.
        print(f"Error: {e}")
        return None


def add_players_to_game(game_name):
    """Allows the user to add players to a game"""

    if not game_name:
        print(f"You need to select a game first.")
        return

    print("List of current players:\n")
    # First of all get the players
    players = players_index()
    for x in range(0, len(players_index())):
        print(f"{x}. {players[x]['name']}")

    user_choice = input("\nEnter a number to select a player, or 'Q' to quit:")

    # If the user quits
    if user_choice in ['Q', 'q']:
        return

    # Ok, try to get the integer the user hopefully entered
    try:
        player_index = int(user_choice)
        player_name = players[player_index]['name']

        # Call the API
        content = battleships_api(f'games/addplayer/{game_name}/{player_name}')
        print(f"{content}")
    except Exception as e:
        # It didn't go well.
        print(f"Error: {e}")
        return


def start_game(game_name):
    """Allows the user to add players to a game"""

    if not game_name:
        print(f"You need to select a game first.")
        return

    # Ok, try to get the integer the user hopefully entered
    try:
        # Call the API
        content = battleships_api(f'games/start/{game_name}')
        print(f"{content}")
    except Exception as e:
        # It didn't go well.
        print(f"Error: {e}")
        return


def play_game_menu(game_name, player_name, player_secret):
    """Display the menu for playing a game, take user input and process choices"""

    # We need a regular expression to detect coordinates
    pattern = re.compile("\((?P<x>[0-9]+),(?P<y>[0-9]+)\)")

    if not game_name:
        print("You must select a game.")
        return
    if not player_name or not player_secret:
        print("You must select a player with a secret.")
        return

    # Keep going till we say otherwise
    quit = False
    while not quit:

        print_banner(player_name, game_name)

        print("Game mode:")
        # Check the game is still going
        winner = games_winner(game_name)
        if winner:
            print(f"Player {winner} has won the game!\nGAME OVER!!!\n\n")

        # It is, other actions
        print("Enter coordinates in brackets to strike e.g. (2,3) or:")
        print("A. To refresh action list")
        print("S. To show your ship positions")
        print("Q. To quit game mode")

        user_choice = input("Please make a selection: ")
        if user_choice in ['Q', 'q']:
            quit = True
        elif user_choice in ['S', 's']:
            display_ships_for_player(game_name, player_name, player_secret)
        elif user_choice in ['A', 'a']:
            display_history(game_name)
        elif pattern.match(user_choice):
            match = pattern.match(user_choice)
            # Convert this to a tuple, the regexp extracts the x, and y, convert them to ints
            location = (int(match['x']), int(match['y']))
            print(location)
            display_strike(game_name, player_name, location, player_secret)
        else:
            print("Invalid choice!")



def main_menu():
    """Display the main menu, take user input and process choices"""

    # When we start, we don't know much
    player_name = None
    player_secret = None
    game_name = None
    game_secret = None

    # Keep going till we say otherwise
    quit = False
    while not quit:

        print_banner(player_name, game_name)

        print("1. Select a player or create one")
        print("2. Select a game or create one")
        print("3. Add players to the selected game")
        print("4. Start the selected game")
        print("5. Play the selected game")
        print("Q. Quit")

        user_choice = input("Please enter your choice: ")
        if user_choice == '1':
            player_data = select_or_create_player()
            # If we got actual data, collect it
            if player_data:
                (player_name, player_secret) = player_data

        elif user_choice == '2':
            game_data = select_or_create_game()
            # If we got actual data, collect it
            if game_data:
                (game_name, game_secret) = game_data

        elif user_choice == '3':
            add_players_to_game(game_name)

        elif user_choice == '4':
            start_game(game_name)

        elif user_choice == '5':
            play_game_menu(game_name, player_name, player_secret)

        elif user_choice in ['Q', 'q']:
            print("Thanks for playing!")
            quit = True

        else:
            print("Invalid choice!")


def main():

     continue_game = True

     while(continue_game):
         continue_game = main_menu()

main()