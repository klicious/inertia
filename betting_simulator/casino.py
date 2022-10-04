import csv
from functools import partial
from multiprocessing import Pool
import numpy as np
import random


class House:
    THOUSAND = 1_000
    MILLION = 1_000_000
    BILLION = 1_000_000_000

    def __init__(
            self,
            win_rate: float,
            tie_rate: float,
            return_on_investment: float,
    ) -> None:
        if win_rate + tie_rate > 1:
            raise Exception("win rate + tie rate cannot exceed 1")
        self.win_rate: float = win_rate
        self.tie_rate: float = tie_rate
        self.return_on_investment: float = return_on_investment
        self._win_range: int = int(House.MILLION * self.win_rate)
        self._tie_range: int = int(House.MILLION * self.tie_rate) + self._win_range
        self._lose_range: int = House.MILLION

    def play(self, bet: float) -> float:
        r = random.SystemRandom().randint(1, House.MILLION)
        return bet * (1 + self.return_on_investment) if r < self._win_range else bet if r < self._tie_range else 0


class Player:

    def __init__(
            self,
            budget: float = 0,
    ) -> None:
        self.initial_budget: float = budget
        self.balance: float = budget
        self.target_balance: float = budget * 2
        self.last_double_balanced_game: int = 0
        self.double_balance_game_lengths = []
        self.min_balance: float
        self.max_balance: float
        self.last_bet: float = 0
        self.max_bet: float = 0
        self.win: int = 0
        self.tie: int = 0
        self.loss: int = 0
        self.lost_last_game: bool = False
        self.losing_streak: int = 0
        self.max_losing_streak: int = 0
        self.cumulative_bet: float = 0
        self.initial_bet: float = 0
        self.max_value: float = budget
        self.max_value_draw_down_pcnt: float = 0
        self.games_played: int = 0

    def __str__(self):
        return str(self.__dict__)

    def play(self, house: House):
        bet = self.bet(house.return_on_investment)
        result = house.play(bet)
        won: bool = result > bet
        if self.lost_last_game and not won:
            self.losing_streak += 1
            if self.max_losing_streak < self.losing_streak:
                self.max_losing_streak = self.losing_streak
        self.lost_last_game = not won
        if won:
            self.win += 1
            self._reset_bet()
            self.losing_streak = 0
        elif result == bet:
            self.tie += 1
        else:
            self.loss += 1
        self.balance += result
        if self.balance > self.max_value:
            self.max_value = self.balance
        else:
            draw_down_pcnt = ((self.balance / self.max_value) - 1) * 100
            if draw_down_pcnt < self.max_value_draw_down_pcnt:
                self.max_value_draw_down_pcnt = draw_down_pcnt
        self.games_played += 1
        if self.balance >= self.target_balance:
            games_till_double: int = self.games_played - self.last_double_balanced_game
            self.double_balance_game_lengths.append(games_till_double)
            self.target_balance *= 2
            self.last_double_balanced_game = self.games_played

    def bet(self, roi: float = 1) -> float:
        # bet = min(self.last_bet * 2, self.balance) if self.lost_last_game else self.balance * 0.01
        bet = self._required_bet(roi)
        if not self.lost_last_game:
            self.initial_bet = bet
        self.cumulative_bet += bet
        bet = self._stop_loss(bet)
        self.balance -= bet
        self.last_bet = bet
        if self.max_bet < bet:
            self.max_bet = bet
        return bet

    def _required_bet(self, roi: float = 1) -> float:
        if not self.lost_last_game:
            return min(self.balance * 0.01 / roi, 100_000_000)
        required_return: float = self.cumulative_bet + (self.initial_bet * roi)
        return required_return / roi
    def _reset_bet(self) -> None:
        self.lost_last_game = False
        self.last_bet = 0
        self.cumulative_bet = 0
        self.initial_bet = 0

    def _stop_loss(self, bet: float) -> float:
        max_bet = self.balance * 0.1
        if self.cumulative_bet <= max_bet:
            return bet
        self._reset_bet()
        return max_bet

    def pnl(self):
        pnl: float = self.balance - self.initial_budget
        pnl_percentage: float = (self.balance / self.initial_budget - 1) * 100
        return {
            "pnl": pnl,
            "pnl_percentage": pnl_percentage,
        }

    def is_broke(self):
        return self.balance <= self.initial_budget * 0.1


def simulate_games(repetition: int, house: House, player: Player):
    broken_rate = False
    for j in range(0, repetition):
        if player.is_broke():
            # print(f"player is broke after {j} games @ win rate: {round(house.win_rate, 4)}. initial budget: {player.initial_budget} balance: {player.balance}")
            broken_rate = True
            break
        player.play(house=house)
    if broken_rate:
        print(f"win rate {round(house.win_rate, 4)} does not work. max losing streak: {player.max_losing_streak}")
        print(player)
        return
    print(
        f"After {repetition} game plays @ win rate {round(house.win_rate, 4)} :: mvdd with {round(player.max_value_draw_down_pcnt, 4)} :: player exits with {player.pnl()}")
    print(player)


