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
        self.session = session
        self.stock_names = stock_names.replace(' ', '')
        self.today_date = self.yesterday_date = str(datetime.now(timezone('US/Eastern')).date())
        self.logger.info('Crawling for date ' + self.today_date)
        self.is_crawling = False
        self.visited_hours = {}

    def status():
        return self.is_crawling

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
        if str(today.date()) != self.today_date:
            self.today_date = str(today.date())
            self.logger.info('Crawling real time data for date ' + self.today_date)
            self.visited_hours = {}

        today_date = today.date().weekday()
        trading_start_time = today.replace(hour = 9, minute = 0, second = 0, microsecond = 0)
        trading_end_time = today.replace(hour = 18, minute = 0, second = 0, microsecond = 0)

        # does not trade on Saturday and Sunday between the above hours
        if today_date >= 5 or today < trading_start_time or today > trading_end_time:
            self.is_crawling = False
            return False, today.hour
        self.is_crawling = True

        return True, today.hour


    def crawl(self, interval = 5):
        """
        crawling data for every interval seconds
        """
        print 'start crawling'
        self.logger.info('start crawling for ' + self.stock_names + '...')
        while True:
            time.sleep(interval)
            # craw for real time data
            to_craw, cur_hour = self._check_time()
            if to_craw == False:
                continue
            # craw for historical
            if self.today_date != self.yesterday_date:
                self._craw_historical()
                self.logger.info('Crawling historical data for date ' + self.yesterday_date)
                self.yesterday_date = self.today_date

            self._crawl_real_time()

            # craw for news for every two hours
            if (cur_hour - 9) % 2 == 0 and cur_hour not in self.visited_hours:
                self.visited_hours[cur_hour] = True
                self.logger.info('Crawling news for hour ' + str(cur_hour))
                self._crawl_news()

    def _craw_historical(self, interval = '5minute', span = 'day', bounds = 'extended'):
        historicals = self.session.historicals(
                stock_names = self.stock_names,
                interval = interval,
                span = span,
                bounds = bounds)
        stocks = self.stock_names.split(',')
        headers = historicals[stocks[0]].keys()

        data_path = self.cur_path + '/../trading_data/' + str(self.yesterday_date)
        for i in range(len(stocks)):
            stock_name = stocks[i]
            historical = historicals[stock_name]
            file_path = data_path + '/' + stock_name + '_' + interval + '_' + span + '_' + bounds + '.csv'
            if os.path.exists(file_path) == False:
                with open(file_path, 'w') as outcsv:
                    writer = csv.DictWriter(outcsv, fieldnames = headers)
                    writer.writeheader()

            with open(file_path, 'a') as outcsv:
                writer = csv.writer(outcsv)
                row = []
                data_len = len(historical[headers[0]])
                for i in range(data_len):
                    row = []
                    for key in headers:
                        row.append(historical[key][i])
                    writer.writerow(row)

    def _crawl_news(self):
        today_date = datetime.now(timezone('US/Eastern')).date()

        data_path = self.cur_path + '/../trading_data/' + str(today_date)
        if os.path.exists(data_path) == False:
            os.mkdir(data_path)

        stocks = self.stock_names.split(',')
        news_list = []
        for i in range(len(stocks)):
            news_list.append(self.session.news(stock_name = stocks[i]))

        headers = news_list[0][0].keys()
        for i in range(len(stocks)):
            stock_name = stocks[i]
            news = news_list[i]

            file_path = data_path + '/' + stock_name + '_news.csv'
            if os.path.exists(file_path) == False:
                with open(file_path, 'w') as outcsv:
                    writer = csv.DictWriter(outcsv, fieldnames = headers)
                    writer.writeheader()

            with open(file_path, 'a') as outcsv:
                writer = csv.writer(outcsv)
                for item in news:
                    row = []
                    for key in headers:
                        val = item[key]
                        if key == 'summary' or key == 'title':
                            val = val.encode('ascii', 'ignore')
                        row.append(val)
                    writer.writerow(row)

        return


    def _crawl_real_time(self):
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

