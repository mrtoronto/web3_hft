import json
import logging
from typing import Any, Dict

import rapidjson

from freqtrade.configuration import setup_utils_configuration
from freqtrade.enums import RunMode
from freqtrade.resolvers import ExchangeResolver
from freqtrade.plugins.pairlistmanager import PairListManager

def convert_pairlist(filename):
    print(f'Converting dynamic pairlist {filename} to static pairlist')
    args = {'config': [filename]}
    config = setup_utils_configuration(args, RunMode.UTIL_EXCHANGE)

    exchange = ExchangeResolver.load_exchange(config['exchange']['name'], config, validate=False)

    quote_currencies = args.get('quote_currencies')
    if not quote_currencies:
        quote_currencies = [config.get('stake_currency')]
    results = {}
    for curr in quote_currencies:
        config['stake_currency'] = curr
        pairlists = PairListManager(exchange, config)
        pairlists.refresh_pairlist()
        results[curr] = pairlists.whitelist

    for curr, pairlist in results.items():
        if not args.get('print_one_column', False) and not args.get('list_pairs_print_json', False):
            print(f"Pairs for {curr}: ")

        if args.get('print_one_column', False):
            print('\n'.join(pairlist))
        elif args.get('list_pairs_print_json', False):
            print(rapidjson.dumps(list(pairlist), default=str))
        else:
            print(pairlist)

    with open(filename, 'r') as f:
        dynam_json = json.load(f)
    static_json = dynam_json.copy()
    static_json['exchange']['pair_whitelist'] = results[config.get('stake_currency')]
    static_json['pairlists'] = [{'method': 'StaticPairList'}]

    static_filename = filename.replace('dynamic', 'static')

    with open(static_filename, 'w') as f:
        json.dump(static_json, f, indent=4)

    