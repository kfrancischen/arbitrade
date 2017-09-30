'''
file created by Kaifeng Chen, 09/27/2017
to access Robinhood API
links here:
https://api.robinhood.com/
some codes are adopted from https://github.com/Jamonek/Robinhood/blob/master/Robinhood/Robinhood.py
'''
from enum import Enum
import requests
import six, logging, getpass
from six.moves.urllib.parse import unquote
from six.moves.urllib.request import getproxies
from six.moves import input
import RH_exceptions
import os.path
from collections import defaultdict
from datetime import datetime
import subprocess, json

class Bounds(Enum):
    """enum for bounds in `historicals` endpoint"""
    REGULAR = 'regular'
    EXTENDED = 'extended'
    TRADING = 'trading'


class Transaction(Enum):
    """enum for buy/sell orders"""
    BUY = 'buy'
    SELL = 'sell'

class Trigger(Enum):
    """enum for trigger"""
    IMMEDIATE = 'immediate'
    STOP = 'stop'

class Order(Enum):
    """enum for order type"""
    MARKET = 'market'
    LIMIT = 'limit'

class Time_In_Force(Enum):
    """enum for time_in_force"""
    GFD = 'gfd'
    GTC = 'gtc'
    IOC = 'ioc'
    FOK = 'fok'
    OPG = 'opg'

