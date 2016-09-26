# -*- coding=utf-8 -*-


class ElasticSearchOperation:

    from elasticsearch import Elasticsearch
    es_host = '192.168.1.101'
    es_port = 9200
    es_client = Elasticsearch(hosts=[{'host': es_host, 'port': es_port}])

    def __init__(self):
        ElasticSearchOperation.es_client.indices.create('StrategyTest', 'operations')

    def insert(self, operation, option, ticket_odds, invest, **kwargs):
        pass

    def search(self, *args, **kwargs):
        pass

