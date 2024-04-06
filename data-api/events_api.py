import requests
from pymongo.mongo_client import MongoClient
from datetime import datetime

CONNECTION_URI = "mongodb+srv://fayadchowdhury:733squashBC@squashbc.ss6kkda.mongodb.net/?retryWrites=true&w=majority&appName=squashbc"

events_list = [
    {
        "name": "2024 Jesters Doubles Tournament",
        "tournamentId": "15842",
        "divIds": []
    },
    {
        "name": "2023 Gamble",
        "tournamentId": "15283",
        "divIds": []
    },
    {
        "name": "2023 Western Canadian Doubles Squash Championships",
        "tournamentId": "15282",
        "divIds": [309, 313, 205, 176, 368, 175, 160, 286, 286, 228]
    },
    {
        "name": "Evergreen Summer Doubles Squash Tournament",
        "tournamentId": "15050",
        "divIds": [174, 309, 156, 313, 201, 355, 176, 177, 177, 228]
    },
    {
        "name": "Hillside Wealth Management 2023 BC Doubles Championships",
        "tournamentId": "14493",
        "divIds": [130, 177, 228, 229, 234, 309, 310, 314, 314, 371]
    },
    {
        "name": "2023 Jesters Doubles",
        "tournamentId": "14053",
        "divIds": []
    },
    {
        "name": "Gamble 100/75 Charity Doubles",
        "tournamentId": "14052",
        "divIds": []
    },
    {
        "name": "Western Canadian Doubles Squash Championships",
        "tournamentId": "14051",
        "divIds": [122, 130, 156, 162, 228, 309, 313, 371, 371]
    },
    {
        "name": "2022 BC Open Doubles Championships",
        "tournamentId": "13377",
        "divIds": []
    },
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

def generate_overall_events_matches_list(events_list):
    events_matches = []
    # match_count = 0
    for event in events_list:
        # print(event["name"])
        tournamentId = event["tournamentId"]
        if len(event["divIds"]) == 0: # No draws available :(
            # print("No draws available for this event")
            continue
        else:
            for divId in event["divIds"]:
                # print(event["name"], divId)
                regular_url = "https://api.ussquash.com/resources/tournaments/{tournamentId}/division/{divId}/draws".format(tournamentId=tournamentId, divId=divId)
                # print(regular_url)
                response = requests.get(regular_url)
                if response.status_code == 200:
                    data = response.json() # Do for each section
                    for section in data:
                        if len(section["matches"]) == 0: # No matches found; try alternative URL
                            # print("No matches found in regular URL, trying alternative URL")
                            alternative_url = "https://api.ussquash.com/resources/tournaments/{tournamentId}/matches/{divId}/1?pageSize=500".format(tournamentId=tournamentId, divId=divId)
                            # print(alternative_url)
                            response2 = requests.get(alternative_url)
                            if response2.status_code == 200:
                                # Handle this data
                                matches = response2.json()
                                # print("Alternative URL success with {x} matches".format(x=len(matches)))
                                # match_count += len(matches)
                                for match in matches:
                                    temp_match = {
                                        "event_name": event["name"],
                                        "type": "Tournament",
                                        "date": convert_date_string(match["MatchDate"]),
                                        "scores": match["Score"],
                                        "player_a1": match["playerLeftId"],
                                        "player_a2": match["playerLeftPartnerId"],
                                        "player_b1": match["playerRightId"],
                                        "player_b2": match["playerRightPartnerId"],
                                    }
                                    # print(temp_match)
                                    events_matches.append(temp_match)
                                # pass
                            else:
                                print("Error: ", response.status_code)
                        else:
                            # print("Regular URL success with {x} matches".format(x=len(section["matches"])))
                            # match_count += len(section["matches"])
                            for match in section["matches"]:
                                temp_match = {
                                    "event_name": event["name"],
                                    "type": "Tournament",
                                    "date": convert_date_string(match["matchdate"]),
                                    "scores": match["Score"],
                                    "player_a1": match["wid1"],
                                    "player_a2": match["wid2"],
                                    "player_b1": match["oid1"],
                                    "player_b2": match["oid2"],
                                }
                                # print(temp_match)
                                events_matches.append(temp_match)
                            # pass
                            # Handle regular data
                else:
                    print("Error: ", response.status_code)
                
        # print("----------------------")
    # print("Match count = {match_count}".format(match_count=match_count))
    return events_matches

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
        print("Error: " + str(e))
    
    # Run once    
    overall_events_matches = generate_overall_events_matches_list(events_list=events_list)
    push_to_mongo_db(client, "squashbc", "matches", overall_events_matches)
    
    client.close()

