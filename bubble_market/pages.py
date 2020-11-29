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
            time_limit=self.session.config['time_limit']
        )

    def before_next_page(self):
        self.session.vars['expiry'] = time.time() + self.session.config['time_limit']


class Auction(Page):
    live_method = 'live_auction'

    def get_timeout_seconds(self):
        return self.session.vars['expiry'] - time.time()

    def vars_for_template(self):
        return {"remaining_periods": Constants.num_rounds - self.group.round_number,
                "av_divided": Constants.average_divided,
                "initial_amount": Constants.endowment,
                "initial_assets": self.player.assets
                }

    def is_displayed(self):
        return self.session.vars['expiry'] - time.time() > 0

class ResultsWaitPage(WaitPage):
    after_all_players_arrive = 'set_payoffs'


class Results(Page):

    def is_displayed(self):
        if self.round_number == Constants.num_rounds:
            return True


page_sequence = [Instructions, Auction, ResultsWaitPage, Results]
