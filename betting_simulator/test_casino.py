from unittest import TestCase

from betting_simulator.casino import Player


class TestHouse(TestCase):
    def test_play(self):
        self.fail()


class TestPlayer(TestCase):
    def test_bet_roi1(self):
        roi = 1
        player = Player(1_000_000)
        bet = player.bet(roi)
        self.assertEqual(10_000, bet)
        player.lost_last_game = True
        bet = player.bet(roi)
        self.assertEqual(20_000, bet)
        bet = player.bet(roi)
        self.assertEqual(40_000, bet)

    def test_bet_roi2(self):
        roi = 2
        player = Player(1_000_000)
        bet = player.bet(roi)
        print(bet)
        player.lost_last_game = True
        bet = player.bet(roi)
        print(bet)
        bet = player.bet(roi)
        print(bet)

