# Options Backtesting <br/>
Chart below shows results from 2016-2021, however, repo only contains data snippet from 2021. <br/>
Viwers can test with (1) any days to expiration <= 7 (ln 24, mainprg.py) and <br/>
(2) different combinations of delta (ln 28-29, mainprg.py, delta>0 & delta<1) 

## Strategy description

We backtested with our tool the 7 DTE (Days To Expiration) put credit spread strategy on SPX. <br/>
Days to expiration: 7<br/>
Frequency: Weekly, 3 times/week since 2021 (SPX has contracts expired on Mon, Wed and Fri every week)<br/>
Strategy: Put credit spread<br/>

### Actions:<br/>
Every Mon, Wed, Fri (excl. holidays when markets are closed), sell put credit spread that expires a week from then.<br/>
Short leg: Sell one put contract at 10 delta and collect credit<br/>
Long leg: buy one put contract at 6 delta and pay debit<br/>

Total Premium Collected (max profit) = short leg credit collected - long leg debit paid<br/>
Stop loss criteria: Loss = 2x Total Premium Collected<br/>

## Result

![alt text](https://github.com/pareto-digital/OptionsBacktesting/blob/main/spx%20pcs%20vs%20spy%20example.png?raw=true)

Between Jan. 2016 to June 2021, total return of the strategy is $66,400 (not consider commision fees), and maximum drawdown was $1,300 in March 2020. The average buying power effect was only $1,0000+, resulting an ROI of 500%+.<br/>

We compare this strategy with holding 100 shares of SPY. The purchasing cost was $20,000 in Jan. 2016. During the same period, SPY rised from $200 to $400 (100% ROI) and max draw down of $10,000+ in March 2020.<br/>

The options strategy is strictly better than buy&hold 100 shares SPY.

