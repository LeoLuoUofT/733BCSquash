import pandas as pd
import ast

def preprocess(input_file_path):
    df = pd.read_csv(input_file_path)
    # Remove entries where the "Game Scores" column is NaN
    df = df.dropna(subset=["Game Scores"])
    df["Match Date"] = pd.to_datetime(df["Match Date"])
    df = df.sort_values(by="Match Date")
    df = df[
        [
            "Match Date",
            "Event Name",
            "Game Scores",
            "Player A1",
            "Player A2",
            "Player B1",
            "Player B2",
        ]
    ]
    df["Game Scores"] = df["Game Scores"].apply(ast.literal_eval)
    
    return df

# Function to calculate expected win probability based on Elo ratings
def expected_win_probability(player_elo, opponent_elo):
    return 1 / (1 + 10 ** ((opponent_elo - player_elo) / 400))

# Function to calculate expected win probability based on Elo ratings
def expected_win_probability_norm(player_elo, opponent_elo):
    return 1 / (1 + 10 ** ((opponent_elo - player_elo) / 1.2))

def elo_sys_with_scorefactor_and_dynamic_k(df, elo_ratings):
    # Initialize parameters for the Elo system
    starting_elo = 1200  # Starting Elo rating for new players
    
    # Function to calculate K-factor based on Elo rating
    def calculate_k_factor(elo_rating):
        if elo_rating < 2000:
            return 30
        elif elo_rating < 2400:
            return 20
        else:
            return 10

    # Iterate through each row (match) in the DataFrame
    for index, row in df.iterrows():
        # Extract match details
        game_score = row["Game Scores"]
        for score in game_score:
            score_a = score[0]
            score_b = score[1]

            # Extract player names
            player_a1 = row["Player A1"]
            player_a2 = row["Player A2"]
            player_b1 = row["Player B1"]
            player_b2 = row["Player B2"]

            # Initialize Elo ratings for new players
            for player in [player_a1, player_a2, player_b1, player_b2]:
                if player not in elo_ratings:
                    elo_ratings[player] = starting_elo

            # Calculate expected win probability for each team
            team_a_elo = (elo_ratings[player_a1] + elo_ratings[player_a2]) / 2
            team_b_elo = (elo_ratings[player_b1] + elo_ratings[player_b2]) / 2
            expected_win_a = expected_win_probability(team_a_elo, team_b_elo)
            expected_win_b = 1 - expected_win_a

            # Update Elo ratings based on actual outcome
            k_factor_a = calculate_k_factor(team_a_elo)
            k_factor_b = calculate_k_factor(team_b_elo)

            # Determine the score difference factor
            score_difference = abs(score_a - score_b)
            score_factor = 1 + (score_difference / 3)  # Adjust this factor as needed

            if score_a > score_b:
                # Team A won
                elo_ratings[player_a1] += k_factor_a * score_factor * (1 - expected_win_a)
                elo_ratings[player_a2] += k_factor_a * score_factor * (1 - expected_win_a)
                elo_ratings[player_b1] += k_factor_b * score_factor * (0 - expected_win_b)
                elo_ratings[player_b2] += k_factor_b * score_factor * (0 - expected_win_b)
            elif score_a < score_b:
                # Team B won
                elo_ratings[player_a1] += k_factor_a * score_factor * (0 - expected_win_a)
                elo_ratings[player_a2] += k_factor_a * score_factor * (0 - expected_win_a)
                elo_ratings[player_b1] += k_factor_b * score_factor * (1 - expected_win_b)
                elo_ratings[player_b2] += k_factor_b * score_factor * (1 - expected_win_b)
            else:
                # Draw
                pass
    return elo_ratings

