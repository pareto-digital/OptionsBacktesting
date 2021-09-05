import requests
import pandas as pd
import psycopg2

TOKEN = 'xxxxxxxxxxxxxxxx'


def get_underlying_price(ticker=None, start_date=None, end_date=None, frequency='daily'):
    """
    Parameters
    ----------
    ticker
    start_date: yyyy-mm-dd
    end_date: yyyy-mm-dd
    Get underlying stock price from Tradier developer API
    Returns
    -------
    """

    response = requests.get('xxxxxxxxxxxxxxxxx',
                            params={'symbol': ticker, 'interval': frequency, 'start': start_date,
                                    'end': end_date},
                            headers={'Authorization': TOKEN, 'Accept': 'application/json'}
                            )

    if response.status_code == 200:
        market_history_response = response.json()
        market_history_df = pd.DataFrame(market_history_response['history']['day'])
        market_history_df = market_history_df.rename(columns={'date': 'Date'})
        market_history_df.set_index("Date", inplace=True)

        return market_history_df

    return "unable to acquire market history" + str(response.status_code)


def get_option_price(start_date, dte, tablename):
    conn = psycopg2.connect(
        host="xxxxxxxxxxx",
        database="xxxxxxxxxxxx",
        user="postgres",
        )
    cur = conn.cursor()

    cur.execute("WITH option_price AS (SELECT *, "
                "expirdate-trade_date AS days_to_expir, "
                "extract(dow from expirdate) AS expirday "
                "FROM {} "
                "WHERE trade_date >= '{}'::date "
                "AND expirdate-trade_date <= {} "
                "ORDER BY {}) "
                "SELECT * FROM option_price".format(tablename, start_date, dte, 'ticker, expirdate, trade_date, strike', dte)) #dte to yte

    option_hist_sql = cur.fetchall()
    cur.close()

    header_list = ['ticker', 'stkpx', 'expirdate', 'yte', 'strike', 'cvolu', 'coi', 'pvolu', 'poi', 'cbidpx', 'cvalue',
                   'caskpx', 'pbidpx', 'pvalue', 'paskpx', 'cbidiv', 'cmidiv', 'caskiv', 'smoothsmvvol', 'pbidiv',
                   'pmidiv', 'paskiv', 'irate', 'divrate', 'residualratedata', 'delta', 'gamma', 'theta', 'vega', 'rho',
                   'phi', 'driftlesstheta', 'extvol', 'extctheo', 'extptheo', 'spot_px', 'trade_date', 'days_to_expir', 'expirday']

    option_hist = pd.DataFrame(option_hist_sql, columns=header_list)
    option_hist.reset_index(drop=True, inplace=True)
    return option_hist
