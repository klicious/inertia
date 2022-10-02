from multiprocessing import Pool
import random


class House:
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
        self._win_range: int = int(House.BILLION * self.win_rate)
        self._tie_range: int = int(House.BILLION * self.tie_rate) + self._win_range
        self._lose_range: int = House.BILLION

    def play(self, bet: float) -> float:
        r = random.uniform(0, House.BILLION)
        return bet * self.return_on_investment if r < self._win_range else bet if r < self._tie_range else 0


class Player:

    def __init__(
            self,
            budget: float = 0,
    ) -> None:
        self.initial_budget: float = budget
        self.balance: float = budget
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
        self.max_value: float = budget
        self.max_value_draw_down_pcnt: float = 0
        self.games_played: int = 0

    def __str__(self):
        return str(self.__dict__)

    def play(self, house: House):
        bet = self.bet()
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
    def bet(self) -> float:
        # bet = min(self.last_bet * 2, self.balance) if self.lost_last_game else self.balance * 0.01
        bet = min(self.last_bet * 2, self.balance) if self.lost_last_game else min(self.balance * 0.01, 1_000_000_000)
        self.cumulative_bet += bet
        bet = self._stop_loss(bet)
        self.balance -= bet
        self.last_bet = bet
        if self.max_bet < bet:
            self.max_bet = bet
        return bet

    def _reset_bet(self) -> None:
        self.lost_last_game = False
        self.last_bet = 0
        self.cumulative_bet = 0

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


def simulate_with_house(win_rate: float = 0.5, tie_rate: float = 0, roi: float = 2):
    game_repetition = 1_000_000
    house = House(win_rate=win_rate, tie_rate=tie_rate, return_on_investment=roi)
    player = Player(budget=1_000_000)
    for j in range(0, game_repetition):
        if player.is_broke():
            break
        player.play(house=house)
    return house, player

def simulate(roi: float = 2):
    steps: int = 200
    win_rates = [0.5545 + (x / 10_000) for x in range(0, steps)]
    with Pool() as pool:
        return pool.map(simulate_with_house, win_rates)


if __name__ == "__main__":
    max_broken_rate: float = 0
    for i in range(0, 1_000_000):
        print(f"Attempt {i + 1}...")
        simulation_results = simulate()
        for simulation in simulation_results:
            house, player = simulation
            if player.is_broke() and house.win_rate > max_broken_rate:
                max_broken_rate = house.win_rate
                print(f"max broken rate updated to {max_broken_rate}")






