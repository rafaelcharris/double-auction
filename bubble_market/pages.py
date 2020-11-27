from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
import time

class Instructions(Page):
    def is_displayed(self):
        return False


class Auction(Page):
    live_method = 'live_auction'

    def vars_for_template(self):
        return {"remaining_periods": Constants.num_rounds - self.group.round_number,
                "av_divided": Constants.average_divided,
                "initial_amount": Constants.endowment,
                "initial_assets": self.player.assets
                }

class ResultsWaitPage(WaitPage):
    pass


class Results(Page):

    def is_displayed(self):
        if self.round_number == Constants.num_rounds:
            return True


page_sequence = [Instructions, Auction, ResultsWaitPage, Results]
