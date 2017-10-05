'''
file created by Kaifeng Chen, 09/30/2017
to visualizing real time tading
'''

import PyQt4
from util import robinhood_api

class robinhood_visualizer:
    cur_path = os.path.dirname(__file__)
    logger = logging.getLogger('Robinhood_API')
    hdlr = logging.FileHandler(cur_path + '/../Robinhood_Visualizer.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
