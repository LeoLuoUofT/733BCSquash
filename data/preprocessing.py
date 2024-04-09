import pandas as pd
import numpy as np
import datetime

# Convert into array of scores
def convert_to_score_array(val):
    # Split by space and append to array
    arr = []
    if type(val) == str:
        for score in val.split(", "):
            arr.append(score)
    elif type(val) == datetime.datetime:
        arr.append(val)
    return arr

# Convert timestamp to game score
def convert_to_game_score(values):
    temp = []
    for val in values:
        if type(val) == datetime.datetime:
            val = pd.Timestamp(val)
            # Extract month and date
            month = val.month
            day = val.day
            temp.append((int(month), int(day)))
        elif type(val) == str:
            a, b = val.split("-")
            temp.append((int(a), int(b)))
            
    return temp

def preprocess(input_file_path, output_file_path):
    df = pd.read_excel(input_file_path)
    
    general_columns = ['Match Date', 'Sport', 'Event Type', 'Event Name', 'Match Status', 'Game Scores']
    player_a1_columns = ['Player A1', 'Player A1 Squash BC Number', 'Player A1 Gender']
    player_a2_columns = ['Player A2', 'Player A2 Squash BC Number', 'Player A2 Gender']
    player_b1_columns = ['Player B1', 'Player B1 Squash BC Number', 'Player B1 Gender']
    player_b2_columns = ['Player B2', 'Player B2 Squash BC Number', 'Player B2 Gender']
    columns = general_columns + player_a1_columns + player_a2_columns + player_b1_columns + player_b2_columns
    df_subset = df[columns]
    
    df_subset["Game Scores"] = df_subset["Game Scores"].apply(convert_to_score_array).apply(convert_to_game_score)
    
    # Convert "nan" genders to "unspecified"

    df_subset["Player A1 Gender"].fillna("unspecified", inplace=True)
    df_subset["Player A2 Gender"].fillna("unspecified", inplace=True)
    df_subset["Player B1 Gender"].fillna("unspecified", inplace=True)
    df_subset["Player B2 Gender"].fillna("unspecified", inplace=True)
    
    df_subset.to_csv(output_file_path, index=False)