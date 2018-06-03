from binance.client import Client
import os
import datetime

api_key = os.environ.get('binance_api_key')
api_secret = os.environ.get('binance_api_secret')
client = Client(api_key, api_secret)

portfolio = {
    'NEO': {
        'percentage': 50,
        'symbol': 'NEOBNB',
        'btc_value': 0.0,
        'balance': 0.0,
        'uncorrected_btc_value': 0.0,
        'uncorrected_amount': 0.0
    },
    'BNB': {
        'percentage': 50,
        'symbol': 'NEOBNB',
        'btc_value': 0.0,
        'balance': 0.0,
        'uncorrected_btc_value': 0.0,
        'uncorrected_amount': 0.0
    }
}

def calculate_uncorrected_value(total_value, current_value, percentage):
    return -(((total_value / 100) * percentage) - current_value)

portfolio_value = 0
minimum = float(client.get_symbol_ticker(symbol='NEOBTC')['price']) / 100

# retrieve asset balance, value and portfolio value
for key in portfolio:
    portfolio[key]['balance'] = float(client.get_asset_balance(asset=key)['free'])

prices = client.get_all_tickers()
for price in prices:
    for key in portfolio.keys():
        if price['symbol'] == key + 'BTC':
            portfolio[key]['btc_value'] = float(price['price']) * portfolio[key]['balance']
            portfolio_value += portfolio[key]['btc_value']

# calculate uncorrected btc value
for key in portfolio.keys():
    total_value = portfolio_value
    current_value = portfolio[key]['btc_value']
    percentage = portfolio[key]['percentage']

    ticker = key + 'BTC'
    uncorrected_btc_value = calculate_uncorrected_value(total_value, current_value, percentage)
    btc_rate = float(client.get_symbol_ticker(symbol=ticker)['price'])
    uncorrected_amount = uncorrected_btc_value / btc_rate

    portfolio[key]['uncorrected_btc_value'] = uncorrected_btc_value
    portfolio[key]['uncorrected_amount'] = round(uncorrected_amount, 2)

# rebalance if there is an asset uncorrected enough to buy and an asset uncorrected enough to sell
for key in portfolio:
    if (portfolio[key]['uncorrected_btc_value'] > minimum):
        sellable = key

        for key in portfolio:
            if (portfolio[key]['uncorrected_btc_value'] < -minimum):
                buyable = key
                side = Client.SIDE_BUY if sellable == 'BNB' else Client.SIDE_SELL
                order = client.create_order(
                    symbol=portfolio[key]['symbol'],
                    side=side,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity=portfolio[sellable]['uncorrected_amount'])

                # save output to debug.log
                f = open('./history.log','a')

                output = str(datetime.datetime.now()) + ": SOLD " + str(portfolio[sellable]['uncorrected_amount']) + sellable + " FOR " + buyable

                f.write(output + '\n')

# temporary code
# print(datetime.datetime.now())
# print(minimum)
# for key in portfolio:
#     print(key + ': ' + str(portfolio[key]['uncorrected_btc_value']))
