from robinhood_api import *

session = robinhood_session()
print "get investment_profile...\n"
print session.investment_profile(), "\n"

print "get instruments...\n"
print session.instruments('GOOGL'), '\n'

print "get quotes...\n"
print session.quotes('GOOGL, GOOG'), '\n'\

print "get news...\n"
#print session.news(stock_name = 'GOOGL'), '\n'

print "get last trade price...\n"
print session.last_trade_price(stock_names = 'GOOGL'), '\n'

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

session.logout()