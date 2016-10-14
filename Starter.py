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
    i = WhoScoreInvestor(game, Analyzer, strong_team=True)
    i.game_processing()
    # print i.analyzer.result
