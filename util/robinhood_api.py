'''
file created by Kaifeng Chen, 09/27/2017
to access Robinhood API
links here:
https://api.robinhood.com/
'''
import subprocess, json

class robinhood_session:
    def __init__(self, username, password, do_print = False):
        self.do_print = do_print
        self._login(username, password)

    def _command(self, string, stock_name = '', extra = '"'):
        if stock_name != '':
            stock_name = stock_name + '/'
        command = 'curl -v https://api.robinhood.com/' + string + \
            '/' + stock_name + ' -H "Accept: application/json" -H "Authorization: Token ' + \
            self.token + extra
        return command

    def _login(self, username, password):
        print "Logging in..."
        command = 'curl -v https://api.robinhood.com/api-token-auth/ -H "Accept: application/json" -d "username=' + username + '&password=' + password + '"'
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr= subprocess.PIPE)
        self.token, err = p.communicate()
        if len(self.token) < 1:
            print 'Error connecting to server:', err
        else:
            print 'Connection successful.'
        self.token = self.token[10:-2]

    def logout(self):
        print "Logging out..."
        command = self._command('api-token-logout', '" -d ""')
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr= subprocess.PIPE)
        out, err = p.communicate()

    def accounts(self):
        print 'accounts...'
        command = self._command('accounts')
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr= subprocess.PIPE)
        out, err = p.communicate()
        out = json.loads(out)
        if self.do_print:
            result = out["results"]
            for dic in result:
                for key in dic:
                    print key,': ', dic[key]
        return out

    def mfa(self):
        command = self._command('mfa')
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr= subprocess.PIPE)
        out, err = p.communicate()
        out = json.loads(out)
        if self.do_print:
            for key in out:
                print key, ': ', out[key]
        return out


    def margin_interest_charges(self):
        command = self._command('cash_journal/margin_interest_charges')
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr= subprocess.PIPE)
        out, err = p.communicate()
        out = json.loads(out)
        if self.do_print:
            for key in out:
                print key, ': ', out[key]
        return out


    def margin_upgrades(self):
        command = self._command('margin/upgrades')
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr= subprocess.PIPE)
        out, err = p.communicate()
        out = json.loads(out)
        if self.do_print:
            for key in out:
                print key, ': ', out[key]
        return out


    def instruments(self):
        command = self._command('instruments')
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr= subprocess.PIPE)
        out, err = p.communicate()
        out = json.loads(out)
        if self.do_print:
            for key in out:
                print key, ': ', out[key]
        return out

    def quotes(self, stock_name):
        command = self._command('quotes', stock_name = stock_name)
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr= subprocess.PIPE)
        out, err = p.communicate()
        out = json.loads(out)
        if self.do_print:
            for key in out:
                print key, ': ', out[key]
        return out

    def fundamentals(self, stock_name):
        command = self._command('fundamentals', stock_name = stock_name)
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr= subprocess.PIPE)
        out, err = p.communicate()
        out = json.loads(out)
        if self.do_print:
            for key in out:
                print key, ': ', out[key]
        return out


    def orders(self):
        print "orders..."
        # this is the function for placing and cancelling orders

    '''
    def historicals(self):
        
        
    def subscription_fees(self):
        # TO CHECK

    def id_documents(self):
        # TO CHECK

    def portflios(self):


    def markets(self):


    def wire_relationships(self):


    def subscriptions(self):


    def wire_transfers(self):


    def dividents(self):

    def applications(self):

    def notification_settings(self):
        # not important

    def user(self):

    def notifications(self):

    def ach_queued_deposit(self):

    def ach_relationships(self):

    def ach_deposit_schedules(self):

    def ach_iav_auth(self):

    def ach_transfers(self):


    def positions(self):


    def watchlists(self):

    def document_requests(self):

    def edocuments(self):

    def password_reset(self):

    def password_change(self):
    '''