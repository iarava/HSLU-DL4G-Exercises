import numpy as np
from jass.base import const

from jass.base.const import color_masks
from jass.base.const import card_values
from jass.base.player_round_cheating import PlayerRoundCheating
from jass.player.player_cheating import PlayerCheating


class MinimaxPlayer(PlayerCheating):
    def select_trump(self, rnd: PlayerRoundCheating) -> int:
        """
        Player chooses a trump based on the given round information.
        Args:
            rnd: current round
        Returns:
            selected trump
        """
        # select the trump with the largest number of cards
        print("Cards:", rnd.hand)
        print("Cards in String:", const.convert_one_hot_encoded_cards_to_str_encoded_list(rnd.hand))
        trump = 0
        trump_value = [
            [1, 1, 0.75, 2, 0.5, 1.5, 0.5, 0.5, 0.25],
            [0, 0, 0.1, 0.1, 0.25, 0.25, 0.5, 0.75, 1],
            [1, 0.75, 0.5, 0.25, 0.25, 0.1, 0.1, 0, 0]
        ]

        max_trump_value = 0
        highest_color_trump = 0
        max_unde_value = 0
        max_obe_value = 0
        for i in range(4):
            trump_value_color = 0.0
            unde_value_color = 0.0
            obe_value_color = 0.0
            for j in range(const.color_offset[i], const.color_offset[i] + 9):
                trump_value_color += rnd.hand[j] * trump_value[0][j % 9]
                unde_value_color += rnd.hand[j] * trump_value[1][j % 9]
                obe_value_color += rnd.hand[j] * trump_value[1][j % 9]
            print("trump_values for", i, ":", trump_value_color)
            if max_trump_value <= trump_value_color:
                max_trump_value = trump_value_color
                highest_color_trump = i
            max_unde_value += unde_value_color
            max_obe_value += obe_value_color
        print("calculated highest Trump:", max_trump_value)
        print("calculated Unde-Ufe:", max_unde_value)
        print("calculated Obe-Abe:", max_obe_value)
        if rnd.forehand != False:
            if max_trump_value >= 4 or max_obe_value >= 4 or max_unde_value >= 4:
                trump = self.compareTrumpUndeUfeObeAbe(max_trump_value, highest_color_trump, max_unde_value,
                                                       max_obe_value)
            else:
                trump = const.PUSH
        else:
            trump = self.compareTrumpUndeUfeObeAbe(max_trump_value, highest_color_trump, max_unde_value, max_obe_value)

        print("Selected Trump:", trump)

        return trump

    def play_card(self, rnd: PlayerRoundCheating) -> int:
        """
        Player returns a card to play based on the given round information.
        Args:
            rnd: current round
        Returns:
            card to play, int encoded
        """
        # play random

        # get the valid cards to play
        valid_cards = rnd.get_valid_cards()

        value_of_hand = self.get_value_of_hand(rnd)

        # select a random card
        cardToPlay = self.minimax_recursive(rnd)
        return cardToPlay

    def compareTrumpUndeUfeObeAbe(self, max_trump_value, highest_color_trump, max_unde_value, max_obe_value):
        trump = 0
        if max_trump_value >= max_obe_value:
            if max_trump_value >= max_unde_value:
                trump = highest_color_trump
            else:
                trump = const.UNE_UFE
        elif max_trump_value >= max_unde_value:
            trump = highest_color_trump
        elif max_obe_value >= max_unde_value:
            trump = const.OBE_ABE
        elif max_unde_value > max_obe_value:
            trump = const.UNE_UFE
        return trump

    def get_value_of_hand(self, rnd: PlayerRoundCheating) -> np.array:
        hand = rnd.hand
        for i in range(hand.size):
            if hand[i] == 1:
                hand[i] = card_values[rnd.trump, i]

        return hand

    def getIndexOfValidCardWithHighestValue(self, rnd: PlayerRoundCheating) -> int:
        hand = rnd.hand
        indexOfCardToReturn = 0
        highestValue = 0
        for i in range(hand.size):
            if hand[i] == 1 and card_values[rnd.trump, i] >= highestValue:
                indexOfCardToReturn = i
                highestValue = card_values[rnd.trump, i]

        return indexOfCardToReturn

    def getIndexOfValidCardWithLowestValue(self, rnd: PlayerRoundCheating) -> int:
        hand = rnd.hand
        indexOfCardToReturn = 0
        lowestValue = 1000
        for i in range(hand.size):
            if hand[i] == 1 and card_values[rnd.trump, i] <= lowestValue:
                indexOfCardToReturn = i
                lowestValue = card_values[rnd.trump, i]

        return indexOfCardToReturn

    def getHighestValueInHand(self, rnd: PlayerRoundCheating) -> np.array:
        hand = rnd.hand
        # Array[0] -> Index of Card, Array[1] -> Value of Card
        # ToDo: Refactor later to Container
        returnArray = np.zeros(shape=[2], dtype=np.int32)

        for i in range(hand.size):
            if hand[i] == 1 and card_values[rnd.trump, i] >= returnArray[1]:
                returnArray[1] = card_values[rnd.trump, i]
                returnArray[0] = i

        return returnArray

    def minimax_recursive(self, rnd: PlayerRoundCheating) -> int:

        rndCopy = PlayerRoundCheating()
        rndCopy.set_from_round(rnd)

        returnValue = self.minimax_recursive2(rndCopy, False)
        return returnValue[1]

    def minimax_recursive2(self, roundCheating: PlayerRoundCheating, enemyPlayer: bool) -> np.array:

        # playerID = roundCheating.player
        validCards = roundCheating.get_valid_cards()
        returnValues = np.zeros(shape=[2], dtype=np.int32)

        if roundCheating.nr_cards_in_trick >= 3:
            if enemyPlayer:
                returnValues = self.getHighestValueInHand(roundCheating)
                returnValues[1] = (-1) * returnValues[1]
                return returnValues
            else:
                returnValues = self.getHighestValueInHand(roundCheating)
                return returnValues
        else:
            cardValues = np.zeros(shape=[36], dtype=np.int32)
            for i in range(validCards.size):
                if validCards[i] == 1:
                    newRound = self.createFollowingRoundFromTurn(roundCheating, i)
                    cardValues[i] = (self.minimax_recursive2(newRound, not enemyPlayer))[1]

            if enemyPlayer:
                returnValues[0] = np.argmin(cardValues)
                returnValues[1] = cardValues[returnValues[0]]
                return returnValues
            else:
                returnValues[0] = np.argmax(cardValues)
                returnValues[1] = cardValues[returnValues[0]]
                return returnValues

    def createFollowingRoundFromTurn(self, currentRound: PlayerRoundCheating, cardToPlay: int) -> PlayerRoundCheating:
        newRound = PlayerRoundCheating()
        newRound.set_from_round(currentRound)

        newRound.current_trick[newRound.nr_cards_in_trick] = cardToPlay
        newRound.hands[newRound.player, cardToPlay] = 0

        newRound.nr_cards_in_trick = newRound.nr_cards_in_trick + 1
        newRound.nr_played_cards = newRound.nr_played_cards + 1
        newRound.player = (newRound.player - 1) % 4

        newRound.hand = newRound.hands[newRound.player]

        return newRound