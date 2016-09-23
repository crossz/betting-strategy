# -*- coding=utf-8 -*-
import random
import pymysql

conn = pymysql.connect(host='192.168.1.5', user='caiex', passwd='12345678', db="crawler", charset="utf8")
cur = conn.cursor()


class Strategy:

    def compute_changing_rate(self, ticket_odds, market_odds):
        pass

    def buy_ticket(self, odds_set):
        pass

    def cash_out(self, odds_set):
        pass

    def payout(self):
        winning = 0.0
        winning_tickets = self.ticket_bucket[self.result]
        for ticket in winning_tickets:
            winning += winning_tickets[ticket][0] * winning_tickets[ticket][1]
        self.winning += winning

    def game_processing(self):
        for odds_set in self.odds_sets:
            self.buy_ticket(odds_set)
            self.cash_out(odds_set[:-1:])
        self.payout()

    def show_final_stat(self):
        print 'invest: %f' % self.invest
        print 'winning: %f' % self.winning
        print 'money: %f' % (self.money + self.winning)

    def __init__(self, odds_sets):
        self.ticket_bucket = {0: {}, 1: {}, 2: {}}
        self.money = 1
        self.invest = 0
        self.winning = 0
        score = odds_sets[0][-2] if odds_sets[0][-1] is None else odds_sets[0][-1]
        if int(score[0]) > int(score[2]):
            self.result = 0
        elif int(score[0]) == int(score[2]):
            self.result = 1
        elif int(score[0]) < int(score[2]):
            self.result = 2
        self.odds_sets = map(lambda x: x[0:4:], odds_sets[::-1])


class KellyInvestor(Strategy):

    @staticmethod
    def kelly_formula(odds, probility):
        # type: (float, float) -> float
        return (odds * probility - 1 + probility) / odds

    @staticmethod
    def get_probilities(odds_set):
        odds_set = map(lambda x: float(x), odds_set)
        margin = 1 / odds_set[0] + 1 / odds_set[1] + 1 / odds_set[2]
        return 1 / (margin * odds_set[0]), 1 / (margin * odds_set[1]), 1 / (margin * odds_set[2])

    def compute_changing_rate(self, ticket_odds, market_odds):
        try:
            if ticket_odds > market_odds:
                return (ticket_odds - market_odds) / (market_odds * (ticket_odds - 1)) + 1
            else:
                return ticket_odds / market_odds - 1
        except ZeroDivisionError:
            return 0

    def cash_out(self, odds_set):
        total = 0

        i = 0
        for i in range(len(odds_set)):
            if len(self.ticket_bucket[i]) == 0:
                continue
            copy = self.ticket_bucket[i].copy()
            for ticket in self.ticket_bucket[i]:
                percentage = self.compute_changing_rate(self.ticket_bucket[i][ticket][0], float(odds_set[i]))

                if percentage > self.cash_out_factor_high or percentage < self.cash_out_factor_low:
                    total += self.ticket_bucket[i][ticket][0] / float(odds_set[i]) * self.ticket_bucket[i][ticket][1]
                    # print i, percentage, self.ticket_bucket[i][ticket], odds_set[i]
                    print 'CashOut -- > option: %d, ticket_odds: %f, invest: %f, market_odds: %s, changing_rate: %f' \
                          % (i, self.ticket_bucket[i][ticket][0], self.ticket_bucket[i][ticket][1], odds_set[i], percentage)

                    del copy[ticket]
            self.ticket_bucket[i] = copy
            i += 1

        self.winning += total

    @staticmethod
    def random_fluctuating(number):
        return number * random.uniform(0.9, 1.1)

    def buy_ticket(self, odds_set):
        if odds_set[-1] == 'Run':
            return
        odds_set = map(lambda x: float(x), odds_set[:-1:])
        probilities = KellyInvestor.get_probilities(odds_set)
        for i in range(len(odds_set)):
            if random.random() < self.buying_factor:
                f = KellyInvestor.kelly_formula(odds_set[i] - 1, KellyInvestor.random_fluctuating(probilities[i]))
                if f > 0:
                    invest = f * self.money
                    self.ticket_bucket[i][len(self.ticket_bucket[i])] = (odds_set[i], invest)
                    print 'BuyTicket --> option: %d, ticket_odds: %f, invest: %f' % (i, odds_set[i], invest)
                    self.invest += invest
                    self.money -= invest

    def __init__(self, odds_sets, buying_factor=0.5, cash_out_factor_high=1.8, cash_out_factor_low=-0.5):
        Strategy.__init__(self, odds_sets)
        self.buying_factor = buying_factor
        self.cash_out_factor_high = cash_out_factor_high
        self.cash_out_factor_low = cash_out_factor_low


class NonCashoutInvestor(KellyInvestor):

    def cash_out(self, odds_set):
        pass

sql = 'SELECT europe_id FROM company_odds_history ORDER BY RAND() LIMIT 50'

cur.execute(sql)
europe_ids = cur.fetchall()

total_money = 0
total_invest = 0
total_game = 0
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
    if len(result_set) <= 50:
        continue
    try:
        s = KellyInvestor(result_set, buying_factor=0.8, cash_out_factor_high=1.8, cash_out_factor_low=-0.5)
        # s = NonCashoutInvestor(result_set, buying_factor=0.1, cash_out_factor_high=1.5, cash_out_factor_low=-0.3)
        s.game_processing()
        s.show_final_stat()

        total_invest += s.invest
        total_money += s.winning
        total_game += 1
    except ValueError as e:
        print e.message
    except IndentationError as e:
        print e.message
print '=' * 70
print 'total invest: %f' % total_invest
print 'total winning: %f' % total_money
print 'total game: %d' % total_game
