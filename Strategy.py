# -*- coding=utf-8 -*-
import random
import uuid


class Strategy:
    """
    Basic strategy logic with unimplements methods (e.g. buy_ticket, cash_out)
    and implemented methods.(e.g. payout, game_process...)
    """

    @staticmethod
    def compute_changing_rate(ticket_odds, market_odds):
        """
        Compute changing rate

        :param ticket_odds: odds when this ticket was bought
        :param market_odds: current market odds
        :return: rate of win or loss
        """
        try:
            if ticket_odds > market_odds:
                return (ticket_odds - market_odds) / (market_odds * (ticket_odds - 1)) + 1
            else:
                return ticket_odds / market_odds - 1
        except ZeroDivisionError:
            return 0

    def buy_ticket(self, odds_set):
        pass

    def cash_out(self, odds_set):
        pass

    def store_operation(self, operation, option, ticket_odds, invest, market_odds=None, changing_rate=None):
        """
        Store operation and output some logging

        :param operation: buy in or cash out
        :param option: ticket option
        :param ticket_odds: odds on ticket
        :param invest: the investment on this ticket
        :param market_odds: current market odds
        :param changing_rate: rate of win or loss
        """
        self.operation_list.append((operation, option, ticket_odds, invest, market_odds, changing_rate))
        if operation == 0:
            operation = 'CashOut'
        elif operation == 1:
            operation = 'BuyTicket'
        print '%s -- > option: %d, ticket_odds: %f, invest: %f, market_odds: %s, changing_rate: %s' \
            % (operation, option, ticket_odds, invest, market_odds, changing_rate)

    def payout(self):
        """
        Pay out
        Iterate ticket_bucket and see what's left in it.
        """
        winning = 0.0
        winning_tickets = self.ticket_bucket[self.game_data.result]
        for ticket in winning_tickets:
            winning += winning_tickets[ticket][0] * winning_tickets[ticket][1]
        self.winning += winning

    def game_processing(self):
        """
        Mock game processing.
        Buy in or cash out while reading each odds.
        Pay out when odds come to its end
        """
        for odds_set in self.game_data.odds_sets:
            self.buy_ticket(odds_set)
            self.cash_out(odds_set)
        self.payout()
        self.result_dict['total_winning'] = self.winning
        self.result_dict['total_invest'] = self.invest
        self.result_dict['total_money'] = self.money + self.winning
        self.show_final_stat()

    def show_final_stat(self):
        """
        Print some log of mocking result
        """
        print 'invest: %f' % self.invest
        print 'winning: %f' % self.winning
        print 'money: %f' % (self.money + self.winning)

    def __init__(self, game_data):
        self.ticket_bucket = {0: {}, 1: {}, 2: {}}
        self.money = 1
        self.invest = 0
        self.winning = 0
        self.game_data = game_data
        self.operation_list = list()
        self.result_dict = {
            'uuid': uuid.uuid1().__str__(),
            'europe_id': game_data.europe_id,
            'unique_id': game_data.unique_id,
            'handicap_line': game_data.handicap_line,
            'hilo_line': game_data.hilo_line,
            'result': game_data.result,
            'strategy': str(self.__class__).split('.')[1],
            'strategy_args': dict()
        }


