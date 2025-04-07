# -----------------------------------------------
# app.py - Main Flask backend for the dashboard
# -----------------------------------------------

# 🔁 Libraries for API requests, datetime, JSON, etc.
import requests
from flask import Flask, render_template, request, jsonify
from datetime import datetime
from unidecode import unidecode
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Initialize the Flask app
app = Flask(__name__)
# -----------------------------------------------
# API Configuration - Football-Data and API-Football
# -----------------------------------------------

# Football-Data.org credentials (used for league table, team squad)
FOOTBALL_DATA_API_KEY = "ddff9ce68ffd4c2ab85d24a5785165f8"
FOOTBALL_DATA_BASE_URL = "https://api.football-data.org/v4/competitions/{league_code}/scorers"

# API-Football credentials (used for players, stats, search, comparison)
API_FOOTBALL_KEY = "9079e46b893350b5d97c8ebaa102a8d2"
API_FOOTBALL_BASE_URL = "https://v3.football.api-sports.io/players"

# Headers for both APIs
FOOTBALL_DATA_HEADERS = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}
API_FOOTBALL_HEADERS = {"x-apisports-key": API_FOOTBALL_KEY}

# League codes for dropdowns/searches
LEAGUE_CODES = {
    "PL": "Premier League",
    "BL1": "Bundesliga",
    "SA": "Serie A",
    "LL": "La Liga",
    "FL1": "Ligue 1",
    "DED": "Eredivisie",
    "PPL": "Primeira Liga",
    "CL": "Champions League",
    "EL": "Europa League",
    "WC": "World Cup",
    "EC": "European Championship",
    "MLS": "Major League Soccer",
    "BSA": "Brasileirão Serie A",
    "ARG": "Argentine Primera Division",
    "LIGA MX": "Liga MX",
    "SPL": "Scottish Premiership",
    "J1": "J1 League",
    "K1": "K League 1",
}

# Cache for faster repeat player searches
search_cache = {}

@app.route("/")
def home():
    """
    Home Page
    """
    return render_template("home.html")

