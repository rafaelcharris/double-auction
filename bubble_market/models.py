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
    num_rounds = 10
    fundamental_value = [0, 8, 28, 60]

class Subsession(BaseSubsession):
    def creating_session(self):
        for group in self.get_groups():
            group.fundamental_value = random.choice(Constants.fundamental_value)


class Group(BaseGroup):
    fundamental_value = models.IntegerField()
    highest_bidder = models.IntegerField()
    highest_bid = models.CurrencyField(initial=0)
    lowest_ask = models.CurrencyField(initial = 0)
    lowest_asker = models.IntegerField()
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

#    def bids(self):
#        return Bid.objects.filter(player=self)
#
#class Bid(ExtraModel):
#    player = models.Link(Player)
#    group = models.Link(Group)

#TODO: Hacer que se puedan comprar cosas
#TODO: mostar info de las transacciones
#TODO: Agregar límite de tiempo