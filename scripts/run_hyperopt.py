from filelock import FileLock, Timeout

from freqtrade.optimize.hyperopt import Hyperopt

import logging
from freqtrade.enums import RunMode
from freqtrade.commands.optimize_commands import setup_optimize_configuration

logger = logging.getLogger(__name__)

def _setup_hyperopt_config(
    strategy,
    config_file,
    timerange,
    wallet_size,
    stake_percentage,
    deployable_capital,
    loss,
    spaces, 
    epochs,
    timeframe='1h',
    export=False
):

    stake_amount = wallet_size * stake_percentage

    ### Amount to spend per trade
    max_open_trades = int((wallet_size * deployable_capital) / stake_amount)

    config = setup_optimize_configuration({
            'strategy': strategy,
            'config': [config_file],
            'timeframe': timeframe,
            'timerange': timerange
        }, RunMode.HYPEROPT
    )

    config['stake_percentage'] = stake_percentage
    config['dry_run_wallet'] = wallet_size
    config['wallet_size'] = config['dry_run_wallet'] * config['tradable_balance_ratio']
    config['stake_amount'] = stake_amount
    config['max_open_trades'] = max_open_trades
    config['strategy'] = strategy
    config['config_file'] = config_file
    config['timerange'] = timerange
    config['hyperopt_loss'] = loss
    config['export_to_gsheet'] = export
    config['spaces'] = spaces
    config['epochs'] = epochs
    config['hyperopt_min_trades'] = 1
    return config



def _run_hyperopt(config) -> None:
    """
    Start hyperopt script
    :param args: Cli args from Arguments()
    :return: None
    """

    logger.info('Starting freqtrade in Hyperopt mode')

    lock = FileLock(Hyperopt.get_lock_filename(config))

    try:
        with lock.acquire(timeout=1):

            # Remove noisy log messages
            logging.getLogger('hyperopt.tpe').setLevel(logging.WARNING)
            logging.getLogger('filelock').setLevel(logging.WARNING)

            # Initialize backtesting object
            hyperopt = Hyperopt(config)
            hyperopt.start()

    except Timeout:
        logger.info("Another running instance of freqtrade Hyperopt detected.")
        logger.info("Simultaneous execution of multiple Hyperopt commands is not supported. "
                    "Hyperopt module is resource hungry. Please run your Hyperopt sequentially "
                    "or on separate machines.")
        logger.info("Quitting now.")