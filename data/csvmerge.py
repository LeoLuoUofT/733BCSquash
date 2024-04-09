import pandas as pd

def merge_csv(preprocessed, temp, output):
    # Load the CSV files into pandas DataFrames
    preprocessed_data = pd.read_csv(preprocessed)
    temp_data = pd.read_csv(temp)

    # Rename columns in temp_data to match the column names in preprocessed_data
    temp_data.rename(
        columns={
            "event_name": "Event Name",
            "type": "Event Type",
            "date": "Match Date",
            "scores": "Game Scores",
            "player_a1_gender": "Player A1 Gender",
            "player_a1_name": "Player A1",
            "player_a2_gender": "Player A2 Gender",
            "player_a2_name": "Player A2",
            "player_b1_gender": "Player B1 Gender",
            "player_b1_name": "Player B1",
            "player_b2_gender": "Player B2 Gender",
            "player_b2_name": "Player B2",
        },
        inplace=True,
    )

    # Get the common columns after renaming
    shared_columns = list(set(preprocessed_data.columns) & set(temp_data.columns))

    # Concatenate the DataFrames based on the shared columns
    concatenated_data = pd.concat(
        [preprocessed_data, temp_data], ignore_index=True, sort=False, join="inner", axis=0
    )

    # Save the concatenated DataFrame to a new CSV file
    concatenated_data.to_csv(output, index=False)