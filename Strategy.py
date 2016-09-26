# -*- coding=utf-8 -*-
import random
from LoadData import GameData


class Strategy:

    def compute_changing_rate(self, ticket_odds, market_odds):
        pass

    def buy_ticket(self, odds_set):
        pass

    def cash_out(self, odds_set):
        pass

    def payout(self):
        winning = 0.0
        winning_tickets = self.ticket_bucket[self.game_data.result]
        for ticket in winning_tickets:
            winning += winning_tickets[ticket][0] * winning_tickets[ticket][1]
        self.winning += winning

    def game_processing(self):
        for odds_set in self.game_data.odds_sets:
            self.buy_ticket(odds_set)
            self.cash_out(odds_set[:-1:])
        self.payout()

    def show_final_stat(self):
        print 'invest: %f' % self.invest
        print 'winning: %f' % self.winning
        print 'money: %f' % (self.money + self.winning)

    def __init__(self, game_data):
        self.ticket_bucket = {0: {}, 1: {}, 2: {}}
        self.money = 1
        self.invest = 0
        self.winning = 0
        self.game_data = game_data


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
            ticket_copy = self.ticket_bucket[i].copy()
            for ticket in self.ticket_bucket[i]:
                percentage = self.compute_changing_rate(self.ticket_bucket[i][ticket][0], float(odds_set[i]))

                if percentage > self.cash_out_factor_high or percentage < self.cash_out_factor_low:
                    total += self.ticket_bucket[i][ticket][0] / float(odds_set[i]) * self.ticket_bucket[i][ticket][1]
                    # print i, percentage, self.ticket_bucket[i][ticket], odds_set[i]
                    print 'CashOut -- > option: %d, ticket_odds: %f, invest: %f, market_odds: %s, changing_rate: %f' \
                          % (i, self.ticket_bucket[i][ticket][0], self.ticket_bucket[i][ticket][1], odds_set[i], percentage)

                    del ticket_copy[ticket]
            self.ticket_bucket[i] = ticket_copy
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

    def __init__(self, game_data, buying_factor=0.5, cash_out_factor_high=1.8, cash_out_factor_low=-0.5):
        Strategy.__init__(self, game_data)
        self.buying_factor = buying_factor
        self.cash_out_factor_high = cash_out_factor_high
        self.cash_out_factor_low = cash_out_factor_low


class NonCashoutInvestor(KellyInvestor):

    def cash_out(self, odds_set):
        pass

