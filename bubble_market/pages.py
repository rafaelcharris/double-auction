from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
import time

class Instructions(Page):
    def is_displayed(self):
        if self.round_number == 1:
            return True

    def vars_for_template(self):
        return dict(
            time_limit=self.session.config['time_limit'],
            periods = Constants.num_rounds - 1
        )

    def before_next_page(self):
        self.session.vars['expiry'] = time.time() + self.session.config['time_limit']


class Auction(Page):
    live_method = 'live_auction'
    form_model = 'group'

    def get_timeout_seconds(self):
        return self.session.vars['expiry'] - time.time()

    def vars_for_template(self):
        self.player.cumulative_variable()
        return {"remaining_periods": Constants.num_rounds +1 - self.group.round_number,
                "average_div_now": self.group.fundamental_value*self.group.round_number,
                "av_divided": Constants.average_divided,
                "initial_amount": self.player.money,
                "initial_assets": self.player.assets,
                "previous_dividend": int(self.group.in_round(self.round_number - 1 ).fundamental_value) if self.round_number > 2 else "-"
                }

    def is_displayed(self):
        return self.round_number > 1 and self.round_number < Constants.num_rounds + 1

class ResultsWaitPage(WaitPage):
    after_all_players_arrive = 'set_payoffs'


class Results(Page):
    def before_next_page(self):
        self.session.vars['expiry'] = time.time() + self.session.config['time_limit']


    def is_displayed(self):
        return self.round_number > 1 and self.round_number < Constants.num_rounds + 1


page_sequence = [Instructions, Auction, ResultsWaitPage, Results]
