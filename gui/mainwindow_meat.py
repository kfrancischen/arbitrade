'''
file created by Kaifeng Chen, 10/11/2017
ui function for main window
'''
from PyQt5 import QtCore, QtGui, QtWidgets
from gui import Ui_Arbitrade

class mainwindow_meat(QMainWindow):
    def __init__(self, session):
        '''
        initialize mainwindow UI
        '''
        super(mainwindow_meat, self).__init__()

        self.session = session
        self.ui = Ui_Arbitrade()
        self.ui.setupUi(self)


    def add_content_to_portfolio_table_widget(self):
        
    def add_content_to_date_time_view(self):
