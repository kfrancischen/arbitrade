import six

if six.PY3:
    from arbitrade.util import robinhood_api
else:
    from util import robinhood_api