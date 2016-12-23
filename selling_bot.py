from poloniex import Poloniex
from decimal import Decimal
import time
import datetime
from config import *


polo = Poloniex(API_KEY, SECRET)


def main():
    # for each coin, create a specific coin seller
    global polo
    coin_sellers = [CoinSeller(config) for config in sell_coin_configs]

    while True:
        for coin_seller in coin_sellers:
            try:
                coin_seller.sell()                
            except:
                print('\033[91merror when selling {}. recreate polo.\033[0m'.format(coin_seller.coin))
                polo = Poloniex(API_KEY, SECRET)

        time.sleep(SLEEP_TIME)


class CoinSeller:
    def __init__(self, config):
        self.msg = ''
        self.prev_msg = ''
        
        # self.config = config
        self.coin = config['coin']
        self.coin_pair = config['coin_pair']
        self.amount_threshold = config['amount_threshold']
        self.min_price = config['min_price']

    def sell(self):
        # cancel order and check if there are coins to sell
        open_orders = polo.returnOpenOrders(self.coin_pair)
        for open_order in open_orders:
            polo.cancelOrder(open_order['orderNumber'])
        balance = polo.returnBalances()[self.coin]

        # find a proper price and sell
        if Decimal(balance) == 0:
            self.msg = 'no \033[92m{}\033[0m to sell'.format(self.coin)
        else:
            orders = polo.returnOrderBook(self.coin_pair, depth=50)
            asks = orders['asks']
            bids = orders['bids']

            sell_rate = Decimal(self.min_price)  # min sell rate
            
            sum_amount = Decimal(0)
            for rate, amount in asks:
                sum_amount += Decimal(amount)
                proper_sell_rate = Decimal(rate) - Decimal('0.00000001')
                sell_rate = max(sell_rate, proper_sell_rate)
                if sum_amount > self.amount_threshold:  # TODO: sum_amount may never be more than threshold.
                    high_bid_rate = Decimal(bids[0][0])
                    if sell_rate == high_bid_rate:
                        sell_rate = sell_rate + Decimal('0.00000001')
                    break

            self.msg = 'place sell order: \033[96m{} \033[92m{}\033[0m at \033[96m{}\033[0m'.format(balance, self.coin, sell_rate)
            polo.sell(self.coin_pair, str(sell_rate), balance)

        # print message
        if self.msg != self.prev_msg:
            print('\033[2m{}\033[0m   {}'.format(datetime.datetime.now(), self.msg))
        self.prev_msg = self.msg


# class bcolors:
#     HEADER = '\033[95m'
#     OKBLUE = '\033[94m'
#     OKGREEN = '\033[92m'
#     WARNING = '\033[93m'
#     FAIL = '\033[91m'
#     ENDC = '\033[0m'
#     BOLD = '\033[1m'
#     UNDERLINE = '\033[4m'


if __name__ == '__main__':
    main()
