from robinhood_api import *

session = robinhood_session()
session.update(stock_names = 'GOOGL, GOOG')

print "get investment_profile...\n"
print session.investment_profile(), "\n"

print "get instruments...\n"
print session.instruments(stock_name = 'GOOGL'), '\n'

print "get quotes...\n"
print session.quotes(stock_names = 'GOOGL, GOOG'), '\n'\

print "get news...\n"
print session.news(stock_name = 'GOOGL'), '\n'

print "get last trade price...\n"
print session.last_trade_price(stock_names = 'GOOGL, GOOG'), '\n'

print "get ask price...\n"
print session.ask_price(stock_names = 'GOOGL, GOOG'), '\n'

print "get ask size...\n"
print session.ask_size(stock_names = 'GOOGL, GOOG'), '\n'

print "get bid price...\n"
print session.bid_price(stock_names = 'GOOGL, GOOG'), '\n'

print "get bid size...\n"
print session.bid_size(stock_names = 'GOOGL, GOOG'), '\n'

print "get previous close price...\n"
print session.previous_close_price(stock_names = 'GOOGL, GOOG'), '\n'

print "get adjusted previous close price...\n"
print session.adjusted_previous_close_price(stock_names = 'GOOGL, GOOG'), '\n'

print "get update time...\n"
print session.updated_time(stock_names = 'GOOGL, GOOG'), '\n'

print "get last extended hours trade price...\n"
print session.last_extended_hours_trade_price(stock_names = 'GOOGL, GOOG'), '\n'


print "get historicals...\n"
print session.historicals(stock_names='GOOGL, GOOG', interval='5minute', span='day'), '\n'


print "get fundamentals...\n"
print session.fundamentals(stock_names = 'GOOGL, GOOG'), '\n'

print "adjusted_equity_previous_close...\n"
print session.adjusted_equity_previous_close(), '\n'

print "adjusted_equity_previous_close...\n"
print session.adjusted_equity_previous_close(), '\n'

print "withdrawable_amount...\n"
print session.withdrawable_amount(), '\n'

print "equity...\n"
print session.equity(), '\n'


print "last_core_equity...\n"
print session.last_core_equity(), '\n'

print "excess_margin...\n"
print session.excess_margin(), '\n'

print "extended_hours_equity...\n"
print session.extended_hours_equity(), '\n'

print "market value...\n"
print session.market_value(), '\n'

print "extended_hours_market_value..\n"
print session.extended_hours_market_value(), '\n'

print "last core market value...\n"
print session.last_core_market_value(), '\n'

print "order history...\n"
print session.order_history(), '\n'

print "dividends...\n"
print session.dividends(), '\n'

print "positions...\n"
print session.positions(), '\n'

print "securities owned...\n"
print session.securities_owned(), '\n'

print "invested stocks...\n"
print session.invested_stocks(), '\n'

fit_instrument = session.instruments(stock_name = 'FIT')[0]

print session.place_sell_order(instrument = fit_instrument, quantity = 1)

session.logout()