@app.route("/player/<int:player_id>")
def player_profile(player_id):
    """
    Route: /player/<player_id>
    Purpose: Display detailed profile information for a specific player using the API-Football service.

    Steps:
    1. Send a GET request to the API-Football endpoint to retrieve player data for the 2024 season.
    2. If the request fails or no data is returned, render a custom error page.
    3. Extract the player's personal information and statistics from the API response.
    4. Organize the extracted data into a dictionary to pass into the template.
    5. Render the player profile template with the fetched data.
    """

    # Set request headers including API key
    headers = {"x-apisports-key": API_FOOTBALL_KEY}

    # Compose the API request URL to fetch the player info and stats for season 2024
    url = f"https://v3.football.api-sports.io/players?id={player_id}&season=2024"
    response = requests.get(url, headers=headers)

    # Handle API error by showing an error page
    if response.status_code != 200:
        return render_template("error.html", message="Failed to fetch player info")

    data = response.json()
    response_data = data.get("response", [])

    # If the player is not found, show a "Player not found" error page
    if not response_data:
        return render_template("error.html", message="Player not found")

    # Extract player and stats info from the first result
    player_info = response_data[0]["player"]
    stats = response_data[0]["statistics"][0] if response_data[0]["statistics"] else {}

    # Construct nationality flag URL
    nationality = player_info.get("nationality", "N/A")
    nationality_flag = f"https://countryflagsapi.com/png/{nationality}" if nationality else ""

    # Round rating to 1d.p.
    raw_rating = stats.get("games", {}).get("rating")
    try:
        rating = round(float(raw_rating), 1) if raw_rating else "N/A"
    except:
        rating = "N/A"

    # Prepare a dictionary of relevant data to pass to the template
    player_data = {
        "id": player_info.get("id"),
        "name": player_info.get("name"),
        "photo": player_info.get("photo"),
        "age": player_info.get("age"),
        "nationality": player_info.get("nationality"),
        "birthdate": player_info.get("birth", {}).get("date"),
        "position": stats.get("games", {}).get("position"),
        "team": stats.get("team", {}).get("name"),
        "team_logo": stats.get("team", {}).get("logo"),
        "is_on_loan": stats.get("games", {}).get("loan"),
        "injured": player_info.get("injured"),

        # Core stats
        "appearances": stats.get("games", {}).get("appearances", 0),
        "minutes": stats.get("games", {}).get("minutes", 0),
        "goals": stats.get("goals", {}).get("total"),
        "assists": stats.get("goals", {}).get("assists"),
        "yellow_cards": stats.get("cards", {}).get("yellow"),
        "red_cards": stats.get("cards", {}).get("red"),
        "rating": rating,  # already rounded earlier

        # Additional stats
        "shots": stats.get("shots", {}).get("total"),
        "shots_on_target": stats.get("shots", {}).get("on"),
        "passes": stats.get("passes", {}).get("total"),
        "key_passes": stats.get("passes", {}).get("key"),
        "tackles": stats.get("tackles", {}).get("total"),
        "interceptions": stats.get("tackles", {}).get("interceptions"),
        "dribbles_success": stats.get("dribbles", {}).get("success"),
        "dribbles_attempts": stats.get("dribbles", {}).get("attempts"),
        "fouls_drawn": stats.get("fouls", {}).get("drawn"),
    }

    # Fetch last 5-10 fixtures for the player
    team_id = stats.get("team", {}).get("id")
    fixtures_url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&season=2024&status=FT"
    fixtures_response = requests.get(fixtures_url, headers=headers)

    match_list = []

    if fixtures_response.status_code == 200:
        fixtures_data = fixtures_response.json().get("response", [])
        for fixture in fixtures_data[:10]:
            fixture_id = fixture.get("fixture", {}).get("id")
            match_date = fixture.get("fixture", {}).get("date", "")[:10]
            match_competition = fixture.get("league", {}).get("name", "Unknown League")
            home_team = fixture.get("teams", {}).get("home", {}).get("name")
            away_team = fixture.get("teams", {}).get("away", {}).get("name")
            score = fixture.get("goals", {})

            # Fetch player performance for each fixture
            player_stats_url = f"https://v3.football.api-sports.io/fixtures/players?fixture={fixture_id}"
            stats_response = requests.get(player_stats_url, headers=headers)
            player_rating = "N/A"
            goals = assists = key_passes = 0

            if stats_response.status_code == 200:
                stats_data = stats_response.json().get("response", [])
                for team in stats_data:
                    for player in team.get("players", []):
                        if player.get("player", {}).get("id") == player_id:
                            stat = player.get("statistics", [])[0]
                            player_rating = stat.get("games", {}).get("rating", "N/A")
                            goals = stat.get("goals", {}).get("total", 0)
                            assists = stat.get("goals", {}).get("assists", 0)
                            key_passes = stat.get("passes", {}).get("key", 0)

            match_list.append({
                "date": match_date,
                "competition": match_competition,
                "home_team": home_team,
                "away_team": away_team,
                "score": score,
                "rating": player_rating,
                "goals": goals,
                "assists": assists,
                "key_passes": key_passes
            })

    player_data["matches"] = match_list


    # Render the profile page and pass player data to the template
    return render_template("player_profile.html", player=player_data)

