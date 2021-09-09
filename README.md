# Options Backtesting (example)

## Strategy description

We used our tool to backtest 7dte put creadit spread strategy on SPX. <br/>
Days to expiration: 7<br/>
Frequency: Weekly, 3 times/week since 2021 (SPX has contracts expired on Mon, Wed and Fri every week)
Strategy: Put credit spread<br/>

### Actions:<br/>
Short leg: Sell one put contract at 10 delta and collect credit<br/>
Long leg: but one put contract at 6 delta and pay debit<br/>

Total Premium Collected (max profit) = short leg credit collected - long leg debit paid<br/>
Stop loss criteria: Loss = 2x Total Premium Collected<br/>

## Result

![alt text](https://github.com/pareto-digital/OptionsBacktesting/blob/main/spx%20pcs%20vs%20spy%20example.png?raw=true)

Between Jan. 2016 to June 2021, total return of the strategy is $66,400 (not consider commision fees), and maximum drawdown was $1,300 in March 2020. The average buying power effect was only $1,0000+, resulting an ROI of 500%+.<br/>

We compare this strategy with holding 100 shares of SPY. The purchasing cost was $20,000 in Jan. 2016. During the same period, SPY rised from $200 to $400 (100% ROI) and max draw down of $10,000+ in March 2020.<br/>

The options strategy is strictly better than buy&hold 100 shares SPY.

