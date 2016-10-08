from LoadData import *
from Strategy import *
from Analysis import *

game_data = GameData.get_data_from_mysql(game_num=50)

for game in game_data:
    # i = KellyInvestor(game, MySQLAnalyzer)
    i = WhoScoreInvestor(game, MySQLAnalyzer, strong_team=True)
    i.game_processing()
