# -*- coding=utf-8 -*-
from elasticsearch.exceptions import RequestError


class ElasticSearchAnalyzer:

    from elasticsearch import Elasticsearch
    es_host = '192.168.175.102'
    es_port = 9200
    index = 'strategytest'
    type = 'operations'
    es_client = Elasticsearch(hosts=[{'host': es_host, 'port': es_port}])

    def __init__(self, game_info):
        try:
            ElasticSearchAnalyzer.es_client.indices.create(ElasticSearchAnalyzer.index, ElasticSearchAnalyzer.type)
        except RequestError as e:
            if e.error != 'index_already_exists_exception':
                print e

        self.game_info = game_info

    def insert(self, operation, option, ticket_odds, invest, **kwargs):

        # noinspection PyDictCreation
        operation_body = {
            'europe_id': self.game_info['europe_id'],
            'handicap_line': self.game_info['handicap_line'],
            'hilo_line': self.game_info['hilo_line'],
            'result': self.game_info['result'],
            'strategy': self.game_info['strategy'],
            'strategy_args': self.game_info['strategy_args'],
            'operation': operation,
            'option': option,
            'ticket_odds': ticket_odds,
            'invest': invest
        }
        if len(kwargs) == 2:
            operation_body['market_odds'] = kwargs['market_odds']
            operation_body['percentage'] = kwargs['percentage']

        ElasticSearchAnalyzer.es_client.create(ElasticSearchAnalyzer.index, ElasticSearchAnalyzer.type, body=operation_body)

    def search(self, *args, **kwargs):
        pass

# game_info = {
#     'europe_id': 123123,
#     'handicap_line': -1,
#     'hilo_line': 2,
#     'result': '1-2',
#     'strategy': 'KellyInvestor',
#     'strategy_args': {
#         'factor1': 0.5,
#         'factor2': 1.8
#     }
# }
#
# eee = ElasticSearchAnalyzer(game_info)
# eee.insert(1, 1, 1.23, 1000)