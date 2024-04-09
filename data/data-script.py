from csvmerge import merge_csv
from preprocessing import preprocess
from mongo_data_preprocessing import preprocess_mongo_data
from data_api import events_api, leagues_api, player_api

input_2019 = "data/data_input/2019_doubles_data.xlsx"
output_2019 = "data/data_output/preprocessed_2019_data.csv"
output_merged = "data/data_output/combined.csv"
mongo_data = "data/data_output/mongo_merged.csv"

if __name__=="__main__":
    print("Populating latest players data")
    player_api.run()
    print("Done")
    print("Populating latest league matches data")
    leagues_api.run()
    print("Done")
    print("Populating latest event matches data")
    events_api.run()
    print("Done")
    print("Preprocessing 2019 data")
    preprocess(input_2019, output_2019)
    print("Done")
    print("Fetching player and match data from MongoDB")
    preprocess_mongo_data(mongo_data)
    print("Concatenating data")
    merge_csv(output_2019, mongo_data, output_merged)
    print("Done")