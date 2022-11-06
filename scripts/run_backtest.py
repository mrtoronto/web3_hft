import logging
import itertools
import json
import numpy as np

from datetime import datetime, timedelta

from freqtrade.optimize.backtesting import Backtesting 
from freqtrade.enums import RunMode
from freqtrade.commands.optimize_commands import setup_optimize_configuration
from scripts.gspread import insert_to_gsheet

logger = logging.getLogger(__name__)

def _calc_consecutive_losing_days(results):
    max_days = 0
    streak = 0

    for p in results['daily_profit']:
        if p[1] < 0:
            streak += 1
        else:
            streak = 0
        
        if streak > max_days:
            max_days = streak
    
    return streak

def _setup_backtest_config(
    strategy,
    strategy_path,
    config_file,
    timerange,
    wallet_size,
    stake_percentage,
    deployable_capital,
    timeframe='1h',
    export=False
):

    ### Amount to spend per trade
    stake_amount = wallet_size * stake_percentage

    ### Amount to spend per trade
    max_open_trades = int((wallet_size * deployable_capital) / stake_amount)

    config = setup_optimize_configuration({
            'strategy': strategy,
            'strategy_path':strategy_path,
            'config': [config_file],
            'timeframe': timeframe,
            'timerange': timerange
        }, RunMode.BACKTEST
    )
    config['stake_percentage'] = stake_percentage
    config['dry_run_wallet'] = wallet_size
    config['wallet_size'] = config['dry_run_wallet'] * config['tradable_balance_ratio']
    config['stake_amount'] = stake_amount
    config['max_open_trades'] = max_open_trades
    config['strategy'] = strategy
    config['config_file'] = config_file
    config['timerange'] = timerange
    config['export_to_gsheet'] = export
    config['backtest_breakdown'] = ['day']
    return config


def _run_backtest(config):
    # Initialize backtesting object
    backtesting = Backtesting(config)
    backtesting.start()

    results = backtesting.results['strategy'][config['strategy']]

    daily_rows = [[
        config['strategy'],
        config['config_file'],
        config['timerange'],
        d[0],
        d[1],
        d[1] / results['starting_balance']
    ] for d in results['daily_profit']]

    row = [
        str(datetime.now()),
        config['strategy'],
        config['config_file'],
        config['timerange'],
        results['stake_amount'],
        results['starting_balance'],
        results['max_open_trades'],
        config['stake_percentage'],
        config['stake_percentage'] * results['max_open_trades'],
        results['stoploss'],
        results['trailing_stop'],
        results['trailing_stop_positive'],
        results['trailing_stop_positive_offset'],
        results['trailing_only_offset_is_reached'],
        json.dumps(results['minimal_roi']),
        results['winning_days'],
        results['losing_days'],
        results['winning_days'] / (results['winning_days'] + results['losing_days']),
        results['wins'],
        results['losses'],
        results['wins'] / (results['wins'] + results['losses']),
        results['total_trades'],
        results['trades_per_day'],
        results['trade_count_long'],
        results['profit_total_long'],
        results['trade_count_short'],
        results['profit_total_short'],
        results['backtest_days'],
        results['profit_total'],
        results['profit_mean'],
        results['profit_median'],
        results['profit_total'] / results['backtest_days'],
        np.mean([i[1] / config['dry_run_wallet'] for i in results['daily_profit'] if i[1] > 0]),
        np.mean([i[1] / config['dry_run_wallet'] for i in results['daily_profit'] if i[1] < 0]),
        np.median([i[1] / config['dry_run_wallet'] for i in results['daily_profit'] if i[1] > 0]),
        np.median([i[1] / config['dry_run_wallet'] for i in results['daily_profit'] if i[1] < 0]),
        results['profit_factor'],
        np.percentile([i[1] for i in results['daily_profit']], 1),
        np.percentile([i[1] for i in results['daily_profit']], 5),
        np.percentile([i[1] for i in results['daily_profit']], 10),
        np.percentile([i[1] for i in results['daily_profit']], 25),
        np.median([i[1] for i in results['daily_profit']]),
        np.percentile([i[1] for i in results['daily_profit']], 75),
        np.percentile([i[1] for i in results['daily_profit']], 90),
        results['market_change'],
        results['rejected_signals'],
        results['backtest_worst_day_abs'],
        results['max_relative_drawdown'],
        (results['drawdown_end_ts'] - results['drawdown_start_ts']) / (3600 * 1000),
        _calc_consecutive_losing_days(results),
        results['holding_avg_s'] / 3600,
        results['winner_holding_avg_s'] / 3600,
        results['loser_holding_avg_s'] / 3600,
    ]

    insert_to_gsheet(
        "backtests_runs", 
        "1SXCBreiE-GT9-eKnALnuUv99wMASsrcLEmKQGeEhyL0", 
        row = row
    )

    insert_to_gsheet(
        "backtests_daily", 
        "1SXCBreiE-GT9-eKnALnuUv99wMASsrcLEmKQGeEhyL0", 
        rows = daily_rows
    )
        