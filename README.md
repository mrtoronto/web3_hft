# web3_hft

## Overview

A distillation of the information in the freqtrade wiki along with Matt's personal learnings from using the library.

Github repo:
https://github.com/freqtrade/freqtrade

Documentation home:
https://www.freqtrade.io/en/stable/

## High-level notes
- [Bot execution logic](https://www.freqtrade.io/en/stable/bot-basics/#bot-execution-logic)
  - Can explain any parts in more detail
- Spot trading is available but shorting and leverage are not supported on spot trades
- Isolated futures trading allows longs, shorts and leverage
- Strategies are written in python
- Input data will be HLOCV data over whatever timeframe (1m, 5m, 15m, 30m, 1h, etc)
- Indicators can be added with the [TA Lib library](https://mrjbq7.github.io/ta-lib/)
- Strategies can be backtested and have specific numbers (stoplosses or indicators) optimized with repeated backtests (hyperoptimization)
- Fees are included in all backtesting
- 

## Freqtrade Pairlists
Each bot needs a list of trading pairs that it will check for entry signals. 

This list can be a static list of trading pairs or it can be a dynamic list generated and kept fresh using the following filters. 

### Static Pairlists
Whitelist specific pairs. Accepts regex wildcards (*/USDT will trade all USDT pairs).

```
1. Volume
  a. Top N assets by volume
  b. Minimum volume
2. Age
  a. Assets listed for at least N days
3. Offset
  a. Offset's the list produced by preceding filters
  b. Ex: Filter for top 50 by volume then offset to remove the top 10
4. Price
  a. Min and max price
  b. Max value (See appendix for explanation)
  c. Low price ratio (See appendix for explanation)
5. Spread
  a. "Removes pairs that have a difference between asks and bids above the 
      specified ratio"
6. Range Stability
  a. "Removes pairs where the difference between lowest low and highest high over 
      lookback_days days is below min_rate_of_change or above max_rate_of_change."
  b. See appendix for full explanation
7. Volatility
  a. "Volatility is the degree of historical variation of a pairs over time, it is measured by 
      the standard deviation of logarithmic daily returns"
  b. See appendix for full explanation

```

## Protections
These are more complex than pairlist filters so I'm just going to list and add a link but if you want me to explain any in detail, let me know. 

- [StoplossGuard](https://www.freqtrade.io/en/stable/plugins/#stoploss-guard)
- [MaxDrawdown](https://www.freqtrade.io/en/stable/plugins/#maxdrawdown)
- [LowProfitPairs](https://www.freqtrade.io/en/stable/plugins/#low-profit-pairs)
- [CooldownPeriod](https://www.freqtrade.io/en/stable/plugins/#cooldown-period)

I haven't used these yet but they sound helpful. Full example in the appendix.


## Appendix

### Price Filter - Max value and low price ratio
![image](https://user-images.githubusercontent.com/34576341/202917867-c47da745-9d1e-474f-a81b-b3bbb42dfdf0.png)

### Range Stability Filter
![image](https://user-images.githubusercontent.com/34576341/202918023-4ebe566d-71e2-4e89-9d9c-291c92eef268.png)

### Volatility filter
![image](https://user-images.githubusercontent.com/34576341/202917996-616ea76e-3939-404c-a4dd-bce5341632ad.png)

### Protections example
![image](https://user-images.githubusercontent.com/34576341/202918129-fe24a73b-650b-4189-95af-1252056dc829.png)
