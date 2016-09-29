from LoadData import *
from Strategy import *
from Analysis import *

game_data = GameData.get_data_from_mysql(game_num=10)

for game in game_data:
    # i = KellyInvestor(game, MySQLAnalyzer)
    i = WhoScoreInvestor(game, MySQLAnalyzer)
    i.game_processing()
