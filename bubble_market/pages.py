from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
import time

class Auction(Page):
    live_method = 'live_auction'
    def vars_for_template(self):
        return {"remaining_periods": Constants.num_rounds - self.group.round_number,
                "av_divided": Constants.average_divided}

class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [Auction, ResultsWaitPage, Results]
