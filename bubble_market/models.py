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
Double Auction with several rounds
"""


class Constants(BaseConstants):
    name_in_url = 'bubble_market'
    players_per_group = None
    num_rounds = 11
    fundamental_value = [0, 8, 28, 60]
    endowment = 500
    average_divided = sum(fundamental_value)/len(fundamental_value)
    assets = 3

class Subsession(BaseSubsession):

    def creating_session(self):
        for group in self.get_groups():
            group.fundamental_value = random.choice(Constants.fundamental_value)
        if self.round_number == 2:
            for players in self.get_players():

                players.assets = Constants.assets
                players.money = Constants.endowment

class Group(BaseGroup):
    fundamental_value = models.CurrencyField()
    highest_bidder = models.IntegerField()
    highest_bid = models.CurrencyField(initial=0)
    lowest_ask = models.CurrencyField(initial = 100)
    lowest_asker = models.IntegerField()

    def set_payoffs(self):
        if self.round_number > 1:
            for player in self.get_players():
                player.payoff = player.assets*self.fundamental_value + player.money


class Player(BasePlayer):

    assets = models.IntegerField()
    money = models.IntegerField()

    def live_auction(self, data):
        if data["type"] == "bid":
            print("Ask data: " + str(data))
            print("getting an bid!")
            group = self.group
            my_id = self.id_in_group
            if data["value"] > self.money:
                response = {"type": "error",
                            "message": "You cannot bid above the money you have!"}
                return {my_id: response}

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
            print("Ask data: "+str(data))
            group = self.group
            my_id = self.id_in_group
            if self.assets - 1 < 0:
                response = {"type": "error",
                            "message": "You don't have assets to sell",
                            }
                return {self.id_in_group: response}
            if data["value"] < group.lowest_ask:
                group.lowest_asker = my_id
                group.lowest_ask = data["value"]
                response = {"id_in_group":my_id,
                            "type": "ask",
                            "value":data["value"]}
                print("Response from ask: " + str(response))
                return {0: response}
            else:
                response = {"type": "error",
                            "message": "You cannot ask above the lowest standing ask"}
                return {my_id: response}

        elif data["type"] == "contract":
             #Restablecer el valor de la highest bid a lo más bajo cuando se venda el paquete
            print("Received a contract!. Looks like this: " + str(data))

            if data["action"] == "press_buy":
                print("The player pressed buy")
                self.group.highest_bidder = self.id_in_group
                if data["value"] <= self.money:
                    print("Player " + str(self.id_in_group) + " has enough money.")
                    print("This is the highest bidder: " + str(self.group.highest_bidder))
                    print("This is the lowest bidder: " + str(self.group.lowest_asker))
                    if data["value"] == 0:
                        response = {"type": "error",
                                    "message": "There are no assets to buy"}
                        return {self.id_in_group: response}
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

                    # Restablecer el valor de highest bid
                    self.group.highest_bid = 0
                    self.group.lowest_ask = Constants.endowment

                    ContractValue.objects.create(player = buyer, value=data["value"], round=self.round_number - 1)

                    response_seller = {"id_in_group": seller.id_in_group,
                                       "type": "contract",
                                       "value": data["value"],
                                       "assets": seller.assets,
                                       "money": seller.money,
                                       "deal": True,
                                       "action": "press_buy"}
                    response_buyer = {"id_in_group": buyer.id_in_group,
                                      "type": "contract",
                                      "value": data["value"],
                                      "assets": buyer.assets,
                                      "money": buyer.money,
                                      "deal": True,
                                      "action": "press_buy"}
                    response_all = {
                        "type": "contract",
                        "value": data["value"],
                        "action": "press_buy"
                        }

                    response = {player.id_in_group: response_all for player in self.group.get_players()}
                    response.update({buyer.id_in_group: response_buyer, seller.id_in_group: response_seller})
                    print("This is the response from a contract" + str(response))
                    return response
                else:
                    print("debería mandar error")
                    response = {"type":"error",
                                "message": "You don't have enough money",
                                "error_code": 4}
                    return {self.id_in_group: response}

            else:
                print("pressed sell")
                self.group.lowest_asker = self.id_in_group
                if self.assets >= 0:
                    print("Player " + str(self.id_in_group) + " has enough assets.")
                    print("This is the highest bidder: " + str(self.group.highest_bidder))
                    print("This is the lowest bidder: " + str(self.group.lowest_asker))
                    if self.group.highest_bidder == self.group.lowest_asker:
                        response = {"type": "error",
                                    "message": "You cannot sell to yourself"
                                    }
                        return {self.id_in_group: response}
                    if data["value"] == 0:
                        response = {"type": "error",
                                    "message": "There are no bids."}
                        return {self.id_in_group: response}
                    buyer = self.group.get_player_by_id(self.group.highest_bidder)
                    seller = self.group.get_player_by_id(self.group.lowest_asker)
                    # Cambiar el dinero
                    buyer.money -= data["value"]
                    seller.money += data["value"]
                    # Cambiar los assets
                    buyer.assets += 1
                    seller.assets -= 1
                    if seller.assets < 0:
                        response_seller = {"type": "error",
                                           "message": "You cannot sell more assets",
                                           "error_code": 2}
                        #devolver los valores a su anterior valor
                        buyer.money += data["value"]
                        seller.money -= data["value"]
                        buyer.assets -= 1
                        seller.assets += 1
                        return {seller.id_in_group: response_seller}
                    else:
                        # Restablecer el valor de highest bid
                        self.group.highest_bid = 0
                        self.group.lowest_ask = Constants.endowment
                        #store the current price in a way

                        ContractValue.objects.create(player = seller, value=data["value"], round=self.round_number - 1)
                        response_seller = {"id_in_group": seller.id_in_group,
                                       "type": "contract",
                                       "value": data["value"],
                                       "assets": seller.assets,
                                       "money": seller.money,
                                        "deal": True,
                                           "action": "press_sell"}
                        response_buyer = {"id_in_group": buyer.id_in_group,
                                           "type": "contract",
                                           "value": data["value"],
                                           "assets": buyer.assets,
                                           "money": buyer.money,
                                          "deal": True,
                                          "action": "press_sell"}
                        response_all = {
                            "type": "contract",
                            "value": data["value"],
                            "deal": False,
                        "action": "press_sell"}

                        response = {player.id_in_group: response_all for player in self.group.get_players()}
                        response.update({buyer.id_in_group: response_buyer, seller.id_in_group: response_seller})
                        print("This is the response from a contract" + str(response))
                        return response
                else:

                    response = {"type": "error",
                                "message": "You don't have enough assets",
                                "error_code": 4}
                    return {self.id_in_group: response}

    def cumulative_variable(self):
        if self.round_number > 2:
            #self.assets = sum(filter(None, [p.assets for p in self.in_previous_rounds()]))

            self.assets = self.in_round(self.round_number - 1).assets
            #OLD FUNCTION
            #self.money = self.in_round(self.round_number - 1).money
            self.money = int(self.in_round(self.round_number - 1).payoff)
            print("Print money: " + str(self.money) + "-------|")


class ContractValue(ExtraModel):
    value = models.IntegerField()
    player = models.Link(Player)
    round = models.IntegerField()
#TODO: Agregar botón de eliminar la bid o ask

#Todo: change the place of the timer

def custom_export(players):
    yield ["player_id", "contract_price", "round"]
    for contract in ContractValue.objects.values():
        print(str(contract['id']))
        yield[contract['id'], contract['value'], contract['round']]
