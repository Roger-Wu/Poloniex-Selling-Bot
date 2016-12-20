from poloniex import Poloniex
from decimal import Decimal
import time
import datetime
from config import *


def sell(polo):
    msg = ""

    # cancel order and check if there are coins to sell
    open_orders = polo.returnOpenOrders(COIN_PAIR)
    for open_order in open_orders:
        polo.cancelOrder(open_order['orderNumber'])
    balance = polo.returnBalances()[COIN_TO_SELL]

    if Decimal(balance) == 0:
        msg = 'balance of {}: {}'.format(COIN_TO_SELL, balance)
    else:
        # sell all the coins
        orders = polo.returnOrderBook(COIN_PAIR, depth=50)
        asks = orders['asks']
        bids = orders['bids']

        sell_rate = Decimal(MIN_PRICE)  # min sell rate
        
        sum_amount = Decimal(0)
        for rate, amount in asks:
            sum_amount += Decimal(amount)
            proper_sell_rate = Decimal(rate) - Decimal('0.00000001')
            sell_rate = max(sell_rate, proper_sell_rate)
            if sum_amount > THRESHOLD:  # sum_amount may never be more than THRESHOLD
                high_bid_rate = Decimal(bids[0][0])
                if sell_rate == high_bid_rate:
                    sell_rate = sell_rate + Decimal('0.00000001')
                break

        msg = 'sell {} {} at {}'.format(balance, COIN_TO_SELL, sell_rate)
        polo.sell(COIN_PAIR, str(sell_rate), balance)

    return msg

polo = Poloniex(API_KEY, SECRET)

prev_msg = ""

while True:
    # print('=========================')
    try:
        msg = sell(polo)

        if msg != prev_msg:
            print('{}   {}'.format(datetime.datetime.now(), msg))
        prev_msg = msg
    except:
        print('error. recreate polo.')
        polo = Poloniex(API_KEY, SECRET)

    time.sleep(SLEEP_TIME)
