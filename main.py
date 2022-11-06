from dateutil import parser
from scripts.dynam2staticPL import convert_pairlist
from scripts.run_backtest import _run_backtest, _setup_backtest_config
from scripts.run_hyperopt import _run_hyperopt, _setup_hyperopt_config
from scripts.run_trade import _run_trade
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Convert dynamic pairlist to static pairlist')
    parser.add_argument('--task', type=str, help='Task to perform')
    parser.add_argument('--config', help='config file path', type=str)
    parser.add_argument('--strategy', help='strategy name', type=str)
    parser.add_argument('--strategy_path', help='strategy path', type=str)
    parser.add_argument('--timerange', help='timerange', type=str)
    parser.add_argument('--wallet_size', help='wallet size', type=float)
    parser.add_argument('--stake_percentage', help='stake percentage', type=float)
    parser.add_argument('--deployable_capital', help='deployable capital', type=float)
    parser.add_argument('--loss', help='loss function', type=str)
    parser.add_argument('--epochs', help='epochs to hyperoptimize for', type=int)
    parser.add_argument('--hyperopt_spaces', help='spaces to optimize', type=str)
    parser.add_argument('--start_date', help='start date', type=str)
    return parser.parse_args()

def main():
    args = parse_args()
    if args.task == 'pairlist':
        convert_pairlist(args.config)
    elif args.task == 'backtest':
        config = _setup_backtest_config(
            args.strategy,
            args.strategy_path,
            args.config,
            args.timerange,
            args.wallet_size,
            args.stake_percentage,
            args.deployable_capital,
            timeframe='1h',
            export=False
        )
        _run_backtest(config)

    elif args.task == 'hyperopt':
        config = _setup_hyperopt_config(
            strategy=args.strategy,
            strategy_path=args.strategy_path,
            config_file=args.config,
            timerange=args.timerange,
            wallet_size=args.wallet_size,
            stake_percentage=args.stake_percentage,
            deployable_capital=args.deployable_capital,
            loss=args.loss,
            spaces=" ".join(args.hyperopt_spaces.split(",")),
            timeframe='1h',
            epochs=args.epochs,
            export=False
        )
        _run_hyperopt(config)

if __name__ == '__main__':  # pragma: no cover
    main()
