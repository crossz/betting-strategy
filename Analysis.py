# -*- coding=utf-8 -*-


class Analyzer:
    """
    Basic Analyzer with defining some nessesary methods in it.(Not completed yet)
    """

    def __init__(self, game_info):
        self.game_info = game_info

    def insert_operation(self, operation, option, ticket_odds, invest, market_odds, percentage):
        pass

    def insert_result(self, total_winning, total_invest, total_money):
        pass


class ElasticSearchAnalyzer(Analyzer):
    """
    The data generated in Strategy module will be stored in ES. In using ES's brilliant searching ability,
    one can analyze the operation data in many ways and dimensions.
    """

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
        """
        Insert operation data into es

        :param operation: buy in or cash out
        :param option: ticket option
        :param ticket_odds: ticket odds
        :param invest: the invest on this ticket
        :param market_odds: current market odds
        :param percentage: winning or loss rate
        :return:
        """
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
        """
        Insert operation data into mysql

        :param operation: buy in or cash out
        :param option: ticket option
        :param ticket_odds: ticket odds
        :param invest: the invest on this ticket
        :param market_odds: current market odds
        :param percentage: winning or loss rate
        """
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
        """
        Insert mocking result into mysql

        :param total_winning: money from pay out and cash out
        :param total_invest: total spending money
        :param total_money: final money in hand
        :return:
        """
        with MySQLAnalyzer.conn.cursor() as cur:
            sql = 'INSERT INTO result ' \
                  '(uuid, europe_id, unique_id, hadicap_line, hilo_line, result, strategy, strategy_args, total_winning, total_invest, final_money) ' \
                  'VALUES ' \
                  '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

            param = (
                self.game_info['uuid'].__str__(),
                self.game_info['europe_id'],
                self.game_info['unique_id'],
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


class MemoryAnalyzer(Analyzer):

    def __init__(self, game_info):
        Analyzer.__init__(self, game_info)
        self.operation_list = list()
        self.result = {
            'uuid': game_info['uuid'].__str__(),
            'europe_id': game_info['europe_id'],
            'unique_id': game_info['unique_id'],
            'handicap_line': game_info['handicap_line'],
            'hilo_line': game_info['hilo_line'],
            'result': game_info['result'],
            'strategy': game_info['strategy'],
        }

    def insert_operation(self, operation, option, ticket_odds, invest, market_odds, percentage):
        self.operation_list.append(
            (operation, option, ticket_odds, invest, market_odds, percentage)
        )

    def insert_result(self, total_winning, total_invest, total_money):
        self.result['total_winning'] = total_winning
        self.result['total_invest'] = total_invest
        self.result['total_money'] = total_money
        self.result['strategy_args'] = self.game_info['strategy_args'].__str__()
