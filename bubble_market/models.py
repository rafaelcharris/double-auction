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
    average_divided = sum(fundamental_value)/len(fundamental_value)
    assets = 1

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

    assets = models.IntegerField(initial = Constants.assets)
    money = models.CurrencyField(initial = Constants.endowment)

    def live_auction(self, data):
        if data["type"] == "bid":

            group = self.group
            my_id = self.id_in_group

            if data["value"] > group.highest_bid:
                group.highest_bidder = my_id

                group.highest_bid = data["value"]
                response = {"id_in_group": my_id,
                            "type": "bid",
                            "value": data["value"]}
                #group.highest_bid = data["value"]
                print("Response from bid: " + str(response))
                return {0: response}
            else:
                response = {"type":"error",
                            "message":"New bids must be higher",
                            "error_code": 1}
                return {self.id_in_group: response}

        elif data["type"] == "ask":
            group = self.group
            my_id = self.id_in_group
            if data["value"] < group.lowest_ask:
                group.lowest_asker = my_id
                response = {"id_in_group":my_id,
                            "type": "ask",
                            "value":data["value"]}
                print("Response from ask: " + str(response))
                return {0: response}

        elif data["type"] == "contract":
             #Restablecer el valor de la highest bid a lo más bajo cuando se venda el paquete
            print("Received a contract!")
            if data["action"] == "press_buy":
                print("The player pressed buy")
                self.group.highest_bidder = self.id_in_group
                if data["value"] <= self.money:
                    print("Player " + str(self.id_in_group) + " has enough money.")
                    print("This is the highest bidder: " + str(self.group.highest_bidder))
                    print("This is the lowest bidder: " + str(self.group.lowest_asker))
                    if self.group.highest_bidder == self.group.lowest_asker:
                        response = {"type": "error",
                                    "message": "You cannot buy from yourself",
                                    "error_code": 3
                                    }
                        return {self.id_in_group: response}

                    buyer = self.group.get_player_by_id(self.group.highest_bidder)
                    seller = self.group.get_player_by_id(self.group.lowest_asker)
                    # Cambiar el dinero
                    buyer.money -= data["value"]
                    seller.money += data["value"]
                    buyer.assets += 1
                    seller.assets -= 1
                    # Cambiar los assets
                    if seller.assets < 0:
                        response_seller = {"type": "error",
                                           "message": "You cannot sell more assets",
                                           "error_code": 2}
                        buyer.money += data["value"]
                        seller.money -= data["value"]
                        buyer.assets -= 1
                        seller.assets += 1
                        return {seller.id_in_group, response_seller}
                    else:
                        # Restablecer el valor de highest bid
                        self.group.highest_bid = 0
                        self.group.lowest_ask = 100

                        response_me = {"id_in_group": buyer.id_in_group,
                                       "type": "contract",
                                       "value": data["value"],
                                       "assets": buyer.assets,
                                       "money": buyer.money}
                        response_all = {
                            "type": "contract",
                            "value": data["value"]}

                        response = {player.id_in_group: response_all for player in self.group.get_players()}
                        response.update({buyer.id_in_group: response_me})
                        print("This is the response from a contract" + str(response))
                        return response
                else:
                    response = {"type":"error",
                                "message": "You don't have enough money",
                                "error_code": 4}
                    return {self.id_in_group: response}

            else:
                self.group.lowest_asker = self.id_in_group
                print("The player pressed buy")

    def bids(self):
        return Bid.objects.filter(player=self)

class Bid(ExtraModel):
    player = models.Link(Player)
    group = models.Link(Group)

#TODO: Hacer que se puedan comprar cosas
#TODO: mostar info de las transacciones

#TODO: Agregar botón de eliminar la bid o ask