class KellyInvestor(Strategy):
    """
    A KellyInvestor will buy tickets using kelly formula and cash out a ticket
    when its price increase/decrease to a certain rate.
    """
    @staticmethod
    def kelly_formula(odds, probility):
        """
        calculate percentage from kelly

        :param odds: odds
        :param probility: winning probility
        :return: percentage of kelly
        """
        return (odds * probility - 1 + probility) / odds

    @staticmethod
    def get_probilities(odds_set):
        """
        calculate probilities from odds

        :param odds_set: odds
        :return: probilities
        """
        margin = 1 / odds_set[0] + 1 / odds_set[1] + 1 / odds_set[2]
        return 1 / (margin * odds_set[0]), 1 / (margin * odds_set[1]), 1 / (margin * odds_set[2])

    def cash_out(self, odds_set):
        """
        Cash out when the percentage reach the threshold

        :param odds_set: list of odds
        """
        total = 0

        for i in range(len(odds_set[0:3:])):
            if len(self.ticket_bucket[i]) == 0:
                continue
            ticket_copy = self.ticket_bucket[i].copy()
            for ticket in self.ticket_bucket[i]:
                percentage = Strategy.compute_changing_rate(self.ticket_bucket[i][ticket][0], odds_set[i])

                if percentage > self.cash_out_factor_high or percentage < self.cash_out_factor_low:
                    total += self.ticket_bucket[i][ticket][0] / odds_set[i] * self.ticket_bucket[i][ticket][1]
                    self.store_operation(0, i, self.ticket_bucket[i][ticket][0], self.ticket_bucket[i][ticket][1], odds_set[i], percentage)
                    del ticket_copy[ticket]
            self.ticket_bucket[i] = ticket_copy
            i += 1

        self.winning += total

    @staticmethod
    def random_fluctuating(number):
        """
        Generate a fluctual of probility

        :param number:
        :return:
        """
        return number * random.uniform(0.9, 1.1)

    def buy_ticket(self, odds_set):
        """
        Buy ticket using kelly formula

        :param odds_set:
        :return:
        """
        if odds_set[-2] == 'Run':
            return
        probilities = KellyInvestor.get_probilities(odds_set)
        for i in range(len(odds_set[0:3])):
            if random.random() < self.buying_factor:
                f = KellyInvestor.kelly_formula(odds_set[i] - 1, KellyInvestor.random_fluctuating(probilities[i]))
                if f > 0:
                    invest = f * self.money
                    self.ticket_bucket[i][len(self.ticket_bucket[i])] = (odds_set[i], invest)
                    self.store_operation(1, i, odds_set[i], invest)
                    self.invest += invest
                    self.money -= invest

    def __init__(self, game_data, buying_factor=0.5, cash_out_factor_high=1.8, cash_out_factor_low=-0.5):
        Strategy.__init__(self, game_data)
        self.result_dict['strategy_args'] = {
            'buying_factor': buying_factor,
            'cash_out_factor_high': cash_out_factor_high,
            'cash_out_factor_low': cash_out_factor_low
        }

        self.buying_factor = buying_factor
        self.cash_out_factor_high = cash_out_factor_high
        self.cash_out_factor_low = cash_out_factor_low


class NonCashoutInvestor(KellyInvestor):
    """
    Inherited from KellyInvestor, the NonCashOutInvestor will also buy tickets using Kelly formula,
    but he/she will cash out tickets when pigs fly.
    """

    def cash_out(self, odds_set):
        """
        never cash out

        :param odds_set: list of odds
        :return:
        """
        pass


class WhoScoreInvestor(Strategy):
    """
    A WhoScoreInvestor will set up a certain strong/weak team at beginning and then buy every option of ticket equally.
    Only When the team which is set up scored earlier than the opposite, the investor would cash out all the tickets.
    """

    def __init__(self, game_data, strong_team=False):
        Strategy.__init__(self, game_data)
        self.result_dict['strategy_args'] = {
            'strong_team': strong_team
        }
        self.strong_team = strong_team
        self.score = '0-0'

    def buy_ticket(self, odds_set):
        """
        Buy all tickets at the beginning

        :param odds_set: list of odds
        """
        if self.money <= 0 or odds_set[-2] == 'Run':
            return
        self.ticket_bucket = {
            0: {0: (odds_set[0], 1.0/3)},
            1: {0: (odds_set[1], 1.0/3)},
            2: {0: (odds_set[2], 1.0/3)}
        }
        self.store_operation(1, 0, odds_set[0], 1.0/3)
        self.store_operation(1, 1, odds_set[1], 1.0/3)
        self.store_operation(1, 2, odds_set[2], 1.0/3)
        self.invest = 1
        self.money = 0

        if self.strong_team ^ (odds_set[0] < odds_set[2]):
            self.score = '0-1'
        else:
            self.score = '1-0'

    def cash_out(self, odds_set):
        """
        Cash out all tickets when one team scored

        :param odds_set: list of odds
        """
        if odds_set[-2] == 'Run' and odds_set[-1] == self.score:
            total = 0
            for option in self.ticket_bucket:
                for ticket in self.ticket_bucket[option]:
                    (odds, invest) = self.ticket_bucket[option][ticket]
                    total += odds / odds_set[option] * invest
                    percentage = Strategy.compute_changing_rate(odds, odds_set[option])
                    self.store_operation(0, option, odds, invest, odds_set[option], percentage)
            self.winning += total
            self.ticket_bucket = {0: {}, 1: {}, 2: {}}
