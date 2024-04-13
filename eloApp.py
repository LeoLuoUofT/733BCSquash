import pandas as pd
import re
from flask import Flask, request, render_template, g, redirect, url_for
import os
from werkzeug.utils import secure_filename
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score


def extract_all_scores(game_score):
    # Define regular expression to match scores in the format "n-n"
    score_pattern = re.compile(r"(\d+)-(\d+)")

    # Find all matches of score pattern in the game score
    matches = score_pattern.findall(game_score)

    if matches:
        # Extract all scores
        scores = [(int(score_a), int(score_b)) for score_a, score_b in matches]
        return scores
    else:
        return None  # No valid scores found


def expected_win_probability_norm(player_elo, opponent_elo):
    return 1 / (1 + 10 ** ((opponent_elo - player_elo) / 1.2))


def check_res(name,df):
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
        scores = extract_all_scores(str(game_score))
        for score in scores:
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


def elo_sys_with_event_normalized(elo_ratings, df):
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
        scores = extract_all_scores(str(game_score))

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
        for score in scores:
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


def generate_match_outcomes(df):
    # Initialize list to store match outcomes
    match_outcomes = []

    # Iterate through each row (match) in the DataFrame
    for index, row in df.iterrows():
        # Extract match details
        game_score = row["Game Scores"]
        scores = extract_all_scores(str(game_score))

        # Initialize counters for wins of each player
        wins_player_a = 0
        wins_player_b = 0

        # Count wins for each player
        if scores:
            for score_a, score_b in scores:
                if score_a > score_b:
                    wins_player_a += 1
                elif score_a < score_b:
                    wins_player_b += 1

        # Determine the match outcome based on wins
        if wins_player_a > wins_player_b:
            match_outcomes.append(1)  # Player A wins
        elif wins_player_a < wins_player_b:
            match_outcomes.append(0)  # Player B wins
        else:
            match_outcomes.append(None)  # Draw

    # Add match outcomes as a new column to the DataFrame
    df["Match Outcome"] = match_outcomes

    return df

def train_ml_model(df):
    # Prepare the features (Elo ratings) and target variable (match outcomes)
    features = df[
        [
            "Player A1 Elo Rating",
            "Player A2 Elo Rating",
            "Player B1 Elo Rating",
            "Player B2 Elo Rating",
        ]
    ]
    target = df["Match Outcome"]

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=44
    )

    # Train the logistic regression model
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)

    return model, accuracy, precision, recall


def find_elo_ratings(players_df, player_names):
    # Initialize Elo ratings dictionary
    elo_ratings = {}

    # Find Elo ratings for each player
    for name in player_names:
        player_info = players_df[players_df["Player"] == name]
        elo_ratings[name] = (
            player_info["Elo"].values[0] if not player_info.empty else None
        )


    # Create DataFrame with Elo ratings for the given players
    elo_df = pd.DataFrame(
        [list(elo_ratings.values())],
        columns=[
            "Player A1 Elo Rating",
            "Player A2 Elo Rating",
            "Player B1 Elo Rating",
            "Player B2 Elo Rating",
        ],
    )
    print(elo_df)
    return elo_df


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"csv"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

ALLOWED_EXTENSIONS = {"csv"}

app.config["UPLOAD_FOLDER"] = "uploads"

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return render_template("upload.html", error="No file part")
        file = request.files["file"]
        if file.filename == "":
            return render_template("upload.html", error="No selected file")
        if file and allowed_file(file.filename):
            df = pd.read_csv(file)

            # Remove entries where the "Game Scores" column is NaN
            df = df.dropna(subset=["Game Scores"])

            df["Match Date"] = pd.to_datetime(df["Match Date"])
            df = df.sort_values(by="Match Date")
            df = generate_match_outcomes(df)
            app.df = df  # Save the DataFrame in the Flask application context
            elo_ratings_event = (
        {}
            )  # Assuming elo_sys_with_event_normalized is defined elsewhere
            elo_ratings_event = elo_sys_with_event_normalized(elo_ratings_event, df)

            sorted_elo_ratings_event = sorted(
                elo_ratings_event.items(), key=lambda x: x[1], reverse=True
            )

            player_stats = []
            for player, elo in sorted_elo_ratings_event:
                (
                    wins,
                    losses,
                    league_wins,
                    league_losses,
                    championship_wins,
                    championship_losses,
                ) = check_res(player, df)
                player_stats.append(
                    (player, elo, wins, losses, championship_wins, championship_losses)
                )

            # Create DataFrame for players
            columns = [
                "Player",
                "Elo",
                "Wins",
                "Losses",
                "Championship Wins",
                "Championship Losses",
            ]
            app.players_df = pd.DataFrame(player_stats, columns=columns)

            app.players_df["Rank"] = (
                app.players_df["Elo"].rank(ascending=False).astype(int)
            )
            return redirect(url_for("display_players"))
        else:
            return render_template("upload.html", error="File type not allowed")
    return render_template("upload.html")


