from LoadData import *
from Strategy import *
from Analysis import *

game_data = GameData.get_data_from_mysql()

for game in game_data:

    KellyInvestor(game)