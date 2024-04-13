# Main app code

import warnings
warnings.filterwarnings("ignore")

from data import data_script
from elo_rating import elo_rating
from outcome_classifier import model

if __name__=="__main__":
    # TODO: Write and run cleanup script if possible
    data_script.run()
    # Next run Elo ratings scripts
    elo_rating.run("data/data_output/combined.csv")
    # Next run model code
    model.run()