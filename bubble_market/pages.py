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
        self.participant.vars['expiry'] = time.time() + self.session.config['time_limit']

class Auction(Page):
    live_method = 'live_auction'

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def vars_for_template(self):
        return {"remaining_periods": Constants.num_rounds - self.group.round_number,
                "av_divided": Constants.average_divided,
                "initial_amount": Constants.endowment,
                "initial_assets": self.player.assets
                }

class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [Instructions, Auction, ResultsWaitPage, Results]
