# -*- coding=utf-8 -*-
import random
import pymysql

conn = pymysql.connect(host='192.168.1.5', user='caiex', passwd='12345678', db="crawler", charset="utf8")
cur = conn.cursor()


sql = 'SELECT \
    odds_one H, \
    odds_two D, \
    odds_three A, \
    c.state, \
    c.score company_score, \
    e.SCORE win310_score \
FROM \
    company_odds_history c \
LEFT JOIN t_crawler_win310 e ON c.europe_id = e.WIN310_EUROPE_ID \
WHERE \
    c.europe_id = 1268044 \
AND c.gaming_company = "利记" \
AND c.odds_type = 0 \
ORDER BY \
    c.update_time DESC'


cur.execute(sql)
result_set = cur.fetchall()



class Strategy:

    def cash_out(self, odds_set):
        return 0

    @staticmethod
    def pricing(ticket_odds, market_odds):
        try:
            if ticket_odds > market_odds:
                return (ticket_odds - market_odds) / (market_odds * (ticket_odds - 1)) + 1
            else:
                return ticket_odds / market_odds - 1
        except ZeroDivisionError:
            return 0

    def buy_ticket(self, odds_set):
        if odds_set[-1] == 'Run':
            return

        i = 0
        for ticket in self.tickets_bucket:
            if self.tickets_bucket[ticket] is None and random.random() > 0.9:
                self.tickets_bucket[i] = float(odds_set[i])
                self.invest += 1
                print self.tickets_bucket, self.invest
            i += 1

    def payout(self):
        for ticket in self.tickets_bucket:
            if ticket is not None and ticket == self.result:
                return self.tickets_bucket[ticket]
        return 0

    def game_processing(self):
        for odds in self.odds_set:
            self.buy_ticket(odds)
            self.winning += self.cash_out(odds[:-1:])
        self.winning += self.payout()

    def __init__(self, odds_set):
        self.tickets_bucket = {0: None, 1: None, 2: None}
        self.invest = 0
        self.winning = 0
        score = odds_set[0][-2] if odds_set[0][-1] is None else odds_set[0][-1]
        if int(score[0]) > int(score[2]):
            self.result = 0
        elif int(score[0]) == int(score[2]):
            self.result = 1
        elif int(score[0]) < int(score[2]):
            self.result = 2
        self.odds_set = map(lambda x: x[0:4:], odds_set[::-1])


class CheapKiller(Strategy):

    def cash_out(self, odds_set):
        total = 0

        i = 0
        for i in range(len(odds_set)):
            if self.tickets_bucket[i] is None:
                continue

            percentage = self.pricing(self.tickets_bucket[i], float(odds_set[i]))
            if percentage > 1.8 or percentage < -0.5:
                total += self.tickets_bucket[i] / float(odds_set[i])
                print i, percentage, self.tickets_bucket[i], float(odds_set[i])
                self.tickets_bucket[i] = None
            i += 1

        return total


initial_tickets = {0: 2.91, 1: 3.25, 2: 2.38}
c = CheapKiller(result_set)
c.game_processing()
print c.winning, c.tickets_bucket, c.invest
