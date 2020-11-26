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
    endowment = 100

class Subsession(BaseSubsession):

    def creating_session(self):
        for group in self.get_groups():
            group.fundamental_value = random.choice(Constants.fundamental_value)


class Group(BaseGroup):
    fundamental_value = models.CurrencyField()
    highest_bidder = models.IntegerField()
    highest_bid = models.CurrencyField(initial=0)
    lowest_ask = models.CurrencyField(initial = 100)
    lowest_asker = models.IntegerField()

class Player(BasePlayer):

    assets = models.IntegerField(initial = 0)
    money = models.CurrencyField(initial = Constants.endowment)

    def live_auction(self, data):
        if data["type"] == "bid":
            group = self.group
            my_id = self.id_in_group

            if data["value"] > group.highest_bid:
                group.highest_bidder = my_id
                response = {"id_in_group": my_id,
                            "type": "bid",
                            "value": data["value"]}
                #group.highest_bid = data["value"]

                return {0: response}
            else:
                response = {"type":"error",
                            "message":"New bids must be higher"}
                return {self.id_in_group: response}

        elif data["type"] == "ask":
            group = self.group
            my_id = self.id_in_group
            if data["value"] < group.lowest_ask:
                response = {"id_in_group":my_id,
                            "type": "ask",
                            "value":data["value"]}
                return {0: response}
        elif data["type"] == "contract":
            my_id = self.id_in_group
            self.assets += 1
            if data["value"] <= self.money:
                self.money -= data["value"]
                response = {"id_in_group": my_id,
                            "type": "contract",
                            "value": data["value"],
                            "assets": self.assets,
                            "money": self.money}
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