def elo_sys_baseline(df, elo_ratings):
    # Initialize parameters for the Elo system
    starting_elo = 1200  # Starting Elo rating for new players

    # Iterate through each row (match) in the DataFrame
    for index, row in df.iterrows():
        # Extract match details
        # Extract match details
        # Extract match details
        game_score = row["Game Scores"]
        for score in game_score:
            score_a = score[0]
            score_b = score[1]

            # Extract player names
            player_a1 = row["Player A1"]
            player_a2 = row["Player A2"]
            player_b1 = row["Player B1"]
            player_b2 = row["Player B2"]

            # Initialize Elo ratings for new players
            for player in [player_a1, player_a2, player_b1, player_b2]:
                if player not in elo_ratings:
                    elo_ratings[player] = starting_elo

            # Calculate expected win probability for each team
            team_a_elo = (elo_ratings[player_a1] + elo_ratings[player_a2]) / 2
            team_b_elo = (elo_ratings[player_b1] + elo_ratings[player_b2]) / 2
            expected_win_a = expected_win_probability(team_a_elo, team_b_elo)
            expected_win_b = 1 - expected_win_a

            # Update Elo ratings based on actual outcome
            k_factor_a = 32
            k_factor_b = 32

            if score_a > score_b:
                # Team A won
                elo_ratings[player_a1] += k_factor_a * (1 - expected_win_a)
                elo_ratings[player_a2] += k_factor_a * (1 - expected_win_a)
                elo_ratings[player_b1] += k_factor_b  * (0 - expected_win_b)
                elo_ratings[player_b2] += k_factor_b  * (0 - expected_win_b)
            elif score_a < score_b:
                # Team B won
                elo_ratings[player_a1] += k_factor_a * (0 - expected_win_a)
                elo_ratings[player_a2] += k_factor_a * (0 - expected_win_a)
                elo_ratings[player_b1] += k_factor_b * (1 - expected_win_b)
                elo_ratings[player_b2] += k_factor_b * (1 - expected_win_b)
            else:
                # Draw
                pass
    return elo_ratings

def elo_sys_with_scorefactor_and_dynamic_k_normalized(df, elo_ratings):
    # Initialize parameters for the Elo system
    starting_elo = 1.5  # Starting Elo rating for new players

    # Function to calculate K-factor based on Elo rating
    def calculate_k_factor(elo_rating):
        if elo_rating < 2000:
            return 0.5
        elif elo_rating < 2400:
            return 0.2
        else:
            return 0.1

    # Iterate through each row (match) in the DataFrame
    for index, row in df.iterrows():
        # Extract match details
        game_score = row["Game Scores"]
        for score in game_score:
            score_a = score[0]
            score_b = score[1]

            # Extract player names
            player_a1 = row["Player A1"]
            player_a2 = row["Player A2"]
            player_b1 = row["Player B1"]
            player_b2 = row["Player B2"]

            # Initialize Elo ratings for new players
            for player in [player_a1, player_a2, player_b1, player_b2]:
                if player not in elo_ratings:
                    elo_ratings[player] = starting_elo

            # Calculate expected win probability for each team
            team_a_elo = (elo_ratings[player_a1] + elo_ratings[player_a2]) / 2
            team_b_elo = (elo_ratings[player_b1] + elo_ratings[player_b2]) / 2
            expected_win_a = expected_win_probability_norm(team_a_elo, team_b_elo)
            expected_win_b = 1 - expected_win_a

            # Update Elo ratings based on actual outcome
            k_factor_a = calculate_k_factor(team_a_elo)
            k_factor_b = calculate_k_factor(team_b_elo)

            # Determine the score difference factor
            score_difference = abs(score_a - score_b)
            score_factor = 1 + (score_difference / 3)  # Adjust this factor as needed

            if score_a > score_b:
                # Team A won
                elo_ratings[player_a1] += k_factor_a * score_factor * (1 - expected_win_a)
                elo_ratings[player_a2] += k_factor_a * score_factor * (1 - expected_win_a)
                elo_ratings[player_b1] += k_factor_b * score_factor * (0 - expected_win_b)
                elo_ratings[player_b2] += k_factor_b * score_factor * (0 - expected_win_b)
            elif score_a < score_b:
                # Team B won
                elo_ratings[player_a1] += k_factor_a * score_factor * (0 - expected_win_a)
                elo_ratings[player_a2] += k_factor_a * score_factor * (0 - expected_win_a)
                elo_ratings[player_b1] += k_factor_b * score_factor * (1 - expected_win_b)
                elo_ratings[player_b2] += k_factor_b * score_factor * (1 - expected_win_b)
            else:
                # Draw
                pass
    return elo_ratings

