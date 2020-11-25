from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
    ExtraModel
)
import random

author = 'Your name here'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'bubble_market'
    players_per_group = None
    num_rounds = 1
    fundamental_value = [0, 8, 28, 60]

class Subsession(BaseSubsession):
    def creating_session(self):
        self.fundamental_value = random.choice(Constants.fundamental_value)


class Group(BaseGroup):
    highest_bidder = models.IntegerField()
    highest_bid = models.CurrencyField(initial=0)
    lowest_ask = models.CurrencyField(initial = 0)

class Player(BasePlayer):

    assets = models.IntegerField()

    def live_auction(self, data):
        if data["type"] == "bid":
            group = self.group
            my_id = self.id_in_group
            if data["value"] > group.highest_bid:
                response = {"id_in_group":my_id,
                            "type": "bid",
                            "value":data["value"]}

                return {0: response}
        else:
            group = self.group
            my_id = self.id_in_group
            if data["value"] < group.lowest_ask:
                response = {"id_in_group":my_id,
                            "type": "ask",
                            "value":data["value"]}
                return {0: response}

