from poloniex import Poloniex
from decimal import *
import time
import datetime
from config import API_KEY, SECRET, COIN_TO_SELL, COIN_PAIR, THRESHOLD, SLEEP_TIME



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
        orders = polo.returnOrderBook(COIN_PAIR)
        asks = orders['asks']
        bids = orders['bids']

        sum_amount = Decimal(0)
        for rate, amount in asks:
            sum_amount += Decimal(amount)
            if sum_amount > THRESHOLD:  # sell at this rate
                sell_rate = Decimal(rate) - Decimal('0.00000001')
                high_bid_rate = Decimal(bids[0][0])
                if sell_rate == high_bid_rate:
                    sell_rate = sell_rate + Decimal('0.00000001')
                break
        sell_rate = str(sell_rate)

        msg = 'sell {} {} at {}'.format(balance, COIN_TO_SELL, sell_rate)
        polo.sell(COIN_PAIR, sell_rate, balance)

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