@app.route("/leaderboard")
def leaderboard():
    """
    Route: /leaderboard
    Purpose: Displays a ranked list of top players across selected leagues, positions, and stats.

    - Supports filtering by:
        • League (e.g., Premier League, La Liga, etc.)
        • Position (Attacker, Midfielder, etc.)
        • Stat (Goals, Assists, Tackles, etc.)

    The route:
    1. Collects filter selections from the user (or uses default values).
    2. Sends paginated API requests to fetch player data.
    3. Filters results by position and stat.
    4. Sorts and returns the top 11 players for rendering on the leaderboard.
    """

    # Fetch query parameters (default to all leagues, all positions, goals stat)
    selected_league = request.args.get('league', 'all')
    selected_position = request.args.get('position', 'all')
    selected_stat = request.args.get('stat', 'goals')
    season = 2024  # Current season to fetch data for

    # Supported stat mappings
    stat_fields = {
        "goals": "goals",
        "assists": "assists",
        "saves": "saves",
        "tackles": "tackles",
        "interceptions": "interceptions",
        "blocks": "blocks",
        "key_passes": "key_passes",
        "fouls_committed": "fouls_committed",
        "fouls_drawn": "fouls_drawn"
    }

    # Available leagues (ID mapped to readable name)
    leagues = {
        "all": "All Leagues",
        "39": "Premier League (ENG)",
        "140": "La Liga (ESP)",
        "135": "Serie A (ITA)",
        "78": "Bundesliga (GER)",
        "61": "Ligue 1 (FRA)",
        "2": "UEFA Champions League",
        "94": "Brazil Serie A",
        "253": "Argentina Liga",
        "262": "Saudi Pro League",
        "4": "World Cup",
        "203": "Chinese Super League",
        "384": "USA MLS",
        "88": "Portugal Primeira Liga",
        "307": "J-League (JPN)"
    }

    # Position filter options
    positions = {
        "all": "All Positions",
        "Attacker": "Attacker",
        "Midfielder": "Midfielder",
        "Defender": "Defender",
        "Goalkeeper": "Goalkeeper"
    }

    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    player_stats = []
    league_ids = list(leagues.keys()) if selected_league == "all" else [selected_league]

    # Loop through each league
    for league_id in league_ids:
        url = "https://v3.football.api-sports.io/players"
        page = 1

        while True:
            # Request players for this league and page
            params = {
                "season": season,
                "league": league_id,
                "page": page
            }
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                break

            data = response.json()
            players = data.get("response", [])
            if not players:
                break

            seen_ids = set()

            # Process each player in response
            for entry in players:
                p = entry.get("player", {})
                statistics = entry.get("statistics", [])

                # Skip if player already added or has no stats
                if not statistics or not p.get("id") or p["id"] in seen_ids:
                    continue

                seen_ids.add(p["id"])
                stats = statistics[0]
                team = stats.get("team", {})
                position = stats.get("games", {}).get("position", "Unknown")

                # Position filter logic (only add if matches)
                if selected_position != "all":
                    normalized = position.lower()
                    match = (
                        (selected_position == "Attacker" and "attacker" in normalized) or
                        (selected_position == "Midfielder" and "midfield" in normalized) or
                        (selected_position == "Defender" and "defend" in normalized) or
                        (selected_position == "Goalkeeper" and "keeper" in normalized)
                    )
                    if not match:
                        continue

                # Get stat value to rank by (based on selected stat)
                value = stats.get("goals", {}).get("total", 0) if selected_stat == "goals" else \
                        stats.get("goals", {}).get("assists", 0) if selected_stat == "assists" else \
                        stats.get("goals", {}).get("saves", 0) if selected_stat == "saves" else \
                        stats.get("tackles", {}).get("total", 0) if selected_stat == "tackles" else \
                        stats.get("tackles", {}).get("interceptions", 0) if selected_stat == "interceptions" else \
                        stats.get("tackles", {}).get("blocks", 0) if selected_stat == "blocks" else \
                        stats.get("passes", {}).get("key", 0) if selected_stat == "key_passes" else \
                        stats.get("fouls", {}).get("committed", 0) if selected_stat == "fouls_committed" else \
                        stats.get("fouls", {}).get("drawn", 0) if selected_stat == "fouls_drawn" else 0

                # Store player result
                player_stats.append({
                    "id": p["id"],
                    "name": p.get("name"),
                    "team": team.get("name"),
                    "team_logo": team.get("logo"),
                    "position": position,
                    "value": value
                })

            page += 1  # Go to next page in API pagination

    # Remove any invalid entries (e.g., missing values)
    player_stats = [p for p in player_stats if p["value"] is not None]

    # Sort by stat value, descending, keep top 11
    leaderboard = sorted(player_stats, key=lambda x: x["value"], reverse=True)[:11]

    # Render the leaderboard template with results
    return render_template("leaderboard.html",
                           leaderboard=leaderboard,
                           leagues=leagues,
                           positions=positions,
                           selected_league=selected_league,
                           selected_stat=selected_stat,
                           selected_position=selected_position)

