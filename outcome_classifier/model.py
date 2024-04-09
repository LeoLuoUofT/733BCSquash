import pandas as pd
import numpy as np
import ast

from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


# def preprocess(input_file_path):
#     df = pd.read_csv(input_file_path)
#     # Remove entries where the "Game Scores" column is NaN
#     df = df.dropna(subset=["Game Scores"])
#     df["Match Date"] = pd.to_datetime(df["Match Date"])
#     df = df.sort_values(by="Match Date")
#     df = df[
#         [
#             "Match Date",
#             "Event Name",
#             "Game Scores",
#             "Player A1",
#             "Player A2",
#             "Player B1",
#             "Player B2",
#         ]
#     ]
#     df["Game Scores"] = df["Game Scores"].apply(ast.literal_eval)
    
#     return df


def generate_match_outcomes(df):
    # Initialize list to store match outcomes
    match_outcomes = []

    # Iterate through each row (match) in the DataFrame
    for index, row in df.iterrows():
        # Extract match details
        scores = row["Game Scores"]
#         scores = extract_all_scores(str(game_score))

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

if __name__=="__main__":
    df = pd.read_csv("elo_rating/final_elo_rating_df.csv")
    df["Game Scores"] = df["Game Scores"].apply(ast.literal_eval)
    data_with_match_outcomes = generate_match_outcomes(df)
    data_with_match_outcomes.dropna(subset=["Match Outcome"], inplace=True)
    features_log = data_with_match_outcomes[
        [
            "Player A1 Elo Rating",
            "Player A2 Elo Rating",
            "Player B1 Elo Rating",
            "Player B2 Elo Rating",
        ]
    ]
    target = data_with_match_outcomes["Match Outcome"]

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        features_log, target, test_size=0.2, random_state=42
    )

    # Train the logistic regression model
    log_model = LogisticRegression()
    log_model.fit(X_train, y_train)

    # Evaluate the model
    y_pred = log_model.predict(X_test)
    log_accuracy = accuracy_score(y_test, y_pred)
    print("Logistic regression model  accuracy:", log_accuracy)
    
    # MLP model - takes Events into account
    features_mlp = data_with_match_outcomes[
        [
            "Player A1 Elo Rating",
            "Player A2 Elo Rating",
            "Player B1 Elo Rating",
            "Player B2 Elo Rating",
            "Event Name"
        ]
    ]
    
    X_train, X_test, y_train, y_test = train_test_split(
        features_mlp, target, test_size=0.2, random_state=42
    )
    
    # Define the column transformer to one-hot encode the "Event Name" feature
    column_transformer = ColumnTransformer(
        [("onehot", OneHotEncoder(), ["Event Name"])], remainder="passthrough"
    )

    # Define the pipeline with column transformer and MLPClassifier
    mlp_pipeline = Pipeline(
        [
            ("preprocessor", column_transformer),
            (
                "classifier",
                MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42),
            ),
        ]
    )

    # Train the model
    mlp_pipeline.fit(X_train, y_train)

    # Evaluate the model
    y_pred = mlp_pipeline.predict(X_test)
    mlp_accuracy = accuracy_score(y_test, y_pred)
    print("MLP model accuracy:", mlp_accuracy)
    