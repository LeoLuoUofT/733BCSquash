This is our submission for CMPT733

We take squash player and match data from ClubLocker and generate a better Elo-based rating and ranking system and a match outcome predictor model

## To install all the required packags
    pip install -r requirements.txt

## To run the data scraping, preprocessing and consolidation code
    python app.py

## To run the main elo app:
    pip install -r requirements.txt
    python eloApp.py
    navigate to localhost 8080 (the link provided in the console)
    then upload the 'concatenated_data.csv' file located in data_creation/data.

## Usage:
    The home page is for uploading csvs, you will not be able to access the rest of the pages without first uploading the match csv.
    The '/display' page shows the current elo ranking according to the csv upload and you can search by player name or show the top n players
    The '/predict' page allows you to create our current best preforming ML model and test it on player matches.
        For names to try out see test_names.txt in the /data_creation/data folder.

Other branches exhibit different experiments and different stages of progress for the project
