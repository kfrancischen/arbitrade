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

class Bounds(Enum):
    """enum for bounds in `historicals` endpoint"""
    REGULAR = 'regular'
    EXTENDED = 'extended'
    TRADING = 'trading'


class Transaction(Enum):
    """enum for buy/sell orders"""
    BUY = 'buy'
    SELL = 'sell'

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
    logger.addHandler(logging.NullHandler())

    def __init__(self):
        self.session = requests.session()
        self.session.proxies = getproxies()
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "X-Robinhood-API-Version": "1.0.0",
            "Connection": "keep-alive",
            "User-Agent": "Robinhood/823 (iPhone; iOS 7.1.2; Scale/2.00)"
        }
        self.session.headers = self.headers
        status = self.login_prompt()
        if status:
            print 'successfully logged in...'

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
            with open(home_dir + '/.robinhood_account', 'w') as f:
                f.write( username + '\t' + password)

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
            res = self.session.post(
                self.endpoints['login'],
                data = payload
            )
            res.raise_for_status()
            data = res.json()
        except requests.exceptions.HTTPError:
            raise RH_exceptions.LoginFailed

        if 'mfa_required' in data.keys():           #pragma: no cover
            raise RH_exceptions.TwoFactorRequired  #requires a second call to enable 2FA

        if 'token' in data.keys():
            self.auth_token = data['token']
            self.headers['Authorization'] = 'Token ' + self.auth_token
            return True
        return False

    def logout(self):
        """function to login"""
        try:
            req = self.session.post(self.endpoints['logout'])
            req.raise_for_status()
        except requests.exceptions.HTTPError as err_msg:
            warnings.warn('Failed to log out ' + repr(err_msg))

        self.headers['Authorization'] = None
        self.auth_token = None
        print "successfully logged out..."
        return req

    def account(self):
        """fetch account information
        Returns:
            (:obj:`dict`): `accounts` endpoint payload
        """
        res = self.session.get(self.endpoints['accounts'])
        res.raise_for_status()  #auth required
        res = res.json()
        return res['results'][0]

    ############################################################
    # GET DATA ABOUT STOCKS FROM QUOTES
    ############################################################
    def investment_profile(self):
        """fetch investment_profile"""
        res = self.session.get(self.endpoints['investment_profile'])
        res.raise_for_status()
        data = res.json()
        return data

    def instruments(self, stock):
        """fetch instruments endpoint
        Args:
            stock (str): stock ticker
        Returns:
            (:obj:`dict`): JSON contents from `instruments` endpoint
        """
        res = self.session.get(
            self.endpoints['instruments'],
            params={'query': stock.upper()}
        )
        res.raise_for_status()
        res = res.json()

        # if requesting all, return entire object so may paginate with ['next']
        if stock == "":
            return res

        return res['results']


    def quotes(self, stock_names):
        """Fetch quote for multiple stocks, in one single Robinhood API call
        Args:
            stock_names (str): stock tickers
        Returns:
            (:obj:`list` of :obj:`dict`): List of JSON contents from `quotes` endpoint, in the
            same order of input args. If any ticker is invalid, a None will occur at that position.
        """
        stock_names = stock_names.replace(' ', '')
        url = str(self.endpoints['quotes']) + "?symbols=" + ",".join(stock_names)
        try:
            req = requests.get(url)
            req.raise_for_status()
            data = req.json()
        except requests.exceptions.HTTPError:
            raise NameError('Invalid Symbols: ' + str(stock_names))

        return data["results"]

    def _quote_data(self, stock_names = ''):
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
        #Check for validity of symbol
        try:
            req = requests.get(url)
            req.raise_for_status()
            data = req.json()
        except requests.exceptions.HTTPError:
            raise NameError('Invalid Symbol: ' + stock)

        return data

    def news(self, stock_name):
        """fetch news endpoint
        Args:
            stock_name (str): stock ticker
        Returns:
            (:obj:`dict`) values returned from `news` endpoint
        """
        return self.session.get(self.endpoints['news'] + stock_name.upper() + "/").json()


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

        data = self._quote_data(stock_names)
        res = []

        if stock_names.find(',') != -1:
            for stock in data['results']:
                if stock == None:
                    continue
                res.append(append_stock(stock))
        else:
            res.append(append_stock(data))
        return res

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
            result[item[0]] = float(item[1])
            quote_str = item[0] + ": $" + item[1]
            self.logger.info(quote_str)
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
            result[item[0]] = float(item[1])
            quote_str = item[0] + ": $" + item[1]
            self.logger.info(quote_str)

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
            result[item[0]] = int(item[1])
            quote_str = item[0] + ": " + item[1]
            self.logger.info(quote_str)

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
            result[item[0]] = float(item[1])
            quote_str = item[0] + ": $" + item[1]
            self.logger.info(quote_str)

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
            result[item[0]] = int(item[1])
            quote_str = item[0] + ": " + item[1]
            self.logger.info(quote_str)

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
            result[item[0]] = float(item[1])
            quote_str = item[0] + ": $" + item[1]
            self.logger.info(quote_str)

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
            result[item[0]] = float(item[1])
            quote_str = item[0] + ": $" + item[1]
            self.logger.info(quote_str)

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
            result[item[0]] = str(item[1])
            quote_str = item[0] + ": " + item[1]
            self.logger.info(quote_str)

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
            result[item[0]] = float(item[1])
            quote_str = item[0] + ": " + item[1]
            self.logger.info(quote_str)

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
        if isinstance(bounds, basestring): #recast to Enum
            bounds = Bounds(bounds)
        stock_names = stock_names.replace(' ', '')
        isString = False
        if stock_names.find(',') == -1:
            url = str(self.endpoints['historicals']) + stock_names + \
                '/?interval=' + interval + '&span=' + span + '&bounds=' + bounds.name.lower()
            isString = True
        else:
            url = str(self.endpoints['historicals']) + "?symbols=" + stock_names + \
                '&interval=' + interval + '&span=' + span + '&bounds=' + bounds.name.lower()
        try:
            req = requests.get(url)
            req.raise_for_status()
            data = req.json()
        except requests.exceptions.HTTPError:
            raise NameError('Invalid Symbols: ' + str(stock_names))

        if isString:
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

        return final_result

    ############################################################
    # GET DATA ABOUT FUNDAMENTALS
    ############################################################
    # TODO

    ############################################################
    # GET DATA ABOUT PORTFOLIOS
    ############################################################
    # TODO

    ############################################################
    # GET DATA ABOUT PORSITIONS
    ############################################################
    # TODO

    ############################################################
    # FUNCTION ABOUT PLACING OR CANCELLING ORDERS
    ############################################################
    # TODO
