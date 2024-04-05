import requests
from pymongo.mongo_client import MongoClient

CONNECTION_URI = "mongodb+srv://fayadchowdhury:733squashBC@squashbc.ss6kkda.mongodb.net/?retryWrites=true&w=majority&appName=squashbc"

# Dictionary for category and DivisionID to do API hits
cat_div = {
    "men_singles_19+": 2,
    "men_singles_25+": 18,
    "men_singles_30+": 21,
    "men_singles_35+": 22,
    "men_singles_40+": 25,
    "men_singles_45+": 26,
    "men_singles_50+": 29,
    "men_singles_55+": 30,
    "men_singles_60+": 33,
    "men_singles_65+": 34,
    "men_singles_70+": 35,
    "men_singles_75+": 36,
    "men_singles_80+": 37,
    "men_singles_85+": 181,
    "women_singles_19+": 329,
    "women_singles_25+": 42,
    "women_singles_30+": 45,
    "women_singles_35+": 46,
    "women_singles_40+": 49,
    "women_singles_45+": 50,
    "women_singles_50+": 53,
    "women_singles_55+": 178,
    "women_singles_60+": 179,
    "women_singles_65+": 180,
    "women_singles_70+": 330,
    "women_singles_75+": 331,
    "women_singles_80+": 332,
    "women_singles_85+": 333,
    "men_doubles_25+": 115,
    "men_doubles_30+": 118,
    "men_doubles_35+": 119,
    "men_doubles_40+": 122,
    "men_doubles_45+": 123,
    "men_doubles_50+": 126,
    "men_doubles_55+": 127,
    "men_doubles_60+": 130,
    "men_doubles_65+": 131,
    "men_doubles_70+": 132,
    "men_doubles_75+": 133,
    "men_doubles_80+": 134,
    "men_doubles_85+": 363,
    "women_doubles_25+": 139,
    "women_doubles_30+": 142,
    "women_doubles_35+": 143,
    "women_doubles_40+": 146,
    "women_doubles_45+": 147,
    "women_doubles_50+": 150,
    "women_doubles_55+": 155,
    "women_doubles_60+": 283,
    "women_doubles_65+": 358,
    "women_doubles_70+": 359,
    "women_doubles_75+": 360,
}

def get_player_rankings(division):
    url = "https://api.ussquash.com/resources/res/public/organizations/10349/rankings?RowsPerPage=10000&PageNumber=1&DivisionId="
    url = url + str(division)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Error: ", response.status_code)
        return None

def generate_overall_players_list(cat_div):
    overall_players_list = []

    for k, v in cat_div.items():
        gender, category, age = k.split("_")
        players = get_player_rankings(v)
        for player in players:
            temp_player = player
            temp_player["gender"] = gender
            temp_player["category"] = category
            temp_player["age"] = age
            overall_players_list.append(temp_player)
            
    return overall_players_list

def push_to_mongo_db(client, db, collection, data):
    db = client[db]
    collection = db[collection]
    try:
        collection.insert_many(data)
        print("Successfully pushed data")
        client.close()
    except(e):
        print("Error pushing data to MongoDB: " + e)

if __name__=="__main__":
    client = MongoClient(CONNECTION_URI)

    # This works. Nice!
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print("Error: " + e)
        
    overall_players_list = generate_overall_players_list(cat_div=cat_div)
    
    push_to_mongo_db(client, "squashbc", "players", overall_players_list)

