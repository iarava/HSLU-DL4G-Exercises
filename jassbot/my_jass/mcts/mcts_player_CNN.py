# HSLU
#
# Created by Thomas Koller on 20.08.18
#

import numpy as np
import time

import jass.base.const as const
from jass.base.player_round import PlayerRound
from jass.player.player import Player
import jass.base.round_factory as roundInf
from my_jass.mcts.Node import Node
from my_jass.mcts.Tree import Tree
from my_jass.mcts.informationset import Informationset

import tensorflow as tf


class MctsPlayerCNN(Player):
    """
    Sample implementation of a player to play Jass.
    """
    list = dict()
    def __init__(self):
        self.model = self.__initModel()

    def __initModel(self):
        return tf.keras.models.load_model('model_TrumpSelection.h5')

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
        print("Forehand:", rnd.forehand)

        #check if already pushed
        if(rnd.forehand == None):
            cards = np.r_[rnd.hand, 0]
            multiplier = np.array([1,1,1,1,1,1,1])
        else:
            cards = np.r_[rnd.hand, 1]
            multiplier = np.array([1,1,1,1,1,1,0])

        y = self.model.predict(cards.reshape(-1,37))
        print(y * multiplier)

        select_trump = np.argmax(y * multiplier)
        if(select_trump == const.MAX_TRUMP+1):
            select_trump = const.PUSH

        print("Select as Trump: ", select_trump)

        return select_trump

    def play_card(self, rnd: PlayerRound) -> int:
        """
        Player returns a card to play based on the given round information.

        Args:
            rnd: current round

        Returns:
            card to play, int encoded
        """
        # play random
        print("player", rnd.player)
        print("played cards:", rnd.tricks)
        """for c in range(0,4):
            print("player",c, ": ", const.convert_one_hot_encoded_cards_to_str_encoded_list(rnd.hands[c]))
            print("valid cards:", const.convert_one_hot_encoded_cards_to_str_encoded_list(rnd.get_valid_cards()))"""
        print("trump", const.trump_strings_short[rnd.trump])

        # get the valid cards to play
        valid_cards = rnd.get_valid_cards()
        print("Valid_cards:", const.convert_one_hot_encoded_cards_to_str_encoded_list(valid_cards))
        played_cards = rnd.current_trick
        first_card = played_cards[0]
        card_state = self.set_card_state(rnd.tricks)
        bock = self.check_if_bock(valid_cards, card_state)
        if first_card == -1 and bock:
            print("bock_color", bock)
            bock_cards = valid_cards * const.color_masks[bock]
            print("bock_cards", bock_cards)
            bock_values = bock_cards * const.card_values[bock]
            highest_bock = np.random.choice(np.flatnonzero(bock_cards))
            card = highest_bock
        else:
            card = self.montecarlo(rnd)

        # select a random card
        # return np.random.choice(np.flatnonzero(valid_cards))
        print("card_played", const.convert_one_hot_encoded_cards_to_str_encoded_list(const.get_cards_encoded(card)))
        return card

    def montecarlo(self, rnd: PlayerRound):
        tree = Tree()

        end_time = time.time() + 5
        all = 1

        while time.time() < end_time:
            counter = 1
            treeInf = Tree()

            while counter <= 50:
                inf = Informationset()
                round = inf.set_sets(rnd)

                # Selection
                selected_node = self.selection(treeInf.get_root())

                # Expansion
                expanded_node = self.expansion(selected_node, rnd)

                # Simulation
                winner = self.simulation(expanded_node, round)

                # Backpropagation
                team = 0
                if rnd.player % 2 == 1:
                    team = 1
                self.backpropagation(expanded_node, winner, team, counter)
                counter += 1

            rootInf = treeInf.get_root()
            Inf_child = rootInf.get_children()
            root = tree.get_root()
            children = root.get_children()
            all += counter
            for i in Inf_child:
                card = i.get_card()
                wins = i.get_wins()
                nr_played = i.get_nr_played()
                if root.get_expanded():
                    for c in children:
                        if c.get_card() == card:
                            c.update_nr_played(nr_played)
                            c.update_wins(wins)
                            c.calculate_ucb(all)
                            root.update_wins(wins)
                            root.update_nr_played(nr_played)
                else:
                    i.calculate_ucb(counter)
                    root.add_child(i)
            root.set_expanded()
        root = tree.get_root()
        print("root_n", root.get_nr_played())
        print("root wins", root.get_wins())
        best_card = root.get_child_with_higest_visit()
        return best_card.get_card()

    def get_random_card(self, cards):
        return np.random.choice(np.flatnonzero(cards))

    def selection(self, root: Node):
        return root

    def expansion(self, node: Node, rnd: PlayerRound):
        valid_cards = rnd.get_valid_cards()
        childs = node.get_children()
        valid_cards_nr = len(const.convert_one_hot_encoded_cards_to_str_encoded_list(valid_cards))
        card = self.get_random_card(valid_cards)
        child_node = None
        if node.get_expanded():
            child_node = node.get_child_with_highest_score()
        else:
            while node.check_if_child_exists(card):
                card = self.get_random_card(valid_cards)
            if len(childs) == (valid_cards_nr - 1):
                node.set_expanded()
            child_node = Node(card)
            child_node.set_parent(node)
            node.add_child(child_node)
        return child_node

    def simulation(self, node: Node, round):
        winner = None
        round.action_play_card(node.get_card())
        while round.nr_tricks < 9:
            next_player = round.player
            if next_player == None:
                break
            cards = round.hands[next_player]
            random_card = self.get_random_card(cards)
            round.action_play_card(random_card)
        if round.points_team_0 > round.points_team_1:
            winner = 0
        elif round.points_team_1 > round.points_team_0:
            winner = 1
        return winner

    def backpropagation(self, node: Node, winner, team, counter):
        temp_node = node
        while temp_node != None:
            if winner == team:
                temp_node.increase_win()
            temp_node.increase_nr_played()
            temp_node.calculate_ucb(counter)
            temp_node = temp_node.get_parent()

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
            if played_color_cards == 9:
                pass
            elif valid_color_cards + played_color_cards == 9:
                bock_color = i
        return bock_color

    def set_card_state(self, tricks):
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