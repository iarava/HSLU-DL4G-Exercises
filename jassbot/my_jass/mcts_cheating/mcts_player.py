# HSLU
#
# Created by Thomas Koller on 20.08.18
#

import numpy as np
import time

import jass.base.const as const
from jass.base.player_round_cheating import PlayerRoundCheating
from jass.player.player_cheating import PlayerCheating
import jass.base.round_factory as roundInf
from my_jass.mcts_cheating.Node import Node
from my_jass.mcts_cheating.Tree import Tree


class CheatingMctsPlayer(PlayerCheating):
    """
    Sample implementation of a player to play Jass.
    """
    list = dict()

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

    def play_card(self, rnd: PlayerRoundCheating) -> int:
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
        print("trump", rnd.trump)

        # get the valid cards to play
        valid_cards = rnd.get_valid_cards()
        print("Valid_cards:", const.convert_one_hot_encoded_cards_to_str_encoded_list(valid_cards))
        #card = self.montecarlo(rnd)
        #print("karte", card)
        card = self.montecarlo(rnd)

        # select a random card
        #return np.random.choice(np.flatnonzero(valid_cards))
        return card

    def montecarlo(self, rnd:PlayerRoundCheating):
        tree = Tree()

        end_time = time.time() + 0.75
        counter = 1

        while time.time() < end_time:
            #Selection
            selected_node = self.selection(tree.get_root())

            #Expansion
            expanded_node = self.expansion(selected_node, rnd)

            #Simulation
            winner = self.simulation(expanded_node,rnd)

            #Backpropagation
            team = 0
            if rnd.player % 2 == 1:
                team = 1
            self.backpropagation(expanded_node,winner,team,counter)
            counter += 1
        root = tree.get_root()
        print("root_n", root.get_nr_played())
        print("root wins", root.get_wins())
        best_card = root.get_child_with_higest_visit()
        return best_card.get_card()

    def get_random_card(self, cards):
        return np.random.choice(np.flatnonzero(cards))

    def selection(self, root: Node):
        node = root
        while node.expanded:
            highest_child = node.get_child_with_highest_score()
            node = highest_child
        return node

    def expansion(self,node: Node, rnd : PlayerRoundCheating):
        valid_cards = rnd.get_valid_cards()
        childs = node.get_children()
        valid_cards_nr = len(const.convert_one_hot_encoded_cards_to_str_encoded_list(valid_cards))
        card = self.get_random_card(valid_cards)
        while node.check_if_child_exists(card):
            card = self.get_random_card(valid_cards)
        if len(childs) == (valid_cards_nr - 1):
            node.set_expanded()
        child_node = Node(card)
        child_node.set_parent(node)
        node.add_child(child_node)
        return child_node

    def simulation(self, node: Node, rnd: PlayerRoundCheating):
        round = roundInf.get_round_from_player_round(rnd, rnd.hands)
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
                temp_node.update_win()
            temp_node.update_nr_played()
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
