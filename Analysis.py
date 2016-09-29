# -*- coding=utf-8 -*-


class Analyzer:

    def __init__(self, game_info):
        self.game_info = game_info

    def insert_operation(self, operation, option, ticket_odds, invest, market_odds, percentage):
        pass

    def insert_result(self, total_winning, total_invest, total_money):
        pass


class ElasticSearchAnalyzer(Analyzer):

    from elasticsearch.exceptions import RequestError
    from elasticsearch import Elasticsearch
    es_host = '192.168.175.102'
    es_port = 9200
    index = 'strategytest'
    type = 'operations'
    es_client = Elasticsearch(hosts=[{'host': es_host, 'port': es_port}])

    def __init__(self, game_info):
        Analyzer.__init__(self, game_info)
        try:
            ElasticSearchAnalyzer.es_client.indices.create(ElasticSearchAnalyzer.index, ElasticSearchAnalyzer.type)
        except ElasticSearchAnalyzer.RequestError as e:
            if e.error != 'index_already_exists_exception':
                print e

    def insert_operation(self, operation, option, ticket_odds, invest, market_odds, percentage):

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

        ElasticSearchAnalyzer.es_client.create(ElasticSearchAnalyzer.index, ElasticSearchAnalyzer.type, body=operation_body)


class MySQLAnalyzer(Analyzer):

    db_host = '192.168.1.5'
    db_user = 'caiex'
    db_passwd = '12345678'

    import pymysql
    conn = pymysql.connect(host=db_host, user=db_user, passwd=db_passwd, db='testing', charset='utf8')

    def __init__(self, game_info):
        Analyzer.__init__(self, game_info)

    def insert_operation(self, operation, option, ticket_odds, invest, market_odds, percentage):

        with MySQLAnalyzer.conn.cursor() as cur:
            sql = 'INSERT INTO operations ' \
                  '(uuid, operation, `option`, ticket_odds, invest, market_odds, percentage) ' \
                  'VALUES ' \
                  '(%s, %s, %s, %s, %s, %s, %s)'
            param = (self.game_info['uuid'].__str__(),
                     operation,
                     option,
                     ticket_odds,
                     invest,
                     market_odds,
                     percentage
                     )
            cur.execute(sql, param)
            MySQLAnalyzer.conn.commit()

    def insert_result(self, total_winning, total_invest, total_money):
        with MySQLAnalyzer.conn.cursor() as cur:
            sql = 'INSERT INTO result ' \
                  '(uuid, europe_id, hadicap_line, hilo_line, result, strategy, strategy_args, total_winning, total_invest, final_money) ' \
                  'VALUES ' \
                  '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

            param = (
                self.game_info['uuid'].__str__(),
                self.game_info['europe_id'],
                self.game_info['handicap_line'],
                self.game_info['hilo_line'],
                self.game_info['result'],
                self.game_info['strategy'],
                self.game_info['strategy_args'].__str__(),
                total_winning,
                total_invest,
                total_money
            )

            cur.execute(sql, param)
            MySQLAnalyzer.conn.commit()