def check_res(df, name):
    # Initialize win and loss counters
    wins = 0
    losses = 0
    league_wins = 0
    league_losses = 0
    championship_wins = 0
    championship_losses = 0

    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        # Extract match details
        game_score = row["Game Scores"]
        for score in game_score:
            score_a, score_b = score

            # Extract player names (assuming the capitalization of 'p' in 'Player')
            player_a1 = row["Player A1"]
            player_a2 = row["Player A2"]
            player_b1 = row["Player B1"]
            player_b2 = row["Player B2"]

            # Check if player is part of the winning team
            if name in [player_a1, player_a2] and score_a > score_b:
                wins += 1
                # Check if the event name contains "League" or "Championships"
                if "League" in row["Event Name"]:
                    league_wins += 1
                elif "Championships" in row["Event Name"]:
                    championship_wins += 1
            elif name in [player_b1, player_b2] and score_b > score_a:
                wins += 1
                # Check if the event name contains "League" or "Championships"
                if "League" in row["Event Name"]:
                    league_wins += 1
                elif "Championships" in row["Event Name"]:
                    championship_wins += 1
            elif name in [player_a1, player_a2] or name in [player_b1, player_b2]:
                losses += 1
                # Check if the event name contains "League" or "Championships"
                if "League" in row["Event Name"]:
                    league_losses += 1
                elif "Championships" in row["Event Name"]:
                    championship_losses += 1

    return (
        wins,
        losses,
        league_wins,
        league_losses,
        championship_wins,
        championship_losses,
    )

def elo_sys_with_event_normalized(df, elo_ratings):
    # Initialize parameters for the Elo system
    starting_elo = 1.5  # Starting Elo rating for new players

    # Function to calculate K-factor based on Elo rating
    def calculate_k_factor(elo_rating):
        if elo_rating < 2000:
            return 0.5
        elif elo_rating < 2400:
            return 0.2
        else:
            return 0.1

    # Iterate through each row (match) in the DataFrame
    for index, row in df.iterrows():
        # Extract match details
        game_score = row["Game Scores"]

        # Extract player names
        player_a1 = row["Player A1"]
        player_a2 = row["Player A2"]
        player_b1 = row["Player B1"]
        player_b2 = row["Player B2"]
    
    
        # Initialize Elo ratings for new players
        for player in [player_a1, player_a2, player_b1, player_b2]:
            if player not in elo_ratings:
                elo_ratings[player] = starting_elo

        df.at[index, "Player A1 Elo Rating"] = elo_ratings[player_a1]
        df.at[index, "Player A2 Elo Rating"] = elo_ratings[player_a2]
        df.at[index, "Player B1 Elo Rating"] = elo_ratings[player_b1]
        df.at[index, "Player B2 Elo Rating"] = elo_ratings[player_b2]
        for score in game_score:
            score_a = score[0]
            score_b = score[1]

            # Calculate expected win probability for each team
            team_a_elo = (elo_ratings[player_a1] + elo_ratings[player_a2]) / 2
            team_b_elo = (elo_ratings[player_b1] + elo_ratings[player_b2]) / 2
            expected_win_a = expected_win_probability_norm(team_a_elo, team_b_elo)
            expected_win_b = 1 - expected_win_a

            # Update Elo ratings based on actual outcome
            k_factor_a = calculate_k_factor(team_a_elo)
            k_factor_b = calculate_k_factor(team_b_elo)

            # Determine the score difference factor
            score_difference = abs(score_a - score_b)
            score_factor = 1 + (score_difference / 3)  # Adjust this factor as needed

            # Check if the event name contains "League" or "Championships"
            event_name = row["Event Name"]
            if "League" in event_name:
                score_factor *= 1.5
            elif "Tournament" in event_name:
                score_factor *= 2
            elif "Championships" in event_name:
                score_factor *= 5  # Weight the match by a factor of 5

            if score_a > score_b:
                # Team A won
                elo_ratings[player_a1] += (
                    k_factor_a * score_factor * (1 - expected_win_a)
                )
                elo_ratings[player_a2] += (
                    k_factor_a * score_factor * (1 - expected_win_a)
                )
                elo_ratings[player_b1] += (
                    k_factor_b * score_factor * (0 - expected_win_b)
                )
                elo_ratings[player_b2] += (
                    k_factor_b * score_factor * (0 - expected_win_b)
                )
            elif score_a < score_b:
                # Team B won
                elo_ratings[player_a1] += (
                    k_factor_a * score_factor * (0 - expected_win_a)
                )
                elo_ratings[player_a2] += (
                    k_factor_a * score_factor * (0 - expected_win_a)
                )
                elo_ratings[player_b1] += (
                    k_factor_b * score_factor * (1 - expected_win_b)
                )
                elo_ratings[player_b2] += (
                    k_factor_b * score_factor * (1 - expected_win_b)
                )
            else:
                # Draw
                pass
    return elo_ratings

