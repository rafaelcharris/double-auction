from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class Auction(Page):
    live_bid = 'live_bid'
    live_ask = 'live_ask'

class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [Auction, ResultsWaitPage, Results]
