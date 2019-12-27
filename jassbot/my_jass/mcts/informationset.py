import jass.base.const as const
import numpy as np
import random
import math
from jass.base.round_factory import get_round_from_player_round
from jass.base.player_round_cheating import PlayerRound
from jass.base.player_round_cheating import PlayerRoundCheating

class Informationset():
    def __init__(self):
        self.sets = []

    def set_sets(self, rnd: PlayerRound) -> PlayerRoundCheating:
        valid_cards = np.flatnonzero(rnd.hand)
        played_cards = rnd.tricks
        other_cards = np.zeros(shape=36, dtype=np.int)
        other_cards.fill(1)
        for i in valid_cards:
            other_cards[i] = 0
        for p in played_cards:
            for q in range(0, 4):
                if p[q] != -1:
                    other_cards[p[q]] = 0
        hands = np.zeros(shape=[4, 36], dtype=np.int)
        nr_cards = (9-rnd.nr_tricks)
        card_in_trick = rnd.nr_cards_in_trick
        trick = rnd.nr_tricks
        first_player = rnd.trick_first_player[trick]
        player_played = first_player
        nr_cards_rand = np.zeros(shape=4, dtype=np.int)
        nr_cards_rand.fill(nr_cards)
        if card_in_trick != 0:
            for c in range(0,card_in_trick):
                nr_cards_rand[player_played] -= 1
                player_played = const.next_player[player_played]
        for j in range(0, 4):
            if j == rnd.player:
                hands[rnd.player] = rnd.hand
            else:
                hand_player, other_cards = self.get_random_hands(other_cards, j, nr_cards_rand[j])
                hands[j] = hand_player
        return get_round_from_player_round(rnd, hands)


    def get_sets(self):
        return self.sets

    def get_random_hands(self, other_cards, player, nr_cards):
        hands_player = np.zeros(shape=36, dtype=int)
        for i in range(0, nr_cards):
            card = random.choice(np.flatnonzero(other_cards))
            other_cards[card] = 0
            hands_player[card] = 1
        return hands_player, other_cards