def run(input_file_path):
    df = preprocess(input_file_path)
    # Initialize Elo ratings for each player
    elo_ratings = {}
    elo_ratings = elo_sys_with_scorefactor_and_dynamic_k(df, elo_ratings)
    elo_ratings_base = {}
    elo_ratings_base = elo_sys_baseline(df, elo_ratings_base)
    elo_ratings_norm = {}
    elo_ratings_norm = elo_sys_with_scorefactor_and_dynamic_k_normalized(df, elo_ratings_norm)
    elo_ratings_event = {}
    elo_ratings_event = elo_sys_with_event_normalized(df, elo_ratings_event)

    # Display or save the updated Elo ratings for each player
    sorted_elo_ratings = sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True)
    sorted_elo_ratings_base = sorted(
        elo_ratings_base.items(), key=lambda x: x[1], reverse=True
    )
    sorted_elo_ratings_norm = sorted(
        elo_ratings_norm.items(), key=lambda x: x[1], reverse=True
    )
    sorted_elo_ratings_event = sorted(
        elo_ratings_event.items(), key=lambda x: x[1], reverse=True
    )
    
    print("Top 5 Players - System: elo_sys_with_scorefactor_and_dynamic_k")
    for player, elo in sorted_elo_ratings[:5]:
        print(f"Player: {player}, Elo: {elo}")

    print("\nTop 5 Players - System: elo_sys_baseline")
    for player, elo in sorted_elo_ratings_base[:5]:
        print(f"Player: {player}, Elo: {elo}")

    print("\nTop 5 Players - System: elo_sys_with_scorefactor_and_dynamic_k_normalized")
    for player, elo in sorted_elo_ratings_norm[:5]:
        print(f"Player: {player}, Elo: {elo}")

    print("\nTop 5 Players - System: elo_sys_with_eventfactor_normalized")
    for player, elo in sorted_elo_ratings_event[:5]:
        print(f"Player: {player}, Elo: {elo}")
        
    df.to_csv("elo_rating/final_elo_rating_df.csv")
    
    pd.DataFrame(sorted_elo_ratings).to_csv("elo_rating/sorted_elo.csv")
    pd.DataFrame(sorted_elo_ratings_base).to_csv("elo_rating/sorted_elo_base.csv")
    pd.DataFrame(sorted_elo_ratings_norm).to_csv("elo_rating/sorted_elo_norm.csv")
    pd.DataFrame(sorted_elo_ratings_event).to_csv("elo_rating/sorted_elo_event.csv")