'''
file created by Kaifeng Chen, 09/26/2017
to trading purpose
'''
import argparse
from util import robinhood_api
from crawler import robinhood_crawler

crawler_session = robinhood_api.robinhood_session(require_log_in = False, write_to_log = False)
crawler = robinhood_crawler.robinhood_crawler(session = crawler_session, stock_names = 'GOOG, GOOGL')
crawler._check_time()

trade_session = robinhood_api.robinhood_session(require_log_in = True, write_to_log = True)

trade_session.logout()
crawler_session.logout()