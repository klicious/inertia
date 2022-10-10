from datetime import datetime, timedelta
from functools import partial

import csv
import json
import os
import random
import numpy as np
import parmap
from tqdm import tqdm


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
        r = random.randint(1, House.MILLION)
        return (
            bet * (1 + self.return_on_investment)
            if r <= self._win_range
            else bet
            if r <= self._tie_range
            else 0
        )


class Player:
    def __init__(
        self,
        budget: float = 0,
    ) -> None:
        self.name: str = "not applicable"
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
        if result > bet:
            self._won()
        elif result == bet:
            self._tied()
        else:
            self._lost()
        self.balance += result
        # draw down calculation
        self._update_max_value_draw_down()
        # game count
        self.games_played += 1
        # break double game count tracker
        self._track_double_balance()

    def _won(self):
        self.win += 1
        self._reset_bet()
        self.losing_streak = 0
        self.lost_last_game = False

    def _tied(self):
        self.tie += 1

    def _lost(self):
        self.loss += 1
        self.losing_streak += 1
        self.max_losing_streak = max(self.max_losing_streak, self.losing_streak)
        self.lost_last_game = True

    def bet(self, _roi: float = 1) -> float:
        bet = min(self._required_bet(_roi), self.balance)
        bet = self._stop_loss(bet)
        if not self.lost_last_game:
            self.initial_bet = bet
        self.cumulative_bet += bet
        self.balance -= bet
        self.last_bet = bet
        if self.max_bet < bet:
            self.max_bet = bet
        return bet

    def _update_max_value_draw_down(self) -> None:
        self.max_value = max(self.max_value, self.balance)
        draw_down_pcnt = ((self.balance / self.max_value) - 1) * 100
        self.max_value_draw_down_pcnt = min(
            draw_down_pcnt, self.max_value_draw_down_pcnt
        )

    def _track_double_balance(self) -> None:
        if self.balance < self.target_balance:
            return
        game_count_till_double: int = self.games_played - self.last_double_balanced_game
        self.double_balance_game_lengths.append(game_count_till_double)
        self.target_balance *= 2
        self.last_double_balanced_game = self.games_played

    def _required_bet(self, roi: float = 1) -> float:
        pass

    def _reset_bet(self) -> None:
        self.lost_last_game = False
        self.last_bet = 0
        self.cumulative_bet = 0
        self.initial_bet = 0

    def _stop_loss(self, bet: float) -> float:
        return bet

    def pnl(self):
        pnl: float = self.balance - self.initial_budget
        pnl_percentage: float = (self.balance / self.initial_budget - 1) * 100
        return {
            "pnl": pnl,
            "pnl_percentage": pnl_percentage,
        }

    def is_broke(self) -> bool:
        pass


class SteadyOnePlayer(Player):
    def __init__(self, budget: float = 0) -> None:
        super().__init__(budget)
        self.name: str = "Steady one player"

    def _required_bet(self, _roi: float = 1) -> float:
        return min(self.balance * 0.01, 100_000_000)

    def is_broke(self) -> bool:
        return self.balance <= self.initial_budget * 0.5


class MartingaleSystemPlayer(Player):
    def __init__(self, budget: float = 0) -> None:
        super().__init__(budget)
        self.name: str = "Martingale system player"

    def _required_bet(self, roi: float = 1) -> float:
        if not self.lost_last_game:
            return min(self.balance * 0.01 / roi, 100_000_000)
        required_return: float = self.cumulative_bet + (self.initial_bet * roi)
        return required_return / roi

    def _stop_loss(self, bet: float) -> float:
        return bet

    def is_broke(self) -> bool:
        return self.balance <= self.initial_budget * 0.1


class MartingaleSystemStopLossPlayer(MartingaleSystemPlayer):
    def __init__(self, budget: float = 0) -> None:
        super().__init__(budget)
        self.name: str = "Martingale system stop-loss player"

    def _stop_loss(self, bet: float) -> float:
        max_bet = self.balance * 0.1
        if (self.cumulative_bet + bet) <= max_bet:
            return bet
        self._reset_bet()
        return max_bet


def track_game_balances(repetition: int, house: House, player: Player):
    balances = [player.balance]
    for _ in range(0, repetition):
        player.play(house=house)
        balances.append(player.balance)
        if player.is_broke():
            break
    return balances


def simulate_games(repetition: int, house: House, player: Player):
    _balances = [player.balance]
    for _ in range(0, repetition):
        player.play(house=house)
        # _balances.append(player.balance)
        if player.is_broke():
            break
    return house, player, _balances


