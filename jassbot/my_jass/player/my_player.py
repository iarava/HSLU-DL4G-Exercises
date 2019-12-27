# HSLU
#
# Created by Thomas Koller on 20.08.18
#

import numpy as np

import jass.base.const as const
from jass.base.player_round import PlayerRound
from jass.player.player import Player


class MyPlayer(Player):
    """
    Sample implementation of a player to play Jass.
    """

    def select_trump(self, rnd: PlayerRound) -> int:
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
            for j in range(const.color_offset[i], const.color_offset[i]+9):
                trump_value_color += rnd.hand[j] * trump_value[0][j%9]
                unde_value_color += rnd.hand[j] * trump_value[1][j%9]
                obe_value_color += rnd.hand[j] * trump_value[1][j%9]
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
                trump = self.compareTrumpUndeUfeObeAbe(max_trump_value, highest_color_trump, max_unde_value, max_obe_value)
            else:
                trump = const.PUSH
        else:
            trump = self.compareTrumpUndeUfeObeAbe(max_trump_value,highest_color_trump, max_unde_value, max_obe_value)

        print("Selected Trump:", trump)

        return trump

    def play_card(self, rnd: PlayerRound) -> int:
        """"
        Player returns a card to play based on the given round information.

        Args:
            rnd: current round

        Returns:
            card to play, int encoded
        """
        # play random
        trump = rnd.trump
        played_cards = rnd.current_trick
        print("---------------Trick-------------------")
        print("currenct cards:", const.convert_one_hot_encoded_cards_to_str_encoded_list(rnd.hand))
        print("played cards:", const.convert_int_encoded_cards_to_str_encoded(self.get_played_cards_in_trick(played_cards)))
        print("Trump:", trump, const.trump_strings_german_long[trump])
        # get the valid cards to play
        valid_cards = rnd.get_valid_cards()
        valid_cards_nr = const.convert_one_hot_encoded_cards_to_int_encoded_list(rnd.get_valid_cards())
        print("valid cards:", const.convert_one_hot_encoded_cards_to_str_encoded_list(valid_cards))
        card_values = valid_cards*const.card_values[trump]
        highest_card = np.argmax(card_values)
        if highest_card == 0 and np.any(card_values[:] == highest_card):
            highest_card = valid_cards_nr[0]
        highest_card_value = const.card_values[trump, highest_card]
        first_card = played_cards[0]
        first_card_color = const.color_of_card[first_card]
        first_player = False
        same_team = False
        card = highest_card
        card_state = self.set_card_state(rnd.tricks)
        bock = self.check_if_bock(valid_cards, card_state)
        if first_card != -1:
            current_highest_played_card = np.argmax(const.get_cards_encoded(self.get_played_cards_in_trick(played_cards))* const.card_values[trump])
            current_player_highest_card = np.where(played_cards == current_highest_played_card)[0]
            print("current played highest cards", current_highest_played_card)
            print("current player with highest card", current_player_highest_card)
            print("Player:", rnd.player)
            print("Played Cards:", rnd.nr_cards_in_trick)
            print("Dealer", rnd.dealer)
            same_team = const.same_team[rnd.player, current_player_highest_card]
            print("Same Team:", same_team)
            highest_played_card_value = const.card_values[trump, current_highest_played_card]
            cards_of_first_color = valid_cards * const.color_masks[first_card_color]
            card_value_of_first_color = cards_of_first_color * const.color_masks[first_card_color]
            card_value_of_first_color_int = const.convert_one_hot_encoded_cards_to_int_encoded_list(card_value_of_first_color)
            print("cards of first color:", const.convert_one_hot_encoded_cards_to_str_encoded_list(cards_of_first_color))
            print("bock", bock)
            if not(const.OBE_ABE == trump or trump == const.UNE_UFE):
                trump_cards = valid_cards * const.color_masks[trump]
                trump_card_values = trump_cards*const.card_values[trump]
                if same_team:
                    card = self.card_for_same_player_high(card_value_of_first_color, card_value_of_first_color_int, valid_cards_nr)
                else:
                    if highest_card_value > highest_played_card_value:
                        card = highest_card
                    elif highest_played_card_value % 9 < 1:
                        card = np.argmax(trump_cards)
                    else:
                        card = valid_cards_nr[np.argmin(valid_cards_nr)]
            if trump == const.OBE_ABE:
                if same_team:
                    card = self.card_for_same_player_high(card_value_of_first_color, card_value_of_first_color_int, valid_cards_nr)
                else:
                    if highest_card_value > highest_played_card_value:
                        card = highest_card
                    else:
                        card = valid_cards_nr[np.argmin(valid_cards_nr)]
            if trump == const.UNE_UFE:
                if same_team:
                    card = self.card_for_same_player_high(card_value_of_first_color, card_value_of_first_color_int,valid_cards_nr)
                else:
                    if highest_card_value > highest_played_card_value:
                        card = highest_card
                    else:
                        card = valid_cards_nr[np.argmin(valid_cards_nr)]
        else:
            if bock != None:
                        print("bock_color", bock)
                        bock_cards = valid_cards * const.color_masks[bock]
                        print("bock_cards", bock_cards)
                        bock_values = bock_cards * const.card_values[bock]
                        highest_bock = np.random.choice(np.flatnonzero(bock_cards))
                        card = highest_bock

        print("selected card:", const.convert_int_encoded_cards_to_str_encoded([card]))
        return card

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

    def get_played_cards_in_trick(self, trick) -> []:
        return [card for card in trick if card != -1]

    def card_for_same_player_high(self, card_value_of_first_color, card_value_of_first_color_int, valid_cards_nr):
        check10 = np.any(card_value_of_first_color[:] == 10)
        if check10:
            card = np.where(card_value_of_first_color == 10)[0]
        else:
            if np.size(card_value_of_first_color_int) != 0:
                card = card_value_of_first_color_int[np.argmin(card_value_of_first_color_int)]
            else:
                card = valid_cards_nr[np.argmin(valid_cards_nr)]
        return card

    def check_if_bock(self, valid_cards, card_state):
        bock_color = None
        for i in range(0, 4):
            cards_color = valid_cards * const.color_masks[i]
            valid_color_cards = len(np.flatnonzero(cards_color))
            played_color_cards = len(np.flatnonzero(card_state[i]))
            print("nr_cards", valid_color_cards + played_color_cards)
            if played_color_cards == 9:
                pass
            elif valid_color_cards + played_color_cards == 9:
                bock_color = i
        print("bock_color", bock_color)
        return bock_color


    def set_card_state(self,tricks):
        card_state = np.array(
            [
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
            ], np.int32
        )
        for trick in tricks:
            for i in range(0, 4):
                if trick[i] != -1:
                    color_of_card = const.color_of_card[trick[i]]
                    card_state[color_of_card, (trick[i] % 9)] = 1
        return card_state