from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
import time

class Auction(Page):
    live_method = 'live_auction'

class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [Auction, ResultsWaitPage, Results]