def simulate_with_player(
    player: Player,
    win_rate: float = 0.5,
    tie_rate: float = 0,
    roi: float = 1,
    game_size: int = 1_000_000,
):
    house = House(win_rate=win_rate, tie_rate=tie_rate, return_on_investment=roi)
    return simulate_games(game_size, house, player)


def simulate_martingale_system_player(
    win_rate: float = 0.5,
    tie_rate: float = 0,
    roi: float = 1,
    game_size: int = 1_000,
    repetition: int = 10_000,
):
    players = [MartingaleSystemPlayer(budget=1_000_000) for _ in range(0, repetition)]
    return [
        simulate_with_player(p, win_rate, tie_rate, roi, game_size) for p in players
    ]


def simulate_martingale_stoploss_player(
    win_rate: float = 0.5,
    tie_rate: float = 0,
    roi: float = 1,
    game_size: int = 1_000,
    repetition: int = 10_000,
):
    players = [
        MartingaleSystemStopLossPlayer(budget=1_000_000) for _ in range(0, repetition)
    ]
    return [
        simulate_with_player(p, win_rate, tie_rate, roi, game_size) for p in players
    ]


def simulate_steady_one_player(
    win_rate: float = 0.5,
    tie_rate: float = 0,
    roi: float = 1,
    game_size: int = 1_000,
    repetition: int = 10_000,
):
    players = [SteadyOnePlayer(budget=1_000_000) for _ in range(0, repetition)]
    return [
        simulate_with_player(p, win_rate, tie_rate, roi, game_size) for p in players
    ]


def simulate_multiple_rates(simulation_func, roi: float = 1):
    steps: int = 30
    step: float = 0.01
    initial_rate: float = 0.5
    win_rates = []
    for _ in range(0, 10):
        win_rates += [initial_rate + (step * x) for x in range(0, steps)]
    return parmap.map(
        partial(simulation_func, roi=roi),
        win_rates,
        pm_pbar={
            "desc": f"Simulating {steps} steps of rates starting from {round(initial_rate, 2)}. (Each step being {round(step, 4)})"
        },
    )


def _calculate_game_result(rate: float, player_name: str, roi: float):
    players = _load_players(player_name, roi, rate)
    print("=========================================")
    mvdds = [p.max_value_draw_down_pcnt for p in players]
    mvdd_min = round(np.min(mvdds), 4)
    mvdd_max = round(np.max(mvdds), 4)
    mvdd_std = round(np.std(mvdds), 4)
    mvdd_mean = round(np.mean(mvdds), 4)
    print(
        f"@ rate[{round(rate, 4)}] with sample size[{len(mvdds)}] :: MVDD :: min[{mvdd_min}] max[{mvdd_max}] std[{mvdd_std}] mean[{mvdd_mean}]"
    )
    pnls = [((p.balance - p.initial_budget) / p.initial_budget) * 100 for p in players]
    pnl_min = round(np.min(pnls), 4)
    pnl_max = round(np.max(pnls), 4)
    pnl_std = round(np.std(pnls), 4)
    pnl_mean = round(np.mean(pnls), 4)
    print(
        f"@ rate[{round(rate, 4)}] with sample size[{len(pnls)}] :: PnL :: min[{pnl_min}] max[{pnl_max}] std[{pnl_std}] mean[{pnl_mean}]"
    )
    double_balance_game_lengths = sum(
        [p.double_balance_game_lengths for p in players], []
    )
    if not double_balance_game_lengths:
        double_balance_game_lengths.append(0)
    double_balance_game_length_min = round(np.min(double_balance_game_lengths), 4)
    double_balance_game_length_max = round(np.max(double_balance_game_lengths), 4)
    double_balance_game_length_std = round(np.std(double_balance_game_lengths), 4)
    double_balance_game_length_mean = round(np.mean(double_balance_game_lengths), 4)
    double_balance_game_length_count = len(double_balance_game_lengths)
    print(
        f"@ rate[{round(rate, 4)}] with sample size[{len(pnls)}] :: Double game lengths :: min[{double_balance_game_length_min}] max[{double_balance_game_length_max}] std[{double_balance_game_length_std}] mean[{double_balance_game_length_mean}] count[{double_balance_game_length_count}]"
    )
    return {
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


def _write_game_results_to_file(rates: list, player_name: str, roi: float):
    results = parmap.map(
        partial(
            _calculate_game_result,
            player_name=player_name,
            roi=roi,
        ),
        rates,
        pm_pbar={
            "desc": f"Calculating {len(rates)} results of {player_name} with roi {roi} to file"
        },
    )
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
    directory = os.path.join("results", "stats", player_name)
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = f"{player_name.replace(' ', '_')}_rate_50-80_roi_{roi}.csv"
    with open(
        os.path.join(directory, filename),
        "w",
    ) as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)


