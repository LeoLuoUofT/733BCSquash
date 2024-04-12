import requests
from pymongo.mongo_client import MongoClient
from datetime import datetime

CONNECTION_URI = "mongodb+srv://fayadchowdhury:733squashBC@squashbc.ss6kkda.mongodb.net/?retryWrites=true&w=majority&appName=squashbc"

match_ids = [
    '184188',
    '184187',
    '184160',
    '184124',
    '184122',
    '182863',
    '169279',
    '169278',
    '169283',
    '169280',
    '169281',
    '169277',
    '169274',
    '169275',
    '169273',
    '169272',
    '169271',
    '169270',
    '169269',
    '169267',
    '169266',
    '169264',
    '169263',
    '169261',
    '169260',
    '169258',
    '169256',
    '169257',
    '169254',
    '169255',
    '169252',
    '169251',
    '169248',
    '182419',
    '176013',
    '176009',
    '176007',
    '169115',
    '169080',
    '169113',
    '169114',
    '169111',
    '169112',
    '169109',
    '169108',
    '169107',
    '169102',
    '169105',
    '169106',
    '169104',
    '169101',
    '169096',
    '169093',
    '169095',
    '169088',
    '169094',
    '169092',
    '169091',
    '169089',
    '169087',
    '169090',
    '169085',
    '169086',
    '169084',
    '169083',
    '169082',
    '169081',
    '167599',
    '167598',
    '167480',
    '167479',
    '167417',
    '167127',
    '167126',
    '167125',
    '167124',
    '167104',
    '167103',
    '166985',
    '166984',
    '156598',
    '156597',
    '156595',
    '156596',
    '156593',
    '156594',
    '156592',
    '156591',
    '156590',
    '156587',
    '156588',
    '156580',
    '156579',
    '156586',
    '156585',
    '156584',
    '156583',
    '156581',
    '156582',
    '156578',
    '156577',
    '156575',
    '156576',
    '156574',
    '156573',
    '156572',
    '156569',
    '165028',
    '156466',
    '156465',
    '156517',
    '156519',
    '156514',
    '156513',
    '156516',
    '156511',
    '156512',
    '156505',
    '156506',
    '156507',
    '156508',
    '156501',
    '156503',
    '156488',
    '156497',
    '156498',
    '156500',
    '156499',
    '156493',
    '156494',
    '156495',
    '156496',
    '156489',
    '156492',
    '156486',
    '156487',
    '156482',
    '156481',
    '156483',
    '156484',
    '156478',
    '156480',
    '156479',
    '156475',
    '156476',
    '156470',
    '156471',
    '156472',
    '156464',
    '156463',
]

def convert_date_string(date_str):
    try:
        # Parse the date string to a datetime object
        date_obj = datetime.strptime(date_str, '%m/%d/%Y')
        
        # Format the datetime object as the desired timestamp format
        timestamp_str = date_obj.strftime('%Y-%m-%dT00:00:00')
        
        return timestamp_str
    except ValueError:
        # If the input string does not match the specified format, return it as is
        return date_str

def get_match_info(match_id):
    url = "https://api.ussquash.com/resources/leagues/scorecards/live?id="
    url = url + str(match_id)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Error: ", response.status_code)
        return None

def get_player_id_from_name(client, db, collection, name):
    # Corner case for Kelly Ann Zander -_-
    if name == "Kelly Ann Zander":
        first_name = "Kelly Ann"
        last_name = "Zander"
    else:
        first_name, last_name = name.split(" ", 1)
    result = client[db][collection].find_one({"fname": first_name.strip(), "lname": last_name.strip()})
    if result == None:
        # print("No ID found for {name}".format(name=name))
        return None
    return result['_id']

def generate_overall_league_matches_list(client, db, player_collection, match_ids):
    overall_league_matches = []
    for match in match_ids:
        data = get_match_info(match)[0]
        temp = {
            "event_name": "Random League", # Possibly acquire this name
            "type": "League",
            "date": convert_date_string(data["matchDate"]),
            "scores": data["score"],
            "player_a1": get_player_id_from_name(client, db, player_collection, data["playerHome1Name"]) if data["playerHome1Name"] != "Default" else 0,
            "player_a2": get_player_id_from_name(client, db, player_collection, data["playerHome2Name"]) if data["playerHome2Name"] != "Default" else 0,
            "player_b1": get_player_id_from_name(client, db, player_collection, data["playerVisiting1Name"]) if data["playerVisiting1Name"] != "Default" else 0,
            "player_b2": get_player_id_from_name(client, db, player_collection, data["playerVisiting2Name"]) if data["playerVisiting2Name"] != "Default" else 0,
        }
        overall_league_matches.append(temp)
        
    print("Overall league matches generated")
    return overall_league_matches

def push_to_mongo_db(client, db, collection, data):
    db = client[db]
    collection = db[collection]
    try:
        collection.insert_many(data)
        print("Successfully pushed data")
    except Exception as e:
        print("Error pushing data to MongoDB: " + str(e))

def run():
    client = MongoClient(CONNECTION_URI)

    # This works. Nice!
    try:
        client.admin.command('ping')
        # print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print("Error: " + str(e))
    
    # Run once    
    overall_league_matches = generate_overall_league_matches_list(client, "squashbc", "players_aggregated", match_ids=match_ids)
    push_to_mongo_db(client, "squashbc", "matches", overall_league_matches)
    
    client.close()

