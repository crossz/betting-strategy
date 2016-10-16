import LoadData
import Strategy
import Analysis
GameData = LoadData.GameData
WhoScoreInvestor = Strategy.WhoScoreInvestor
KellyInvestor = Strategy.KellyInvestor
# Analyzer = Analysis.MemoryAnalyzer
Analyzer = Analysis.MySQLAnalyzer
game_data = GameData.get_data_from_mysql(game_num=1)

for game in game_data:
    # i = KellyInvestor(game, Analyzer)
    i = WhoScoreInvestor(game, strong_team=True)
    i.game_processing()
    a = Analyzer(i.operation_list, i.result_dict)
    a.save_all()
    # print i.analyzer.result