@app.route('/league-table')
def league_table():
    """
    Route: /league-table
    Purpose: Fetches and displays the current league standings for a selected league using the Football-Data API.

    Process:
    1. Reads the selected league code from the URL query (default is 'PL' for Premier League).
    2. Sends a GET request to the Football-Data API to retrieve the standings.
    3. Parses the team data (position, name, crest, etc.) into a list of dictionaries.
    4. Renders the 'league_table.html' template with the formatted standings.
    """

    # Get selected league code from query string or use default ("PL")
    league_code = request.args.get('league', 'PL')

    # Construct API URL and headers
    url = f"https://api.football-data.org/v4/competitions/{league_code}/standings"
    headers = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}

    standings = None  # Default fallback if API fails or returns no data

    # Call the API
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        try:
            # Extract list of teams from the standings table
            standings = [
                {
                    "team_id": team['team']['id'],
                    "position": team['position'],
                    "name": team['team']['name'],
                    "crest": team['team'].get('crest'),
                    "played": team['playedGames'],
                    "won": team['won'],
                    "draw": team['draw'],
                    "lost": team['lost'],
                    "goals_for": team['goalsFor'],
                    "goals_against": team['goalsAgainst'],
                    "goal_difference": team['goalDifference'],
                    "points": team['points']
                }
                for team in data['standings'][0]['table']
            ]
        except (KeyError, IndexError) as e:
            # In case the API response format is incorrect or incomplete
            print(f"DEBUG - Error parsing standings: {e}")
            standings = None

    # If standings is still empty, return error to user
    if not standings:
        return "Error: No standings data found", 500

    # Optional debug print (safe to remove later)
    print("DEBUG - Successfully retrieved standings:", standings)

    # Render the table using template
    return render_template(
        "league_table.html",
        standings=standings,
        leagues=LEAGUE_CODES,
        selected_league=league_code
    )

@app.route('/team/<int:team_id>')
def team_squad(team_id):
    """
    Route: /team/<team_id>
    Purpose: Fetch and display the full squad list and basic team info for a specific team.

    Steps:
    1. Send a GET request to Football-Data API to retrieve the team details and player list.
    2. Parse and format team metadata (name, crest, venue, etc.).
    3. Extract each player's details including age (calculated from date of birth).
    4. Render the team_squad.html page with all the info.
    """

    # Construct API URL and authentication header
    url = f"https://api.football-data.org/v4/teams/{team_id}"
    headers = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}

    squad = []       # List to hold player data
    team_info = {}   # Dictionary to store general team info

    # Make API request
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("DEBUG - Raw API response:", data)  # Optional: can remove in production

        # Extract general team info
        team_info = {
            "id": data.get("id"),
            "name": data.get("name"),
            "crest": data.get("crest"),
            "founded": data.get("founded"),
            "venue": data.get("venue"),
        }

        # Helper function to calculate player's age from date of birth
        def calculate_age(date_of_birth):
            if date_of_birth:
                birth_date = datetime.strptime(date_of_birth, "%Y-%m-%d")
                today = datetime.today()
                return today.year - birth_date.year - (
                    (today.month, today.day) < (birth_date.month, birth_date.day)
                )
            return "N/A"

        # Extract and format each player’s data
        squad = [
            {
                "id": player.get("id"),
                "name": player.get("name"),
                "position": player.get("position"),
                "shirt_number": player.get("shirtNumber", "N/A"),
                "age": calculate_age(player.get("dateOfBirth")),
                "nationality": player.get("nationality"),
            }
            for player in data.get("squad", [])
        ]

    else:
        print(f"DEBUG - Failed to fetch squad data for team {team_id}")

    # If no squad returned, print a debug message
    if not squad:
        print("DEBUG - No squad data found!")

    # Render the squad view with team + player info
    return render_template("team_squad.html", team_info=team_info, squad=squad)

@app.route("/search")
def search():
    """
    Route: /search
    Purpose: Renders the search page UI (search.html).
    """
    return render_template("search.html")

@app.route("/search_player", methods=["GET"])
def search_player():
    """
    Searches for players across multiple seasons and leagues using API-Football.
    Returns basic player info for displaying in search results.
    """

    player_name = request.args.get("player", "").strip()
    if not player_name or player_name.lower() == "undefined":
        return jsonify({"players": []})

    if player_name in search_cache:
        return jsonify(search_cache[player_name])

    headers = {"x-apisports-key": API_FOOTBALL_KEY}

    # Most popular global leagues to include in search
    popular_leagues = [
        39, 140, 135, 78, 61, 2, 94, 88, 253, 307,
        203, 262, 1, 3, 41, 144, 25, 325, 43
    ]

    # Try multiple recent seasons to increase match chance
    seasons = ["2024", "2023", "2022"]
    search_key = unidecode(player_name.lower())

    def flag(country):
        return f"https://countryflagsapi.com/png/{country.replace(' ', '%20')}"

    unique_players = {}

    for season in seasons:
        for league_id in popular_leagues:
            url = f"https://v3.football.api-sports.io/players?search={player_name}&league={league_id}&season={season}"
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                continue

            for item in response.json().get("response", []):
                player = item.get("player", {})
                stats = item.get("statistics", [])

                player_id = player.get("id")
                if not player_id or player_id in unique_players:
                    continue

                position = "Unknown"
                if stats and stats[0].get("games"):
                    position = stats[0]["games"].get("position", "Unknown")

                unique_players[player_id] = {
                    "id": player_id,
                    "name": player.get("name", "Unknown"),
                    "age": player.get("age", "N/A"),
                    "position": position,
                    "photo": player.get("photo", ""),
                    "nationality": player.get("nationality", "N/A"),
                    "flag": flag(player.get("nationality", ""))
                }

    final_players = sorted(unique_players.values(), key=lambda x: x["name"].lower())
    result = {"players": final_players}
    search_cache[player_name] = result
    return jsonify(result)

