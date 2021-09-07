import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import Functions.Query as Query
from Functions.Leg_selection import select_put_leg, leg_pnl_cal, pnl_cal, stop_loss, odds_calc
import pandas_market_calendars as mcal
import numpy as np

ticker = 'SPY'
start_date = '2016-01-01'
end_date = '2021-05-28'
frequency = 'daily'
number_of_trades = 1


stock_price = Query.get_underlying_price(ticker, start_date, end_date).reset_index(drop=False)
stock_price['close'] = stock_price['close']
option_price = Query.get_option_price(start_date, 7, 'options_history_spx')
option_price['strike_distance'] = option_price['stkpx'] - option_price['strike']

#options_7dte = option_price[((option_price['days_to_expir'] == 2)&(option_price['expirday'].isin([3,5])))|((option_price['days_to_expir'] == 3)&(option_price['expirday'] == 1))].reset_index(drop=True)
options_7dte = option_price[option_price['days_to_expir'] == 7].reset_index(drop=True)

options_7dte = options_7dte[options_7dte['expirday'].isin([1, 3, 5])].reset_index(drop=True)

# delta vs. credit
put_options_short_legs = select_put_leg(options_7dte, select_param='delta', select_val=.1, side='short')
put_options_long_legs = select_put_leg(options_7dte, select_param='delta', select_val=.06,  side='long')

# leg pnl calc
short_put_leg_pnl_trimmed = leg_pnl_cal(put_options_short_legs, option_price, option_type='put', side='short')
long_put_leg_pnl_trimmed = leg_pnl_cal(put_options_long_legs, option_price, option_type='put', side='long')

isNaked = False
PnL_final_put = pnl_cal(short_put_leg_pnl_trimmed, long_put_leg_pnl_trimmed, option_type='put', naked=isNaked)
# Stop loss and max loss criteria
PnL_final_put_with_stop_loss, stop_loss_occurrences_put = stop_loss(PnL_final_put, stop_crit=3, naked=isNaked)

odds_put, win_rate_put, year_end_pnl_max_drawdown_put = odds_calc(PnL_final_put_with_stop_loss)

# Buying Power Effect
PnL_final_put_with_stop_loss = PnL_final_put_with_stop_loss[(PnL_final_put_with_stop_loss['days_to_expir'] != 7)].sort_values(by=['trade_date', 'short_date_transact'])
bpe_analysis_put = PnL_final_put_with_stop_loss.groupby(['ticker', 'trade_date'])['BPE'].agg(['sum', 'count']).reset_index(drop=False)

print('Plot starts here')
stock_price['pnl'] = (stock_price.close - stock_price.close.values[0])*100

# # fig, ax = plt.subplots(figsize=(15,8))
odds_put['losing trade'] = (1-odds_put['Win'])*odds_put['cumulative_pnl']
losing_trade_put = odds_put[odds_put['Win']== False].reset_index(drop=True)

bpe_losing_put = pd.merge(losing_trade_put[['ticker', 'trade_date', 'Win']], bpe_analysis_put, on=['ticker', 'trade_date'], how='left')


nyse = mcal.get_calendar('NYSE')
holidays = pd.DataFrame(nyse.holidays().holidays, columns=['holidays'])
holidays['holidays'] = pd.to_datetime(holidays['holidays']).dt.date
holidays2016andon = holidays[(holidays['holidays'] >= pd.to_datetime(start_date))&(holidays['holidays'] <= pd.to_datetime(end_date))].reset_index(drop=True)
#
plt.figure()
ax1 = plt.subplot(211)
ax1.xaxis.set_major_locator(matplotlib.dates.YearLocator())
ax1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y'))
ax1.yaxis.set_major_formatter('${x:1.0f}')
ax1.tick_params(axis='x', labelsize=15)
ax1.tick_params(axis='y', labelsize=15)
ax1.plot(pd.to_datetime(stock_price['Date']), stock_price['pnl'], 'b')
ax1.plot(pd.to_datetime(odds_put['trade_date']), number_of_trades*odds_put['cumulative_pnl'] * 100, 'g')
ax1.plot(pd.to_datetime(losing_trade_put['trade_date']), number_of_trades*losing_trade_put['cumulative_pnl'] * 100, '.r', markersize=10)

ax1.spines['right'].set_visible(False)
ax1.spines['top'].set_visible(False)

ticker='SPX'
plt.title(ticker+' Put Credit Spread PnL 2x stop-loss, number of option trades = ' + str(len(odds_put)) + ', win rate = ' + "{0:.2f}%".format((1-len(stop_loss_occurrences_put)/len(odds_put))*100), fontsize=20)
ax1.legend(['SPY x100', 'Option', 'Losing Trades'], loc='upper left', fontsize=15)


ax2 = plt.subplot(212)
ax2.yaxis.set_major_formatter('${x:1.0f}')
ax2.tick_params(axis='x', labelsize=15)
ax2.tick_params(axis='y', labelsize=15)
ax2.plot(pd.to_datetime(bpe_analysis_put['trade_date']), number_of_trades * bpe_analysis_put['sum'], 'g')
ax2.plot(pd.to_datetime(bpe_losing_put['trade_date']), number_of_trades*bpe_losing_put['sum'], '.r', markersize=10)


for days in holidays2016andon['holidays']:
    ax2.axvline(x=days, linestyle=":")

ax2.spines['right'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax2.legend(['Buying Power Effect', 'Losing Trades Put', 'Holidays'], loc='upper left', fontsize=15)

