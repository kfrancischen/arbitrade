'''
file created by Kaifeng Chen, 09/29/2017
to download trading data from Robinhood
'''

from util import robinhood_api
import sys, logging
import os.path, time
from datetime import datetime
from pytz import timezone
import csv

class robinhood_crawler:
    cur_path = os.path.dirname(__file__)
    logger = logging.getLogger('Robinhood_Crawler')
    hdlr = logging.FileHandler(cur_path + '/../Robinhood_Crawler.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

    def __init__(self, session, stock_names):
        if session.status() == False:
            self.logger.info('session not logged in...')
            print 'session not logged in...'
            sys.exit()

        self.session = session
        self.stock_names = stock_names.replace(' ', '')

    def _check_time(self):
        """check whether it is trading today"""
        '''
        from official website:
        Traditionally, the markets are open from 9:30AM EST - 4:00PM EST during normal business days.
        With extended hours trading, you'll be able to trade:

        Pre-Market opens 30 minutes earlier starting at 9:00AM EST
        After-Hours continues for 120 minutes (2 hours) until 6:00PM EST
        '''
        today = datetime.now(timezone('US/Eastern'))
        today_date = today.date().weekday()

        trading_start_time = today.replace(hour = 9, minute = 0, second = 0, microsecond = 0)
        trading_end_time = today.replace(hour = 18, minute = 0, second = 0, microsecond = 0)

        # does not trade on Saturday and Sunday between the above hours
        if today_date >= 5 or today < trading_start_time or today > trading_end_time:
            return False

        return True


    def crawl(self, interval = 5):
        """
        crawling data for every interval seconds
        """
        print 'start crawling'
        self.logger.info('start crawling for ' + self.stock_names + '...')
        while True:
            time.sleep(interval)
            if self._check_time() == False:
                self.logger.info('check time: False...')
                continue
            self.logger.info('check time: correct. Writing to disk...')
            self._crawl_every()


    def _crawl_every(self):
        """
        crawling data for every interval
        """
        today_date = datetime.now(timezone('US/Eastern')).date()

        data_path = self.cur_path + '/../trading_data/' + str(today_date)
        if os.path.exists(data_path) == False:
            os.mkdir(data_path)
        stocks = self.stock_names.split(',')
        quotes = self.session.quotes(stock_names = self.stock_names)
        headers = quotes[0].keys()
        for i in range(len(stocks)):
            stock_name = stocks[i]
            quote = quotes[i]
            file_path = data_path + '/' + stock_name + '.csv'
            if os.path.exists(file_path) == False:
                with open(file_path, 'w') as outcsv:
                    writer = csv.DictWriter(outcsv, fieldnames = headers)
                    writer.writeheader()

            with open(file_path, 'a') as outcsv:
                writer = csv.writer(outcsv)
                row = []
                for key in headers:
                    row.append(quote[key])
                writer.writerow(row)
            self.logger.info('writing ' + stock_name + ' finished...')

