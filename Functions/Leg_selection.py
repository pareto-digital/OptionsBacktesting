import pandas as pd


def select_put_leg(option_data_df, select_param='delta', select_val=.2, side='short'):
    """
    Assuming put (put delta = 1-nominal delta)

    Args:
        option_data:
        delta:
        side:

    Returns:

    """
    if select_param == 'delta':
        option_data_delta_selected = option_data_df[((1-option_data_df[select_param]) <= select_val)]  # 1-delta: due to put
    elif select_param == 'pvalue':
        option_data_delta_selected = option_data_df[(option_data_df[select_param] <= select_val)]
    else:
        option_data_delta_selected = option_data_df[(option_data_df[select_param] >= select_val)]

    option_data_delta_selected = option_data_delta_selected.rename(columns={'delta': side+'_delta',
                                                                                'pbidpx': side+'_pbidpx',
                                                                                'pvalue': side+'_pvalue',
                                                                                'paskpx': side+'_paskpx',
                                                                                'trade_date': side+'_trade_date'})

    option_data_delta_selected = option_data_delta_selected.sort_values(by=['ticker', 'expirdate', 'strike'])
    # if select_param == 'strike_distance':
    #     option_data_delta_selected = option_data_delta_selected.groupby(['ticker', 'expirdate']).first().reset_index(drop=False)  # put use last()
    # else:
    option_data_delta_selected = option_data_delta_selected.groupby(['ticker', 'expirdate']).last().reset_index(
        drop=False)  # put use last()

    return option_data_delta_selected


def select_call_leg(option_data_df, select_param='delta', select_val=.2, side='short'):
    """
    Assuming call (call delta = nominal delta)

    Args:
        option_data:
        delta:
        side:

    Returns:

    """

    option_data_delta_selected = option_data_df[(option_data_df[select_param] <= select_val)]

    option_data_delta_selected = option_data_delta_selected.rename(columns={'delta': side+'_delta',
                                                                                'cbidpx': side+'_cbidpx',
                                                                                'cvalue': side+'_cvalue',
                                                                                'caskpx': side+'_caskpx',
                                                                                'trade_date': side+'_trade_date'})

    # if select_param == 'strike_distance':
    #     option_data_delta_selected = option_data_delta_selected.groupby(['ticker', 'expirdate']).last().reset_index(drop=False)  # put use last()
    # else:
    option_data_delta_selected = option_data_delta_selected.groupby(['ticker', 'expirdate']).first().reset_index(drop=False)  # put use last()

    return option_data_delta_selected


def leg_pnl_cal(options_legs_df, option_all_data_df, option_type='put', side='short'):

    if option_type=='put':
        otype = '_p'
    else:
        otype = '_c'

    trade_data = options_legs_df[['ticker', 'expirdate', side+'_trade_date', 'strike', side+'_delta', side+otype+'bidpx',
                                  side+otype+'value', side+otype+'askpx']]

    #Rename to differentiate leg side
    trade_data = trade_data.rename(
        columns={side+'_delta': side+'_delta_transact', side+otype+'bidpx': side+otype+'bidpx_transact',
                 side+otype+'value': side+otype+'value_transact', side+otype+'askpx': side+otype+'askpx_transact',
                 side+'_trade_date': side+'_date_transact'})

    leg_pnl = pd.merge(trade_data, option_all_data_df, how='left', on=['ticker', 'expirdate', 'strike'])

    if side == 'short':
        leg_pnl['pnl_short'] = leg_pnl[side+otype+'value_transact'] - leg_pnl[otype[1]+'value'] #pvalue vs cvalue
    else:
        leg_pnl['pnl_long'] = leg_pnl[otype[1]+'value'] - leg_pnl[side+otype+'value_transact']

    leg_pnl = leg_pnl.sort_values(by=['expirdate', 'trade_date'])

    leg_pnl_trim = trim_leg(leg_pnl, otype, side)

    return leg_pnl_trim


def trim_leg(leg_pnl_df, otype, side='short'):
    """
    Trim data on each leg for merge

    Args:
        leg_pnl_df:
        side:

    Returns:

    """
    leg_pnl_trimmed = leg_pnl_df[['ticker', 'expirdate', side+'_date_transact', 'strike', side+'_delta_transact',
                                  side+otype+'value_transact', otype[1]+'value', 'delta', 'trade_date', 'days_to_expir',
                                  'pnl_'+side]]

    leg_pnl_trimmed = leg_pnl_trimmed.rename(
        columns={'strike': side+'_strike', otype[1]+'value': side+otype+'value', 'delta': side+'_delta'})

    return leg_pnl_trimmed