def _to_balances_statistics(player_name: str, roi: float, rate: float, index: int):
    balances = _load_balances(player_name, roi, rate, index)
    return {
        "sample_size": len(balances),
        "index": index,
        "min": np.min(balances),
        "max": np.max(balances),
        "mean": np.mean(balances),
        "std": np.std(balances),
    }


def _write_game_balances_track_to_file(rates: list, player_name: str, roi: float):
    headers = ["index", "min", "max", "mean", "std"]
    for rate in tqdm(rates, desc="Writing game balances track to file."):
        path = os.path.join("game_balances", "raw")
        indexes = []
        prefix = f"{player_name.replace(' ', '_')}_rate_{round(rate, 2)}_roi_{round(roi, 2)}_index_"
        for f in os.listdir(path):
            if f.startswith(prefix):
                split_filename = f.split("_")
                index: int = int(split_filename[-3])
                indexes.append(index)
        if not indexes:
            return
        rows = [_to_balances_statistics(player_name, roi, rate, i) for i in indexes]
        directory = os.path.join("game_balances", "stats")
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = os.path.join(
            directory,
            f"{player_name.replace(' ', '_')}_rate_{rate}_roi_{roi}_game_balances.csv",
        )
        with open(
            filename,
            "w",
        ) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)


def simulate_and_save(
    simulation_with_player_func,
    roi: float,
    player_name: str,
):
    simulation_results = simulate_multiple_rates(simulation_with_player_func, roi)
    rates = set()
    rate_players_dict = {}
    for simulations in tqdm(
        simulation_results,
        desc=f"Converting data produced from simulations of {player_name}",
    ):
        for simulation in simulations:
            _house, _player, _balances = simulation
            win_rate = _house.win_rate
            rates.add(win_rate)
            players = rate_players_dict.get(win_rate, [])
            players.append(_player)
            rate_players_dict[win_rate] = players
            # for index, balance in enumerate(_balances):
            #     index_balances = _load_balances(player_name, roi, win_rate, index)
            #     index_balances.append(balance)
            #     _save_index_balances(player_name, roi, win_rate, index, index_balances)
    win_rates = [r for r, pl in rate_players_dict.items()]
    parmap.map(
        partial(
            _save_players_from_dict,
            player_name=player_name,
            roi=roi,
            rate_players_dict=rate_players_dict,
        ),
        win_rates,
        pm_pbar={
            "desc": f"Saving {len(win_rates)} rates of data produced from {player_name} simulations"
        },
    )
    _write_game_results_to_file(list(rates), player_name, roi)
    # _write_game_balances_track_to_file(list(rates), player_name, roi)


def _save_players_from_dict(
    win_rate: float, roi: float, player_name: str, rate_players_dict: dict
):
    _players = rate_players_dict.get(win_rate, [])
    players = _load_players(player_name, roi, win_rate)
    players += _players
    _save_players(player_name, roi, win_rate, players)


def _get_full_filepath(directory: str, filename: str):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return os.path.join(
        directory,
        filename,
    )


def _save(filename: str, data):
    with open(filename, "w") as file:
        json.dump(data, file)


def _load(filename: str, default=None):
    if not os.path.isfile(filename):
        return [] if default is None else default
    with open(filename, "r") as file:
        return json.load(file)


def _get_saved_index_balances_filename(
    player_name: str, roi: float, win_rate: float, index: int
):
    win_rate_str = str(round(win_rate, 2))
    roi_str = str(round(roi, 2))
    directory = os.path.join(
        "game_balances",
        "raw",
        "index_balances",
        player_name,
        f"roi_{roi_str}",
        f"win_rate_{win_rate_str}",
    )
    filename = f"{player_name.replace(' ', '_')}_rate_{win_rate_str}_roi_{roi_str}_index_{index}_game_balances.json"
    return _get_full_filepath(directory, filename)


def _save_index_balances(
    player_name: str, roi: float, win_rate: float, index: int, balances: list
) -> None:
    filename = _get_saved_index_balances_filename(player_name, roi, win_rate, index)
    _save(filename, balances)


def _load_balances(player_name: str, roi: float, win_rate: float, index: int) -> list:
    filename = _get_saved_index_balances_filename(player_name, roi, win_rate, index)
    return _load(filename)


