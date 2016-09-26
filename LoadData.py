# -*- coding=utf-8 -*-

db_host = '192.168.1.5'
db_user = 'caiex'
db_passwd = '12345678'


class GameData:

    def __init__(self, origin_data):
        self.europe_id = origin_data[0][0]

        self.handicap_line = origin_data[0][-2]
        self.hilo_line = origin_data[0][-1]

        score = origin_data[0][-3] if origin_data[0][-3] is not None else origin_data[0][-4]
        if int(score[0]) > int(score[2]):
            self.result = 0
        elif int(score[0]) == int(score[2]):
            self.result = 1
        elif int(score[0]) < int(score[2]):
            self.result = 2
        self.odds_sets = map(lambda x: x[1:5:], origin_data[::-1])

    @staticmethod
    def get_data_from_mysql(europe_id=None, game_num=50):
        import pymysql

        game_list = list()
        with pymysql.connect(host=db_host, user=db_user, passwd=db_passwd, db='crawler', charset='utf8') \
                as cursor:

            with cursor as cur:
                if europe_id is None:
                    sql = 'SELECT europe_id FROM company_odds_history ORDER BY RAND() LIMIT %d' % game_num

                    cur.execute(sql)
                    europe_ids = cur.fetchall()
                else:
                    europe_ids = (europe_id, )

                for europe_id in europe_ids:
                    sql = 'SELECT \
                        a.europe_id, \
                        a.odds_one, \
                        a.odds_two, \
                        a.odds_three, \
                        a.state, \
                        a.score, \
                        b.SCORE final_score, \
                        c.handicap_line, \
                        c.liji_hilo_line \
                    FROM \
                        company_odds_history a \
                    LEFT OUTER JOIN t_crawler_win310 b ON a.europe_id = b.WIN310_EUROPE_ID \
                    LEFT OUTER JOIN odds_model c ON a.europe_id = c.europe_id \
                    WHERE \
                        a.odds_type = 0 \
                    AND a.gaming_company = "利记" \
                    AND a.europe_id = %s \
                    ORDER BY \
                        a.update_time DESC' % europe_id

                    cur.execute(sql)
                    result_set = cur.fetchall()
                    if len(result_set) > 50:
                        game_list.append(GameData(result_set))

        return game_list

    def __str__(self):
        return 'europe_id: %d' % self.europe_id

    def __repr__(self):
        return self.__str__()
