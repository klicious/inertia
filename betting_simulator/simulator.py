import collections
import random
import numpy as np
import json


def unique(list1):
    x = np.array(list1)
    return np.unique(x)


def play_games(_budget: int, _total_bet: int, _max_bet: int):
    bet_on_win = True
    _win_records = []
    for _i in range(0, 10000):
        bet_on_win = not bet_on_win
        # ends the game is there is no budget left
        if _budget == 0:
            return

        # place a new bet
        current_bet = 0
        if len(_win_records) != 0:
            won_last_game = _win_records[-1]
            if won_last_game:
                current_bet = 0
            else:
                current_bet = _total_bet
        current_bet = current_bet if current_bet > 0 else bet
        _max_bet = _max_bet if _max_bet >= current_bet else current_bet

        # play the game
        r = random.uniform(0, 10)
        game_won = True if r > 5 else False
        # game_won = game_won if bet_on_win else not game_won

        wins_in_last_three_game = [win for win in _win_records[-3:] if win is True]
        # lost last three games, so reset the cycle
        if len(wins_in_last_three_game) == 0 and len(_win_records) >= 3 and current_bet != bet:
            _win_records.append(game_won)
            continue

        if game_won:
            _budget += current_bet
            _total_bet = 0
            _win_records.append(True)
            win_records[True] = win_records[True] + 1
        else:
            _budget -= current_bet
            _total_bet += current_bet
            _win_records.append(False)
            win_records[False] = win_records[False] + 1
        # print(f"current budget[{_budget}], current bet[{current_bet}], game result[{'win' if game_won else 'loss'}]")
    return _max_bet


win_records = {True: 0, False: 0}
max_bets = {}
initial_budget = 400_000
bet = 10_000
for i in range(0, 10000):
    budget = initial_budget
    total_bet = 0
    max_bet = 0
    max_bet = play_games(budget, total_bet, max_bet)
    max_bets[max_bet] = max_bets[max_bet] + 1 if max_bet in max_bets else 1

win_count = len([won for won in win_records if won is True])

sorted_max_bets = collections.OrderedDict({k: v for k, v in sorted(max_bets.items(), key=lambda item: item[1])})
print(json.dumps(sorted_max_bets, indent=4))

# print(f"budget[{budget}]")
# print(f"revenue[{budget - initial_budget}]")
# print(f"max bet[{max_bet}]")
# print(f"total_bet[{total_bet}]")
# print(f"win record: {win_count}/{len(win_records)}")
# print(f"win rate: {win_count / len(win_records) * 100}")
