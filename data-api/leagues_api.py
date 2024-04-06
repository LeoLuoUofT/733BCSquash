import requests
from pymongo.mongo_client import MongoClient

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

def generate_overall_league_matches_list(match_ids):
    overall_league_matches = []
    for match in match_ids:
        data = get_match_info(match)[0]
        temp = {
            "type": "League",
            "date": data["matchDate"],
            "scores": data["score"],
            "player_a1": data["playerHome1Name"],
            "player_a2": data["playerHome2Name"],
            "player_b1": data["playerVisiting1Name"],
            "player_b2": data["playerVisiting2Name"],
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
        
if __name__=="__main__":
    client = MongoClient(CONNECTION_URI)

    # This works. Nice!
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print("Error: " + e)
        
    overall_league_matches = generate_overall_league_matches_list(match_ids=match_ids)
    push_to_mongo_db(client, "squashbc", "matches", overall_league_matches)
    
    client.close()

