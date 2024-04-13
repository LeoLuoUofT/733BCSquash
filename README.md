# 733BCSquash

Branch names correspond to work done by individual teammates

Leo - Notebooks deal with Elo rating system trials and match outcome predictor model trials - Elo_system.ipynb
Data--scrape - Experimental scraping scripts that we tried as well as some that gave us relevant URLs for future API hits
Akanksha - Experimental scraping notebooks
Maureen - Visualization aggregations and Tableau dashboard bits
fayad - Complete app with preprocessing, Elo generation and model training pipeline

Please check out to fayad for the whole app as it stands now and other branches to see different milestones or stages in our project

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