@app.route("/display", methods=["GET", "POST"])
def display_players():
    if hasattr(app, "players_df"):
        top_players_count = int(request.form.get("top_players_count", 10))
        search_name = request.form.get("search_name", "")  # Get the search query
        top_players = app.players_df.sort_values(by="Elo", ascending=False)

        if search_name:
            # Filter players by search query
            top_players = top_players[
                top_players["Player"].str.contains(search_name, case=False)
            ]

        top_players = top_players.head(top_players_count)

        return render_template(
            "display.html",
            table_data=top_players.values,
            top_players_count=top_players_count,
            search_name=search_name,
        )
    else:
        return redirect(url_for("upload_file"))


@app.route("/predict", methods=["GET", "POST"])
def predict():
    if hasattr(app, "players_df"):
        if request.method == "POST":
            if request.form["action"] == "create_predictor":
                # Create the ML predictor
                model, accuracy, precision, recall = train_ml_model(
                    app.df
                )  # Assuming df is your DataFrame

                app.model = model
                app.accuracy = accuracy
                app.precision = precision
                app.recall = recall
                return render_template(
                    "predict.html",
                    message="ML predictor created successfully!",
                    accuracy=app.accuracy,
                    precision=app.precision,
                    recall=app.recall,
                )
            elif request.form["action"] == "predict_match":
                # Predict match outcome
                player_A1 = request.form["player_A1"]
                player_A2 = request.form["player_A2"]
                player_B1 = request.form["player_B1"]
                player_B2 = request.form["player_B2"]
                # Use the trained model to predict match outcome

                try:
                    temp_df = find_elo_ratings(
                        app.players_df, (player_A1, player_A2, player_B1, player_B2)
                    )
                    match_outcome = app.model.predict(temp_df)[0]
                    if match_outcome == 1:
                        match_percentage = app.model.predict_proba(temp_df)[0][0] * 100
                        match_outcome = f"Team A, consisting of {player_A1} and {player_A2}, Win"
                    else:
                        match_percentage = app.model.predict_proba(temp_df)[0][1] * 100
                        match_outcome = f"Team B, consisting of {player_B1} and {player_B2}, Win"
                    return render_template(
                        "predict.html",
                        message="Match outcome predicted successfully!",
                        player_A1=player_A1,
                        player_A2=player_A2,
                        player_B1=player_B1,
                        player_B2=player_B2,
                        accuracy=app.accuracy,
                        precision=app.precision,
                        recall=app.recall,
                        match_outcome=match_outcome,
                        winning_percentage=match_percentage,
                    )
                except Exception as e:
                    try:
                        print(e)
                        return render_template(
                            "predict.html",
                            error_message="Names entered incorrectly.",
                            player_A1=player_A1,
                            player_A2=player_A2,
                            player_B1=player_B1,
                            player_B2=player_B2,
                            accuracy=app.accuracy,
                            precision=app.precision,
                            recall=app.recall,
                        )
                    except Exception as e: 
                        print(e)
                        return render_template(
                            "predict.html",
                            error_message="Please create a model first.",
                            player_A1=player_A1,
                            player_A2=player_A2,
                            player_B1=player_B1,
                            player_B2=player_B2,
                        )
        return render_template("predict.html")
    else:
        return redirect(url_for("upload_file"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
