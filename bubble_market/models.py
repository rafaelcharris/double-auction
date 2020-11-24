from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)


author = 'Your name here'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'bubble_market'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    highest_bidder = models.IntegerField()
    highest_bid = models.CurrencyField(initial=0)
    lowest_ask = models.CurrencyField(initial = 0)

class Player(BasePlayer):
    def live_bid(self, bid):
        group = self.group
        my_id = self.id_in_group
        if bid > group.highest_bid:
            response = dict(id_in_group=my_id, bid=bid)
            return {0: response}

    def live_ask(self, ask):
        group = self.group
        my_id = self.id_in_group
        if ask < group.lowest_bid:
            response = dict(id_in_group=my_id, ask=ask)
            return {0: response}
