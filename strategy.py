# -*- coding=utf-8 -*-
import random
import pymysql

conn = pymysql.connect(host='192.168.1.5', user='caiex', passwd='12345678', db="crawler", charset="utf8")
cur = conn.cursor()


class Strategy:

    def cash_out(self, odds_set):
        return 0

    def pricing(self, ticket_odds, market_odds):
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
            if self.tickets_bucket[ticket] is None and random.random() < self.buying_factor:
                self.tickets_bucket[i] = float(odds_set[i])
                self.invest += 1
                print self.tickets_bucket, self.invest
            i += 1

    def payout(self):
        for ticket in self.tickets_bucket:
            if self.tickets_bucket[ticket] is not None and ticket == self.result:
                return self.tickets_bucket[ticket]
        return 0

    def game_processing(self):
        for odds in self.odds_set:
            self.buy_ticket(odds)
            self.winning += self.cash_out(odds[:-1:])
        self.winning += self.payout()

    def show_final_stat(self):
        print 'winning: %f' % self.winning
        print 'total invest: %f' % self.invest
        if self.invest != 0:
            print 'profiting rate: %f' % (self.winning / self.invest)
        else:
            print 'profiting rate: 0'
        print 'tickets: %s' % self.tickets_bucket

    def __init__(self, odds_set, buying_factor=0.5):
        self.tickets_bucket = {0: None, 1: None, 2: None}
        self.invest = 0
        self.winning = 0
        self.buying_factor = buying_factor
        score = odds_set[0][-2] if odds_set[0][-1] is None else odds_set[0][-1]
        if int(score[0]) > int(score[2]):
            self.result = 0
        elif int(score[0]) == int(score[2]):
            self.result = 1
        elif int(score[0]) < int(score[2]):
            self.result = 2
        self.odds_set = map(lambda x: x[0:4:], odds_set[::-1])


class Investor(Strategy):

    def cash_out(self, odds_set):
        total = 0

        i = 0
        for i in range(len(odds_set)):
            if self.tickets_bucket[i] is None:
                continue

            percentage = self.pricing(self.tickets_bucket[i], float(odds_set[i]))
            if percentage > self.cash_out_factor_high or percentage < self.cash_out_factor_low:
                total += self.tickets_bucket[i] / float(odds_set[i])
                print i, percentage, self.tickets_bucket[i], float(odds_set[i])
                self.tickets_bucket[i] = None
            i += 1

        return total

    def __init__(self, odds_set, cash_out_factor_high=1.5, cash_out_factor_low=-0.5):
        Strategy.__init__(self, odds_set)
        self.cash_out_factor_high = cash_out_factor_high
        self.cash_out_factor_low = cash_out_factor_low


class ExpectationInvestor(Investor):

    @staticmethod
    def get_probilities(odds_set):
        odds_set = map(lambda x: float(x), odds_set)
        margin = 1/odds_set[0] + 1/odds_set[1] + 1/odds_set[2]
        return 1 / (margin * odds_set[0]), 1 / (margin * odds_set[1]), 1 / (margin * odds_set[2])

    def pricing(self, ticket_odds, probilities):
        expectation = ticket_odds * probilities
        if expectation > 1:
            return expectation - 1 / ticket_odds - 1
        else:
            return expectation - 1

    def cash_out(self, odds_set):
        total = 0

        i = 0
        for i in range(len(odds_set)):
            if self.tickets_bucket[i] is None:
                continue
            try:
                probilities = self.get_probilities(odds_set)
                percentage = self.pricing(self.tickets_bucket[i], probilities[i])
                if percentage > self.cash_out_factor_high or percentage < self.cash_out_factor_low:
                    total += self.tickets_bucket[i] / float(odds_set[i])
                    print i, percentage, self.tickets_bucket[i], float(odds_set[i])
                    self.tickets_bucket[i] = None
            except ZeroDivisionError:
                pass
            i += 1

        return total


sql = 'SELECT europe_id FROM company_odds_history ORDER BY RAND() LIMIT 50'

cur.execute(sql)
europe_ids = cur.fetchall()


total_winning = 0
total_invest = 0
for europe_id in europe_ids:
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
        c.europe_id = %s \
    AND c.gaming_company = "利记" \
    AND c.odds_type = 0 \
    ORDER BY \
        c.update_time DESC' % europe_id
    print '*' * 50 + str(europe_id[0]) + '*' * 50
    cur.execute(sql)
    result_set = cur.fetchall()
    if len(result_set) > 50:
        c = Investor(result_set, 1.8)
        # c = Strategy(result_set)
        # c = ExpectationInvestor(result_set, 1.8)
        c.game_processing()
        total_winning += c.winning
        total_invest += c.invest
        c.show_final_stat()

print total_winning, total_invest

