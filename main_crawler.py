'''
file created by Kaifeng Chen, 10/02/2017
to crawl Robinhood data
'''
from util import robinhood_api
from crawler import robinhood_crawler
'''
one can change the stock_names to add more stocks of interest
'''
def main(stock_names = 'GOOG, GOOGL, FB, NVDA, BABA, NFLX, AAPL, AMAT, ADBE, AMZN, TSLA' + \
        ', DIS, GPRO, SBUX, F, BAC, FIT, GE, SNAP, SPY, EBAY, ORCL, JD, TWTR, TSM, MKC, ABBV, MS' + \
        ', AMD, BIDU, BBY, C, CVX, CMCSA, CSCO, ETFC, FOXA, GS, HPQ, IBM, JPM, SPGI, T, WB, XOM, YELP' + \
        ', Z, TSN, MU, PYPL'):

    crawler_session = robinhood_api.robinhood_session(require_log_in = False, write_to_log = False)
    crawler = robinhood_crawler.robinhood_crawler(session = crawler_session, stock_names = stock_names)
    crawler.crawl(interval = 30)
    crawler_session.logout()


main()