@app.route("/compare")
def compare_page():
    """
    Route: /compare
    Purpose: Renders the player comparison page where users can search for and compare two players side-by-side.

    - Loads the compare.html template.
    - Frontend will handle dynamic search and stats rendering via JavaScript and API calls.
    """
    return render_template("compare.html")


@app.route("/api/player_stats/<int:player_id>")
def api_player_stats(player_id):
    """
    Route: /api/player_stats/<player_id>
    Purpose: Fetch detailed current season statistics for a specific player by ID.
             Used by the compare page to populate visual charts and comparisons.

    Process:
    1. Send GET request to API-Football with the player ID and 2024 season.
    2. Validate response and locate the most complete statistics block.
    3. Extract relevant fields (general, attacking, defensive, passing).
    4. Return all stats as JSON for frontend chart rendering.
    """

    # Request player data for 2024 season
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    url = f"https://v3.football.api-sports.io/players?id={player_id}&season=2024"
    response = requests.get(url, headers=headers)

    # If request fails, return error
    if response.status_code != 200:
        return jsonify({"error": "API request failed"}), 500

    # Parse response and check data
    data = response.json().get("response", [])
    if not data:
        return jsonify({"error": "Player not found"}), 404

    stats_list = data[0].get("statistics", [])
    if not stats_list:
        return jsonify({"error": "No statistics found"}), 404

    # Find best stat block for 2024
    best_stat = None
    for stat in stats_list:
        if stat.get("league", {}).get("season") == 2024 and (
                stat.get("games", {}).get("appearances") or stat.get("games", {}).get("minutes")
        ):
            best_stat = stat
            break

    if not best_stat:
        return jsonify({"error": "No valid 2024 stat block found"}), 404

    player = data[0]["player"]

    # Helper function: safely access nested stats with fallback
    def safe(d, *keys, fallback="N/A"):
        for key in keys:
            d = d.get(key, {})
        return d if isinstance(d, (int, float, str)) and d != "" else fallback

    # Precompute values for derived stats
    total_shots = safe(best_stat, "shots", "total", fallback=0)
    shots_on_target = safe(best_stat, "shots", "on", fallback=0)

    # Return player stats as JSON
    return jsonify({
        # Basic Info
        "name": player.get("name", "N/A"),
        "age": player.get("age", "N/A"),
        "photo": player.get("photo", ""),
        "position": safe(best_stat, "games", "position"),
        "nationality": player.get("nationality", "N/A"),
        "team": safe(best_stat, "team", "name"),
        "team_logo": safe(best_stat, "team", "logo"),
        "flag": f"https://countryflagsapi.com/png/{player.get('nationality', '').replace(' ', '%20')}",

        # Overview Stats
        "appearances": safe(best_stat, "games", "appearances", fallback=0),
        "minutes": safe(best_stat, "games", "minutes", fallback=0),
        "rating": safe(best_stat, "games", "rating"),

        # Attacking Stats
        "goals": safe(best_stat, "goals", "total", fallback=0),
        "assists": safe(best_stat, "goals", "assists", fallback=0),
        "shots": total_shots,
        "shots_on_target": shots_on_target,
        "shots_missed": total_shots - shots_on_target if isinstance(total_shots, (int, float)) else "N/A",
        "penalties_scored": safe(best_stat, "penalty", "scored", fallback=0),
        "penalties_missed": safe(best_stat, "penalty", "missed", fallback=0),
        "penalties_won": safe(best_stat, "penalty", "won", fallback=0),
        "penalties_committed": safe(best_stat, "penalty", "committed", fallback=0),
        "key_passes": safe(best_stat, "passes", "key", fallback=0),

        # Defensive Stats
        "tackles": safe(best_stat, "tackles", "total", fallback=0),
        "interceptions": safe(best_stat, "tackles", "interceptions", fallback=0),
        "blocks": safe(best_stat, "tackles", "blocks", fallback=0),
        "duels_total": safe(best_stat, "duels", "total", fallback=0),
        "duels_won": safe(best_stat, "duels", "won", fallback=0),

        # General / Discipline / Dribbling
        "dribbles_attempts": safe(best_stat, "dribbles", "attempts", fallback=0),
        "dribbles_success": safe(best_stat, "dribbles", "success", fallback=0),
        "fouls_committed": safe(best_stat, "fouls", "committed", fallback=0),
        "fouls_drawn": safe(best_stat, "fouls", "drawn", fallback=0),
        "yellow_cards": safe(best_stat, "cards", "yellow", fallback=0),
        "red_cards": safe(best_stat, "cards", "red", fallback=0),
        "accuracy": safe(best_stat, "passes", "accuracy"),
        "passes": safe(best_stat, "passes", "total", fallback=0),
    })