class robinhood_session:
    """wrapper class for fetching/parsing Robinhood endpoints"""
    endpoints = {
        "login": "https://api.robinhood.com/api-token-auth/",
        "logout": "https://api.robinhood.com/api-token-logout/",
        "investment_profile": "https://api.robinhood.com/user/investment_profile/",
        "accounts": "https://api.robinhood.com/accounts/",
        "ach_iav_auth": "https://api.robinhood.com/ach/iav/auth/",
        "ach_relationships": "https://api.robinhood.com/ach/relationships/",
        "ach_transfers": "https://api.robinhood.com/ach/transfers/",
        "applications": "https://api.robinhood.com/applications/",
        "dividends": "https://api.robinhood.com/dividends/",
        "edocuments": "https://api.robinhood.com/documents/",
        "instruments": "https://api.robinhood.com/instruments/",
        "margin_upgrades": "https://api.robinhood.com/margin/upgrades/",
        "markets": "https://api.robinhood.com/markets/",
        "notifications": "https://api.robinhood.com/notifications/",
        "orders": "https://api.robinhood.com/orders/",
        "password_reset": "https://api.robinhood.com/password_reset/request/",
        "portfolios": "https://api.robinhood.com/portfolios/",
        "positions": "https://api.robinhood.com/positions/",
        "quotes": "https://api.robinhood.com/quotes/",
        "historicals": "https://api.robinhood.com/quotes/historicals/",
        "document_requests": "https://api.robinhood.com/upload/document_requests/",
        "user": "https://api.robinhood.com/user/",
        "watchlists": "https://api.robinhood.com/watchlists/",
        "news": "https://api.robinhood.com/midlands/news/",
        "fundamentals": "https://api.robinhood.com/fundamentals/",
    }

    logger = logging.getLogger('Robinhood')
    hdlr = logging.FileHandler('../Robinhood.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

    def __init__(self):
        self.session = requests.session()
        self.session.proxies = getproxies()
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "X-Robinhood-API-Version": "1.171.0",
            "Connection": "keep-alive",
            "User-Agent": "Robinhood/823 (iPhone; iOS 7.1.2; Scale/2.00)"
        }
        self.session.headers = self.headers
        status = self.login_prompt()
        if status:
            print 'successfully logged in...'
        with open('../cache/instruments.json', 'r') as fp:
            self.instruments_symbol = json.load(fp)

    ############################################################
    # GET DATA ABOUT LOG IN AND OUT
    ############################################################
    def login_prompt(self):
        """Prompts user for username and password and calls login()."""
        username, password = '', ''
        home_dir = os.path.expanduser('~')
        if os.path.exists(home_dir + '/.robinhood_account'):
            print "Using stored account..."
            with open(home_dir + '/.robinhood_account', 'r') as f:
                for line in f:
                    line = line.split()
                    username, password = line[0], line[1]
        else:
            username = input("Username: ")
            password = getpass.getpass()

        return self._login(username = username, password = password)


    def _login(self, username, password, mfa_code = None):
        """
        save and test login info for Robinhood accounts
        Args:
            username (str): username
            password (str): password
        Returns:
            (bool): received valid auth token
        """
        self.username = username
        self.password = password
        payload = {
            'password': self.password,
            'username': self.username
        }
        if mfa_code:
            payload['mfa_code'] = mfa_code

        try:
            http_result = self.session.post(
                self.endpoints['login'],
                data = payload
            )
            http_result.raise_for_status()
            data = http_result.json()
        except requests.exceptions.HTTPError:
            raise RH_exceptions.LoginFailed

        if 'mfa_required' in data.keys():           #pragma: no cover
            raise RH_exceptions.TwoFactorRequired  #requires a second call to enable 2FA

        if 'token' in data.keys():
            self.auth_token = data['token']
            self.headers['Authorization'] = 'Token ' + self.auth_token
            if os.path.exists(os.path.expanduser('~') + '/.robinhood_account') == False:
                with open(os.path.expanduser('~') + '/.robinhood_account', 'w') as f:
                    f.write( username + '\t' + password)
            self.logger.info('successfully loggined in at ' + str(datetime.now()) + '...')
            return True
        return False

    def logout(self):
        """function to login"""
        try:
            http_result = self.session.post(self.endpoints['logout'])
            http_result.raise_for_status()
        except requests.exceptions.HTTPError as err_msg:
            warnings.warn('Failed to log out ' + repr(err_msg))

        self.headers['Authorization'] = None
        self.auth_token = None
        print "successfully logged out..."
        self.logger.info('successfully loggined out at ' + str(datetime.now()) + '...')
        return http_result

    def account(self):
        """fetch account information
        Returns:
            (:obj:`dict`): `accounts` endpoint payload
        """
        http_result = self.session.get(self.endpoints['accounts'])
        http_result.raise_for_status()  #auth required
        http_result = http_result.json()
        self.logger.info('successfully getting account information...')
        return http_result['results'][0]
    ############################################################
    # UPDATE DATA
    ############################################################
    def update(self, stock_names = ''):
        self._quote_data(stock_names)
        self._portfolios()
        print "Updated at time: " + str(datetime.now()) + '\n'
        self.logger.info("updated at time: " + str(datetime.now()))

    ############################################################
    # GET DATA ABOUT STOCKS FROM QUOTES
    ############################################################
    def investment_profile(self):
        """fetch investment_profile"""
        http_result = self.session.get(self.endpoints['investment_profile'])
        http_result.raise_for_status()
        data = http_result.json()
        self.logger.info('successfully getting investment profile...')
        return data

    def instruments(self, stock_name):
        """fetch instruments endpoint
        Args:
            stock (str): stock ticker
        Returns:
            (:obj:`dict`): JSON contents from `instruments` endpoint
        """
        http_result = self.session.get(
            self.endpoints['instruments'],
            params={'query': stock_name.upper()}
        )
        http_result.raise_for_status()
        http_result = http_result.json()

        # if requesting all, return entire object so may paginate with ['next']
        if stock_name == "":
            return http_result
        self.logger.info('successfully getting instruments for stocks ' + stock_name + '...')
        return http_result['results']


    def _instrument_symbol(self):
        """function outputs the instruments url to symbols hash
        only called once
        """
        http_result = self.session.get(
            self.endpoints['instruments']
        )
        http_result.raise_for_status()
        http_result = http_result.json()
        instrument_symbol = {}
        for item in http_result['results']:
            instrument_symbol[item['url']] = item['symbol']

        while http_result['next'] != None:
            http_result = self.session.get(http_result['next'])
            http_result.raise_for_status()
            http_result = http_result.json()
            for item in http_result['results']:
                instrument_symbol[item['url']] = item['symbol']

        with open('instruments.json', 'w') as fp:
            json.dump(instrument_symbol, fp)

        print len(instrument_symbol), ' successful'

    def quotes(self, stock_names):
        """Fetch quote for multiple stocks, in one single Robinhood API call
        Args:
            stock_names (str): stock tickers
        Returns:
            (:obj:`list` of :obj:`dict`): List of JSON contents from `quotes` endpoint, in the
            same order of input args. If any ticker is invalid, a None will occur at that position.
        """
        stock_names = stock_names.replace(' ', '')
        url = str(self.endpoints['quotes']) + "?symbols=" + stock_names.upper()
        try:
            http_result = requests.get(url)
            http_result.raise_for_status()
            data = http_result.json()
        except requests.exceptions.HTTPError:
            raise NameError('Invalid Symbols: ' + str(stock_names))
        self.logger.info('successfully getting quotes for stocks ' + stock_names + '...')
        return data["results"]

    def _quote_data(self, stock_names = '', is_save = True):
        """fetch stock_names quote
        Args:
            stock_names (str): stock ticker, separated by ','
        Returns:
            (:obj:`dict`): JSON contents from `quotes` endpoint
        """
        url = None
        if stock_names.find(',') == -1:
            url = str(self.endpoints['quotes']) + str(stock_names) + "/"
        else:
            url = str(self.endpoints['quotes']) + "?symbols=" + str(stock_names)
        try:
            http_result = requests.get(url)
            http_result.raise_for_status()
            data = http_result.json()
        except requests.exceptions.HTTPError:
            raise NameError('Invalid Symbol: ' + stock)
        if is_save:
            self.quote_data = data
        return data

    def news(self, stock_name):
        """fetch news endpoint
        Args:
            stock_name (str): stock ticker
        Returns:
            (:obj:`dict`) values returned from `news` endpoint
        """
        http_result = self.session.get(self.endpoints['news'] + stock_name.upper() + "/").json()
        self.logger.info('successfully getting news for stock ' + stock_name + '...')

        return http_result['results']


    def _get_quote_list(self, stock_names = '', key = ''):
        """Returns multiple stock info and keys from quote_data (prompt if blank)
        Args:
            stock_names (str): stock ticker (or tickers separated by a comma)
            , prompt if blank
            key (str): key attributes that the function should return
        Returns:
            (:obj:`list`): Returns values from each stock or empty list
                           if none of the stocks were valid
        """
        stock_names, key = stock_names.replace(' ', ''), key.replace(' ', '')

        def append_stock(result):
            keys = key.split(',')
            myStr = ''
            for key_val in keys:
                myStr += str(result[key_val]) + ","
            return (myStr.split(','))

        data = self.quote_data
        http_result = []

        if stock_names.find(',') != -1:
            for stock in data['results']:
                if stock == None:
                    continue
                http_result.append(append_stock(stock))
        else:
            http_result.append(append_stock(data))
        return http_result

    def last_trade_price(self, stock_names = ''):
        """print quote information
        Args:
            stock (str): ticker to fetch, separated by ','
        Returns:
            None
        """
        data = self._get_quote_list(stock_names, 'symbol, last_trade_price')
        result = {}
        for item in data:
            if item[1] != 'None':
                result[item[0]] = float(item[1])

        self.logger.info('successfully getting last_trade_price for stock ' + stock_names + '...')
        return result

    def ask_price(self, stock_names = ''):
        """get asking price for a stock
        Note:
            queries `quote` endpoint, dict wrapper
        Args:
            stock (str): stock ticker
        Returns:
            (float): ask price
        """
        data = self._get_quote_list(stock_names,'symbol, ask_price')
        result = {}
        for item in data:
            if item[1] != 'None':
                result[item[0]] = float(item[1])

        self.logger.info('successfully getting ask_price for stock ' + stock_names + '...')
        return result

    def ask_size(self, stock_names = ''):
        """get ask size for a stock
        Note:
            queries `quote` endpoint, dict wrapper
        Args:
            stock (str): stock ticker
        Returns:
            (int): ask size
        """
        data = self._get_quote_list(stock_names,'symbol, ask_size')
        result = {}
        for item in data:
            if item[1] != 'None':
                result[item[0]] = int(item[1])

        self.logger.info('successfully getting ask_size for stock ' + stock_names + '...')
        return result

    def bid_price(self, stock_names = ''):
        """get asking price for a stock
        Note:
            queries `quote` endpoint, dict wrapper
        Args:
            stock (str): stock ticker
        Returns:
            (float): ask price
        """
        data = self._get_quote_list(stock_names,'symbol, bid_price')
        result = {}
        for item in data:
            if item[1] != 'None':
                result[item[0]] = float(item[1])

        self.logger.info('successfully getting bid_price for stock ' + stock_names + '...')
        return result

    def bid_size(self, stock_names = ''):
        """get ask size for a stock
        Note:
            queries `quote` endpoint, dict wrapper
        Args:
            stock (str): stock ticker
        Returns:
            (int): ask size
        """
        data = self._get_quote_list(stock_names,'symbol, bid_size')
        result = {}
        for item in data:
            if item[1] != 'None':
                result[item[0]] = int(item[1])

        self.logger.info('successfully getting bid_size for stock ' + stock_names + '...')
        return result

    def previous_close_price(self, stock_names = ''):
        """get previous closing price for a stock
        Note:
            queries `quote` endpoint, dict wrapper
        Args:
            stock (str): stock ticker
        Returns:
            (float): previous closing price
        """
        data = self._get_quote_list(stock_names,'symbol, previous_close')
        result = {}
        for item in data:
            if item[1] != 'None':
                result[item[0]] = float(item[1])

        self.logger.info('successfully getting previous_close_price for stock ' + stock_names + '...')
        return result

    def adjusted_previous_close_price(self, stock_names = ''):
        """get adjusted previous closing price for a stock
        Note:
            queries `quote` endpoint, dict wrapper
        Args:
            stock (str): stock ticker
        Returns:
            (float): adjusted previous closing price
        """
        data = self._get_quote_list(stock_names,'symbol, adjusted_previous_close')
        result = {}
        for item in data:
            if item[1] != 'None':
                result[item[0]] = float(item[1])

        self.logger.info('successfully getting adjusted_previous_close_price for stock ' + stock_names + '...')
        return result

    def updated_time(self, stock_names = ''):
        """get last update datetime
        Note:
            queries `quote` endpoint, dict wrapper
        Args:
            stock (str): stock ticker
        Returns:
            (str): last update datetime
        """
        data = self._get_quote_list(stock_names,'symbol, updated_at')
        result = {}
        for item in data:
            if item[1] != 'None':
                result[item[0]] = str(item[1])

        self.logger.info('successfully getting updated_time for stock ' + stock_names + '...')
        return result

    def last_extended_hours_trade_price(self, stock_names = ''):
        """get extended hours trade price
        Note:
            queries `quote` endpoint, dict wrapper
        Args:
            stock (str): stock ticker
        Returns:
            (float): last update datetime
        """
        data = self._get_quote_list(stock_names,'symbol, last_extended_hours_trade_price')
        result = {}
        for item in data:
            if item[1] != 'None':
                result[item[0]] = float(item[1])

        self.logger.info('successfully getting last_extended_hours_trade_price for stock ' + stock_names + '...')
        return result


    ############################################################
    # GET DATA ABOUT STOCKS FROM HISTORICALS
    ############################################################
    def historicals(self, stock_names, interval, span, bounds = Bounds.REGULAR):
        """fetch historical data for stock
        support maximum 75 stocks
        Note: valid interval/span configs
            interval = 5minute | 10minute + span = day, week
            interval = day + span = year
            interval = week
        Args:
            stock_names (str): stock ticker
            interval (str): resolution of data
            span (str): length of data
            bounds (:enum:`Bounds`, optional): 'extended' or 'regular' trading hours
        Returns:
            (:obj:`dict`) values returned from `historicals` endpoint
        """
        if isinstance(bounds, str): #recast to Enum
            bounds = Bounds(bounds)
        stock_names = stock_names.replace(' ', '')
        isSingle = False
        if stock_names.find(',') == -1:
            url = str(self.endpoints['historicals']) + stock_names + \
                '/?interval=' + interval + '&span=' + span + '&bounds=' + bounds.name.lower()
            isSingle = True
        else:
            url = str(self.endpoints['historicals']) + "?symbols=" + stock_names + \
                '&interval=' + interval + '&span=' + span + '&bounds=' + bounds.name.lower()
        try:
            http_result = requests.get(url)
            http_result.raise_for_status()
            data = http_result.json()
        except requests.exceptions.HTTPError:
            raise NameError('Invalid Symbols: ' + str(stock_names))

        if isSingle:
            return {stock_names:data['historicals']}

        result = {}
        data = data["results"]
        stocks = stock_names.split(',')
        for i in range(len(stocks)):
            result[stocks[i]] = data[i]['historicals']

        final_result = {}

        for stock_name in result:
            raw_data = result[stock_name]
            reformat_data = defaultdict(list)
            for i in range(len(raw_data)):
                for key in raw_data[i]:
                    reformat_data[key].append(raw_data[i][key])

            final_result[stock_name] = reformat_data

        self.logger.info('successfully getting historicals for stock ' + stock_names + '...')
        return final_result

    ############################################################
    # GET DATA ABOUT FUNDAMENTALS
    ############################################################
    def fundamentals(self, stock_names = ''):
        """find stock fundamentals data
        Args:
            (str): stock ticker
        Returns:
            (:obj:`dict`): contents of `fundamentals` endpoint
        """
        url = ''
        stock_names = stock_names.replace(' ', '')
        isSingle = False
        if stock_names.find(',') == -1:
            url = str(self.endpoints['fundamentals']) + str(stock_names.upper()) + "/"
            isSingle = True
        else:
            url = str(self.endpoints['fundamentals']) + '?symbols=' + stock_names
        print url
        try:
            http_result = requests.get(url)
            http_result.raise_for_status()
            data = http_result.json()
        except requests.exceptions.HTTPError:
            raise NameError('Invalid Symbol: ' + stock_names) #TODO wrap custom exception

        result = [data] if isSingle else data['results']
        final_result = {}
        stocks = stock_names.split(',')
        for i in range(len(stocks)):
            final_result[stocks[i]] = result[i]

        self.logger.info('successfully getting fundamentals for stock ' + stock_names + '...')
        return final_result

    ############################################################
    # GET DATA ABOUT PORTFOLIOS
    ############################################################
    def _portfolios(self):
        """Returns the user's portfolio data."""
        http_result = self.session.get(self.endpoints['portfolios'])
        http_result.raise_for_status()
        self.portfolio = http_result.json()['results'][0]

    def adjusted_equity_previous_close(self):
        """wrapper for portfolios
        get `adjusted_equity_previous_close` value
        """
        self.logger.info('successfully getting adjusted_equity_previous_close...')
        return float(self.portfolio['adjusted_equity_previous_close'])

    def equity_previous_close(self):
        """wrapper for portfolios
        get `equity_previous_close` value
        """
        self.logger.info('successfully getting equity_previous_close...')
        return float(self.portfolio['equity_previous_close'])

    def withdrawable_amount(self):
        """wrapper for portfolios
        get `withdrawable_amount` value
        """
        self.logger.info('successfully getting withdrawable_amount...')
        return float(self.portfolio['withdrawable_amount'])

    def equity(self):
        """wrapper for portfolios
        get `equity` value
        """
        self.logger.info('successfully getting equity...')
        return float(self.portfolio['equity'])

    def last_core_equity(self):
        """wrapper for portfolios
        get `last_core_equity` value
        """
        self.logger.info('successfully getting last_core_equity...')
        return float(self.portfolio['last_core_equity'])


    def excess_margin(self):
        """wrapper for portfolios
        get `excess_margin` value
        """
        self.logger.info('successfully getting excess_margin...')
        return float(self.portfolio['excess_margin'])

    def extended_hours_equity(self):
        """wrapper for portfolios
        get `extended_hours_equity` value
        """
        try:
            self.logger.info('successfully getting extended_hours_equity...')
            return float(self.portfolio['extended_hours_equity'])
        except TypeError:
            return None

    def market_value(self):
        """wrapper for portfolios
        get `market_value` value
        """
        self.logger.info('successfully getting market_value...')
        return float(self.portfolio['market_value'])

    def extended_hours_market_value(self):
        """wrapper for portfolios
        get `extended_hours_market_value` value
        """
        try:
            self.logger.info('successfully getting extended_hours_market_value...')
            return float(self.portfolio['extended_hours_market_value'])
        except TypeError:
            return None

    def last_core_market_value(self):
        """wrapper for portfolios
        get `last_core_market_value` value
        """
        self.logger.info('successfully getting last_core_market_value...')
        return float(self.portfolio['last_core_market_value'])

    def order_history(self):
        """wrapper for portfolios
        get orders from account
        """
        http_result = self.session.get(self.endpoints['orders']).json()
        result = http_result['results']
        while http_result['next'] != None:
            http_result = self.session.get(http_result['next']).json()
            result += http_result['results']
        self.logger.info('successfully getting order_history...')
        return result

    def dividends(self):
        """wrapper for portfolios
        get dividends from account
        """
        http_result = self.session.get(self.endpoints['dividends']).json()
        result = http_result['results']
        while http_result['next'] != None:
            http_result = self.session.get(http_result['next']).json()
            result += http_result['results']

        self.logger.info('successfully getting dividends...')
        return result

    ############################################################
    # GET DATA ABOUT PORSITIONS
    ############################################################
    def positions(self):
        """Returns the user's positions data."""
        http_result = self.session.get(self.endpoints['positions']).json()
        result = http_result['results']
        while http_result['next'] != None:
            http_result = self.session.get(http_result['next']).json()
            result += http_result['results']

        self.logger.info('successfully getting positions...')
        return result

    def securities_owned(self):
        """
        Returns a list of symbols of securities of which there are more
        than zero shares in user's portfolio.
        """
        http_result = self.session.get(self.endpoints['positions']+'?nonzero=true').json()
        result = http_result['results']
        while http_result['next'] != None:
            http_result = self.session.get(http_result['next']).json()
            result += http_result['results']

        self.logger.info('successfully getting securities_owned...')
        return result


    ############################################################
    # FUNCTION ABOUT PLACING OR CANCELLING ORDERS
    ############################################################
    def _place_order(
            self,
            instrument,
            quantity,
            bid_price = 0.0,
            stop_price = 0.0,
            transaction = None,
            trigger = 'immediate',
            order = 'market',
            time_in_force = 'gfd'
        ):
        """place an order with Robinhood
        Notes:
            OMFG TEST THIS PLEASE!
            Just realized this won't work since if type is LIMIT you need to use "price" and if
            a STOP you need to use "stop_price".  Oops.
            Reference: https://github.com/sanko/Robinhood/blob/master/Order.md#place-an-order
        Args:
            instrument (dict): the RH URL and symbol in dict for the instrument to be traded
            quantity (int): quantity of stocks in order
            bid_price (float): price for order
            transaction (:enum:`Transaction`): BUY or SELL enum
            trigger (:enum:`Trigger`): IMMEDIATE or STOP enum
            order (:enum:`Order`): MARKET or LIMIT
            time_in_force (:enum:`TIME_IN_FORCE`): GFD, GTC, IOC, FOK, OPG
        Returns:
            (:obj:`requests.request`): result from `orders` put command
        """
        if isinstance(transaction, str):
            transaction = Transaction(transaction)
        if isinstance(trigger, str):
            trigger = Trigger(trigger)
        if isinstance(order, str):
            order = Order(order)
        if isinstance(time_in_force, str):
            time_in_force = Time_In_Force(time_in_force)

        if not bid_price:
            bid_price = self._quote_data(stock_names = instrument['symbol'], is_save = False)['bid_price']

        command = 'curl -v ' + self.endpoints['orders'] + ' -H "Accept: application/json" -H "Authorization: Token ' + self.auth_token + '"' + \
            ' -d account=' + self.account()['url'] + \
            ' -d instrument=' + unquote(instrument['url']) + \
            ' -d symbol=' + instrument['symbol'] + \
            ' -d type=' + order.name.lower() + \
            ' -d time_in_force=' + time_in_force.name.lower() + \
            ' -d trigger=' + trigger.name.lower() + \
            ' -d quantity=' + str(quantity) + \
            ' -d side=' + transaction.name.lower()

        if order.name.lower() == 'limit':
            command = command + ' -d price=' + str(bid_price)
        if trigger.name.lower() == 'stop':
            command = command + ' -d stop_price=' + str(stop_price)

        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr= subprocess.PIPE)
        http_result, err = p.communicate()
        if len(http_result) < 1:
            print 'Error connecting to server:', err
            self.logger.error(err + '...')
            return None
        else:
            print 'Connection successful.'
        http_result = json.loads(http_result)
        return http_result

    def place_buy_order(
            self,
            instrument,
            quantity,
            bid_price = 0.0,
            stop_price = 0.0,
            trigger = 'immediate',
            order = 'market',
            time_in_force = 'gfd'
    ):
        """wrapper for placing buy orders
        Args:
            instrument (dict): the RH URL and symbol in dict for the instrument to be traded
            quantity (int): quantity of stocks in order
            bid_price (float): price for order
        Returns:
            (:obj:`requests.request`): result from `orders` put command
        """
        transaction = Transaction.BUY
        result = self._place_order(
                instrument = instrument,
                quantity = quantity,
                bid_price = bid_price,
                transaction = transaction,
                trigger = trigger,
                order = order,
                time_in_force = time_in_force)
        if result:
            info_str = '.......success in placing buy order for ' + instrument['symbol'] + '.......'
            info_str += 'quantity: ' + result['quantity'] + '\t' + \
                'price: ' + result['price'] + '\t' + \
                'cumulative quantity: ' + result['cumulative_quantity'] + '\t' + \
                'created at ' + result['created_at'] + '\t' + \
                'fees: ' + result['fees']
            print info_str
            self.logger.info(info_str + '...')

        return result

    def place_sell_order(
            self,
            instrument,
            quantity,
            bid_price = 0.0,
            stop_price = 0.0,
            trigger = 'immediate',
            order = 'market',
            time_in_force = 'gfd'
    ):
        """wrapper for placing sell orders
        Args:
            instrument (dict): the RH URL and symbol in dict for the instrument to be traded
            quantity (int): quantity of stocks in order
            bid_price (float): price for order
        Returns:
            (:obj:`requests.request`): result from `orders` put command
        """
        owned_stocks = self.invested_stocks()
        if instrument['symbol'] not in owned_stocks or quantity > owned_stocks[instrument['symbol']]['quantity']:
            self.logger.error("selling " + str(quantity) + ' ' + instrument['symbol'] + ' failed...')
            print "selling " + str(quantity) + ' ' + instrument['symbol'] + ' failed...'
            return None

        transaction = Transaction.SELL
        result = self._place_order(
                instrument = instrument,
                quantity = quantity,
                bid_price = bid_price,
                transaction = transaction,
                trigger = trigger,
                order = order,
                time_in_force = time_in_force)

        if result:
            info_str = '.......success in placing buy order for ' + instrument['symbol'] + '.......'
            info_str += 'quantity: ' + result['quantity'] + '\t' + \
                'price: ' + result['price'] + '\t' + \
                'cumulative quantity: ' + result['cumulative_quantity'] + '\t' + \
                'created at ' + result['created_at'] + '\t' + \
                'fees: ' + result['fees']
            print info_str
            self.logger.info(info_str + '...')
        return result

    def cancel_order(self, order):
        command = 'curl -v ' + order['cancel'] + ' -H "Accept: application/json" -H "Authorization: Token ' + self.auth_token + '"' + \
            ' -d ""'
        p = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        http_result, err = p.communicate()
        if len(http_result) < 1:
            print 'Error connecting to server:', err
            self.logger.error(err + '...')
            return None
        else:
            print 'Connection successful.'
        http_result = json.loads(http_result)
        self.logger.info('successfully canceling order ' + order['cancel'] + '...')

        return http_result

    ############################################################
    # FUNCTION ABOUT PROFITS AND RATES
    ############################################################
    def invested_stocks(self):
        securities = self.securities_owned()
        invest_stocks = {}
        for item in securities:
            fields = {'quantity': int(float(item['quantity'])), 'created_at': item['created_at'], \
                'updated_at': item['updated_at'], 'average_buy_price': float(item['average_buy_price'])}

            invest_stocks[self.instruments_symbol[item['instrument']]] = fields

        self.logger.info('successfully getting invested_stocks...')
        return invest_stocks
