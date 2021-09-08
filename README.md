# Options Backtesting (example)

## Strategy description

We used our tool to backtest 7dte put creadit spread strategy on SPX. \n
Days to expiration: 7
Strategy: Put credit spread
Actions:
Short leg: Sell one put contract at 10 delta and collect credit
Long leg: but one put contract at 6 delta and pay debit

Total Premium Collected (max profit) = short leg credit collected - long leg debit paid
Stop loss criteria: Loss = 3x Total Premium Collected

## Result

![alt text](https://github.com/pareto-digital/OptionsBacktesting/blob/main/spx%20pcs%20vs%20spy%20example.png?raw=true)

Between Jan. 2016 to June 2021, total return of the strategy is $66,400 (not consider commision fees), and maximum drawdown was $1,300 in March 2020. The average buying power effect was only $1,0000+, resulting an ROI of 500%+.

We compare this strategy with holding 100 shares of SPY. The purchasing cost was $20,000 in Jan. 2016. During the same period, SPY rised from $200 to $400 (100% ROI) and max draw down of $10,000+ in March 2020.

The options strategy is strictly better than buy&hold SPY.