@app.route("/player/<int:player_id>/matches")
def player_match_history(player_id):
    """
    Route: /player/<player_id>/matches
    Purpose: Display the last 10 matches a player participated in during the 2024 season.
             Shows match details and contributions (goals, assists, key passes, rating).

    Steps:
    1. Fetch player info to retrieve team ID.
    2. Use team ID to retrieve all fixtures for the 2024 season.
    3. For each fixture (up to 10), request player stats from the match.
    4. If the player appeared, extract relevant stats and add to results.
    5. Return a rendered HTML page with match history data.
    """

    headers = {
        "X-RapidAPI-Key": API_FOOTBALL_KEY,
        "X-RapidAPI-Host": API_FOOTBALL_BASE_URL
    }
    season = 2024
    matches = []  # Final result list

    # Step 1: Get the player's team from their profile
    player_fixtures_url = f"https://v3.football.api-sports.io/players?id={player_id}&season={season}"
    response = requests.get(player_fixtures_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data.get("response"):
            stats = data["response"][0].get("statistics", [])

            # Loop through all teams the player played for
            for stat in stats:
                team_id = stat["team"]["id"]

                # Step 2: Get fixtures for the team
                fixtures_url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&season={season}"
                fixture_response = requests.get(fixtures_url, headers=headers)

                if fixture_response.status_code == 200:
                    fixtures = fixture_response.json().get("response", [])
                    count = 0  # Only store last 10 matches max

                    for fixture in fixtures:
                        if count >= 10:
                            break  # Stop after 10 matches

                        fixture_id = fixture["fixture"]["id"]

                        # Step 3: Get stats for this fixture
                        player_stats_url = f"https://v3.football.api-sports.io/fixtures/players?fixture={fixture_id}"
                        stat_response = requests.get(player_stats_url, headers=headers)

                        if stat_response.status_code == 200:
                            stat_data = stat_response.json().get("response", [])

                            # Step 4: Check both teams in the match for player ID
                            for team_data in stat_data:
                                for player_entry in team_data.get("players", []):
                                    if player_entry["player"]["id"] == player_id:
                                        # Step 5: Extract match and player performance data
                                        matches.append({
                                            "date": fixture["fixture"]["date"].split("T")[0],
                                            "competition": fixture["league"]["name"],
                                            "home_team": fixture["teams"]["home"]["name"],
                                            "away_team": fixture["teams"]["away"]["name"],
                                            "score": {
                                                "home": fixture["goals"]["home"],
                                                "away": fixture["goals"]["away"]
                                            },
                                            "rating": player_entry.get("statistics", [{}])[0].get("games", {}).get(
                                                "rating", "N/A"),
                                            "goals": player_entry.get("statistics", [{}])[0].get("goals", {}).get(
                                                "total", 0),
                                            "assists": player_entry.get("statistics", [{}])[0].get("goals", {}).get(
                                                "assists", 0),
                                            "key_passes": player_entry.get("statistics", [{}])[0].get("passes", {}).get(
                                                "key", 0),
                                            "position": player_entry.get("statistics", [{}])[0].get("games", {}).get(
                                                "position", "N/A")
                                        })
                                        count += 1

    return render_template("player_matches.html", matches=matches)


if __name__ == "__main__":
    app.run(debug=True)