import numpy as np
import pandas as pd
from datetime import datetime

import requests
from pymongo.mongo_client import MongoClient

CONNECTION_URI = "mongodb+srv://fayadchowdhury:733squashBC@squashbc.ss6kkda.mongodb.net/?retryWrites=true&w=majority&appName=squashbc"

def convert_to_score_array(val):
    # Split by space and append to array
    arr = []
    if type(val) == str:
        for score in val.split(", "):
            arr.append(score)
    elif type(val) == datetime.datetime:
        arr.append(val)
    return arr

def convert_to_game_score(scores):
    if len(scores) == 1: # 1 major string
        scores = scores[0]
        scores_arr = []
        if len(scores) != 0: # Empty string
            scores = scores.split(",") # scores array
            for score in scores:
                score_a, score_b = score.split("-")
                score_tuple = (int(score_a), int(score_b))
                scores_arr.append(score_tuple)
        return scores_arr
    else:
        scores_arr = []
        for score in scores:
            score_a, score_b = score.split("-")
            score_tuple = (int(score_a), int(score_b))
            scores_arr.append(score_tuple)
        return scores_arr

def preprocess_mongo_data(output_file_path):
    client = MongoClient(CONNECTION_URI)
    
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print("Error: " + str(e))
        
    players_collection = client["squashbc"]["players_aggregated"]
    players = players_collection.find()
    players_list = list(players)
    players_df = pd.DataFrame(players_list)
    
    matches_collection = client["squashbc"]["matches"]
    matches = matches_collection.find()
    matches_list = list(matches)
    matches_df = pd.DataFrame(matches_list)
    
    matches_df = matches_df.dropna(subset=["player_a1", "player_a2", "player_b1", "player_b2"])
    
    merged_df = pd.merge(matches_df, players_df, left_on=["player_a1"], right_on=["_id"], how="inner") \
                .drop(columns=["_id_x", "_id_y"]) \
                .rename(columns={
                    "ratings": "player_a1_ratings",
                    "gender": "player_a1_gender",
                    "age": "player_a1_age",
                })
    merged_df["player_a1_name"] = merged_df["fname"] + " " + merged_df["lname"]
    merged_df.drop(columns=["fname", "lname", "player_a1"], inplace=True)
    
    merged_df = pd.merge(merged_df, players_df, left_on=["player_a2"], right_on=["_id"], how="inner") \
                .drop(columns=["_id"]) \
                .rename(columns={
                    "ratings": "player_a2_ratings",
                    "gender": "player_a2_gender",
                    "age": "player_a2_age",
                })
    merged_df["player_a2_name"] = merged_df["fname"] + " " + merged_df["lname"]
    merged_df.drop(columns=["fname", "lname", "player_a2"], inplace=True)
    
    merged_df = pd.merge(merged_df, players_df, left_on=["player_b1"], right_on=["_id"], how="inner") \
                .drop(columns=["_id"]) \
                .rename(columns={
                    "ratings": "player_b1_ratings",
                    "gender": "player_b1_gender",
                    "age": "player_b1_age",
                })
    merged_df["player_b1_name"] = merged_df["fname"] + " " + merged_df["lname"]
    merged_df.drop(columns=["fname", "lname", "player_b1"], inplace=True)
    
    merged_df = pd.merge(merged_df, players_df, left_on=["player_b2"], right_on=["_id"], how="inner") \
                .drop(columns=["_id"]) \
                .rename(columns={
                    "ratings": "player_b2_ratings",
                    "gender": "player_b2_gender",
                    "age": "player_b2_age",
                })
    merged_df["player_b2_name"] = merged_df["fname"] + " " + merged_df["lname"]
    merged_df.drop(columns=["fname", "lname", "player_b2"], inplace=True)
    
    merged_df["date"] = pd.to_datetime(merged_df["date"])
    
    merged_df["scores"] = merged_df["scores"].apply(convert_to_score_array).apply(convert_to_game_score)
    
    merged_df.to_csv(output_file_path)