def _get_saves_players_filename(player_name: str, roi: float, win_rate: float) -> str:
    win_rate_str = str(round(win_rate, 2))
    roi_str = str(round(roi, 2))
    directory = os.path.join("results", "players", player_name, f"roi_{roi_str}")
    filename = f"{player_name.replace(' ', '_')}_rate_{win_rate_str}_roi_{roi_str}_players.json"
    return _get_full_filepath(directory, filename)


def _save_players(player_name: str, roi: float, win_rate: float, players: list) -> None:
    filename = _get_saves_players_filename(player_name, roi, win_rate)
    _save(filename, players)


def _load_players(player_name: str, roi: float, win_rate: float) -> list:
    filename = _get_saves_players_filename(player_name, roi, win_rate)
    return _load(filename, [])


def run_multiple_rates_on_player_and_roi(
    _repetition: int,
    _rate_index_balances_dict: dict,
    _rate_player_dict: dict,
    _simulation_function,
    _roi: float,
    _player_name: str,
):
    for index in range(0, _repetition):
        start_time: datetime = datetime.now()
        attempt = index + 1
        print(
            f"Attempt {attempt} @ {start_time} on {_simulation_function.__name__} with roi {_roi} ..."
        )
        simulate_and_save(
            simulate_steady_one_player,
            _roi,
            _player_name,
        )
        end_time: datetime = datetime.now()
        simulation_timedelta: timedelta = end_time - start_time
        print(f"Attempt {attempt} took [{simulation_timedelta}] to complete")


def run_multiple_rates_on_players_and_rois():
    rois = [1, 2, 3]
    simulation_functions = [
        simulate_martingale_system_player,
        simulate_martingale_stoploss_player,
        simulate_steady_one_player,
    ]
    player_names: dict = {
        simulate_martingale_system_player: MartingaleSystemPlayer().name,
        simulate_martingale_stoploss_player: MartingaleSystemStopLossPlayer().name,
        simulate_steady_one_player: SteadyOnePlayer().name,
    }
    simulation_func_roi_rate_player_dict = {}
    simulation_func_roi_rate_index_balances_dict = {}
    for index in range(0, 1_000_000):
        for simulation_function in simulation_functions:
            roi_rate_player_dict = simulation_func_roi_rate_player_dict.get(
                simulation_function, {}
            )
            roi_rate_index_balances_dict = (
                simulation_func_roi_rate_index_balances_dict.get(
                    simulation_function, {}
                )
            )
            player_name = player_names.get(simulation_function)
            for roi in rois:
                rate_player_dict = roi_rate_player_dict.get(roi, {})
                rate_index_balances_dict = roi_rate_index_balances_dict.get(roi, {})
                start_time: datetime = datetime.now()
                attempt = index + 1
                print(
                    f"Attempt {attempt} @ {start_time} on {simulation_function.__name__} with roi {roi} ..."
                )
                simulate_and_save(
                    simulation_function,
                    roi,
                    player_name,
                )
                end_time: datetime = datetime.now()
                simulation_timedelta: timedelta = end_time - start_time
                print(f"Attempt {attempt} took [{simulation_timedelta}] to complete")
                roi_rate_player_dict[roi] = rate_player_dict
                roi_rate_index_balances_dict[roi] = rate_index_balances_dict
            simulation_func_roi_rate_player_dict[
                simulation_function
            ] = roi_rate_player_dict
            simulation_func_roi_rate_index_balances_dict[
                simulation_function
            ] = roi_rate_index_balances_dict


if __name__ == "__main__":
    run_multiple_rates_on_players_and_rois()

    # rate_player_dict: dict = {}
    # roi = 1
    # player_name = SteadyOnePlayer().name
    # simulation_function = simulate_steady_one_player
    # run_multiple_rates_on_player_and_roi(
    #     1_000_000, rate_player_dict, simulation_function, roi, player_name
    # )

    # deltas = []
    # for i in range(0, 100):
    #     start_timestamp: float = datetime.now().timestamp()
    #     house, player = simulate_martingale_system_player(win_rate=0.8)
    #     end_timestamp: float = datetime.now().timestamp()
    #     delta: float = end_timestamp - start_timestamp
    #     deltas.append(delta)
    #     print(f"time delta: {delta}, player mvdd: {player.max_value_draw_down_pcnt} games played [{player.games_played}] is broke[{player.is_broke()}]")
    # mean = np.mean(deltas)
    # print(f"Average time delta: {mean}")