def simulate_with_house(win_rate: float = 0.5, tie_rate: float = 0, roi: float = 1, game_size: int = 1_000_000):
    house = House(win_rate=win_rate, tie_rate=tie_rate, return_on_investment=roi)
    player = Player(budget=1_000_000)
    for j in range(0, game_size):
        if player.is_broke():
            break
        player.play(house=house)
    return house, player


def simulate_multiple_rates(roi: float = 1):
    steps: int = 30
    # win_rates = [0.5682 + (x / 10_000) for x in range(0, steps)]
    win_rates = []
    for i in range(0, 1000):
        win_rates += [0.5 + (0.01 * x) for x in range(0, steps)]
    with Pool() as pool:
        return pool.map(partial(simulate_with_house, roi=roi), win_rates)


def run_multiple_rates():
    rate_player_dict = {}
    max_broken_rate: float = 0
    roi = 2
    for i in range(0, 1_000_000):
        print(f"Attempt {i + 1}...")
        simulation_results = simulate_multiple_rates(roi)
        for simulation in simulation_results:
            house, player = simulation
            if player.is_broke() and house.win_rate > max_broken_rate:
                max_broken_rate = house.win_rate
                print(f"max broken rate updated to {max_broken_rate}")
            players = rate_player_dict[house.win_rate] if house.win_rate in rate_player_dict else []
            players.append(player)
            rate_player_dict[house.win_rate] = players
        results = []
        for rate, players in rate_player_dict.items():
            print("=========================================")
            mvdds = [p.max_value_draw_down_pcnt for p in players]
            mvdd_min = round(np.min(mvdds), 4)
            mvdd_max = round(np.max(mvdds), 4)
            mvdd_std = round(np.std(mvdds), 4)
            mvdd_mean = round(np.mean(mvdds), 4)
            print(
                f"@ rate[{round(rate, 4)}] with sample size[{len(mvdds)}] :: MVDD :: min[{mvdd_min}] max[{mvdd_max}] std[{mvdd_std}] mean[{mvdd_mean}]")
            pnls = [(p.balance / p.initial_budget) * 100 for p in players]
            pnl_min = round(np.min(pnls), 4)
            pnl_max = round(np.max(pnls), 4)
            pnl_std = round(np.std(pnls), 4)
            pnl_mean = round(np.mean(pnls), 4)
            print(
                f"@ rate[{round(rate, 4)}] with sample size[{len(pnls)}] :: PnL :: min[{pnl_min}] max[{pnl_max}] std[{pnl_std}] mean[{pnl_mean}]")
            double_balance_game_lengths = sum([p.double_balance_game_lengths for p in players], [])
            double_balance_game_length_min = round(np.min(double_balance_game_lengths), 4)
            double_balance_game_length_max = round(np.max(double_balance_game_lengths), 4)
            double_balance_game_length_std = round(np.std(double_balance_game_lengths), 4)
            double_balance_game_length_mean = round(np.mean(double_balance_game_lengths), 4)
            double_balance_game_length_count = len(double_balance_game_lengths)
            print(
                f"@ rate[{round(rate, 4)}] with sample size[{len(pnls)}] :: Double game lengths :: min[{double_balance_game_length_min}] max[{double_balance_game_length_max}] std[{double_balance_game_length_std}] mean[{double_balance_game_length_mean}] count[{double_balance_game_length_count}]")
            result = {
                "sample_size": len(mvdds),
                "rate": round(rate, 4),
                "mvdd_min": mvdd_min,
                "mvdd_max": mvdd_max,
                "mvdd_std": mvdd_std,
                "mvdd_mean": mvdd_mean,
                "pnl_min": pnl_min,
                "pnl_max": pnl_max,
                "pnl_std": pnl_std,
                "pnl_mean": pnl_mean,
                "double_balance_game_length_min": double_balance_game_length_min,
                "double_balance_game_length_max": double_balance_game_length_max,
                "double_balance_game_length_std": double_balance_game_length_std,
                "double_balance_game_length_mean": double_balance_game_length_mean,
            }
            results.append(result)
        headers = [
            "sample_size",
            "rate",
            "mvdd_min",
            "mvdd_max",
            "mvdd_std",
            "mvdd_mean",
            "pnl_min",
            "pnl_max",
            "pnl_std",
            "pnl_mean",
            "double_balance_game_length_min",
            "double_balance_game_length_max",
            "double_balance_game_length_std",
            "double_balance_game_length_mean",
        ]
        with open(f"betting_simulation_result_rate_50-80_roi_{roi}.csv", 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(results)


if __name__ == "__main__":
    run_multiple_rates()