def pnl_cal(short_leg_pnl_df, long_leg_pnl_df, option_type='put', naked=False):
    """

    Returns:

    """
    if option_type=='put':
        otype = '_p'
    else:
        otype = '_c'

    PnL_calc = pd.merge(short_leg_pnl_df, long_leg_pnl_df,
                        left_on=['ticker', 'expirdate', 'short_date_transact', 'trade_date', 'days_to_expir'],
                        right_on=['ticker', 'expirdate', 'long_date_transact', 'trade_date', 'days_to_expir']
                        )

    if naked:
        PnL_calc['value'] = PnL_calc['short'+otype+'value']  # Naked put
    else:
        PnL_calc['value'] = PnL_calc['short'+otype+'value'] - PnL_calc['long'+otype+'value']

    initial_credit = PnL_calc.groupby(['ticker', 'expirdate']).first().reset_index(drop=False)
    initial_credit = initial_credit[['ticker', 'expirdate', 'value']]
    initial_credit = initial_credit.rename(columns={'value': 'init_credit'})

    PnL_final = pd.merge(initial_credit, PnL_calc, how='left', on=['ticker', 'expirdate'])
    PnL_final = PnL_final[PnL_final['init_credit'] > 0].reset_index(drop=True)
    PnL_final['pnl'] = PnL_final['init_credit'] - PnL_final['value']

    return PnL_final


def stop_loss(PnL_df, stop_crit, naked=False):
    """

    Args:
        PnL_df:
        stop_crit:
        naked:

    Returns:
        Pnl with stop loss
        Stop loss occurrences
    """

    PnL_df['stop_loss'] = PnL_df['pnl'] + stop_crit * PnL_df['init_credit'] <= 0
    PnL_df['max_loss'] = (1 - stop_crit) * PnL_df['init_credit']  # Set hard stop price to avoid using EOD price

    stop_loss = PnL_df[PnL_df['stop_loss'] == True].groupby(['ticker', 'expirdate']).first().reset_index(drop=False)
    stop_loss = stop_loss[['ticker', 'expirdate', 'trade_date']]
    stop_loss = stop_loss.rename(columns={'trade_date': 'stop_loss_date'})
    PnL_final_with_stop_loss = pd.merge(PnL_df, stop_loss, how='left', on=['ticker', 'expirdate'])
    PnL_final_with_stop_loss['stopped'] = PnL_final_with_stop_loss['stop_loss_date'] < PnL_final_with_stop_loss[
        'trade_date']
    PnL_final_with_stop_loss = PnL_final_with_stop_loss[PnL_final_with_stop_loss['stopped'] == False]

    #BPE inaccurate yet, need to add back credit collected
    if naked:
        PnL_final_with_stop_loss['BPE'] = 100 * (PnL_final_with_stop_loss['short_strike'])  # Naked put selling
    else:
        PnL_final_with_stop_loss['BPE'] = 100*abs(PnL_final_with_stop_loss['short_strike']-PnL_final_with_stop_loss['long_strike'])

    PnL_final_with_stop_loss = PnL_final_with_stop_loss.sort_values(by=['expirdate', 'trade_date']).reset_index(drop=True)

    return PnL_final_with_stop_loss, stop_loss


def odds_calc(pnl_df):
    odds = pnl_df.groupby(['ticker', 'expirdate']).last().reset_index(drop=False)
    odds['Year'] = pd.to_datetime(odds['trade_date']).dt.to_period('Y')
    odds['pnl_approx'] = odds[['pnl', 'max_loss']].max(axis=1)
    odds['Win'] = odds['pnl_approx'] > 0
    odds['cumulative_pnl'] = odds['pnl_approx'].cumsum()
    odds = odds.sort_values(by=['trade_date'])
    win_rate = odds.groupby(['Year'])['Win'].sum() / odds.groupby(['Year'])['Win'].count()
    year_end_pnl_max_drawdown = odds.groupby(['Year'])['pnl_approx'].agg(['sum', 'min'])
    return odds, win_rate, year_end_pnl_max_drawdown
