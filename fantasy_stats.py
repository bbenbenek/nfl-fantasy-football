import pandas as pd
from yahoo_oauth import OAuth2
import json
from json import dumps
import datetime

class Yahoo_Api():
    def __init__(self, consumer_key, consumer_secret,
                access_key):
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        self._access_key = access_key
        self._authorization = None
    def _login(self):
        global oauth
        oauth = OAuth2(None, None, from_file='./auth/oauth2yahoo.json')
        if not oauth.token_is_valid():
            oauth.refresh_access_token()

class UpdateData():
    #def __init__(self):

    def UpdateTransactions(self):
        # TRANSACTIONS
        # Convert existing 'Transactions_new.json' into 'Transactions_old.json' before
        #### downloading up-to-date new transactions
        load_file = open('./transactions/Transaction_old.json') # load old_transactions
        old_transactions = json.load(load_file)
        load_file.close()

        load_file = open('./transactions/Transaction_new.json') # load new_transactions (this will get written over once we download the newest data from Yahoo)
        new_transactions = json.load(load_file)
        load_file.close()

        with open('./transactions/Transaction_old.json', 'w') as outfile: # save the new*_transactions as old so we can compare the actual new transactions
            json.dump(new_transactions, outfile)

        load_file = open('./transactions/Transaction_old.json') # now load the *new* old_transactions as the base for comparison
        old_transactions = json.load(load_file)
        load_file.close()

        yahoo_api._login() # get the newest transactions and write over the existing new_transactions
        url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/'+game_key+'.l.'+league_id+'/transactions'
        response = oauth.session.get(url, params={'format': 'json'})
        r = response.json()
        with open('./transactions/Transaction_new.json', 'w') as outfile:
            json.dump(r, outfile)
        #### load in newest transaction data
        load_file = open('./transactions/Transaction_new.json')
        new_transactions = json.load(load_file)
        load_file.close()

        #### get number of new transactions since last transaction download
        old_trans = old_transactions['fantasy_content']['league'][1]['transactions']['count']
        new_trans = new_transactions['fantasy_content']['league'][1]['transactions']['count']
        newest_trans = new_trans-old_trans

        transactions = new_transactions['fantasy_content']['league'][1]['transactions']

        #load team number and names references as a dictionary
        team_numbers = {}
        with open('./teams/team_numbers.txt', 'r') as f:
            #for line in f:
            team_numbers= eval(f.read())

        if new_trans > 0: # only run if there are new transactions
            transaction = 0

            #for transaction in range(len(transactions)-1):
            for transaction in range(newest_trans-1, -1, -1):

                # transaction(tr) info
                tr_num = str(transaction).zfill(2) #adds zeros to the front of the number to keep it all the same length
                tr_id = transactions[str(transaction)]['transaction'][0]['transaction_id']
                tr_type = transactions[str(transaction)]['transaction'][0]['type']
                tr_date = datetime.datetime.fromtimestamp(int(transactions[str(transaction)]['transaction'][0]['timestamp'])).strftime('%m-%d-%Y %H:%M:%S')

                # DROPS ### need to update to handle multiple drops, can only handle 1 at a time right now and "AND also dropped..."
                if tr_type == 'drop':
                    players = transactions[str(transaction)]['transaction'][1]['players']
                    for player in range(len(players)-1):
                        tm_name = players[str(player)]['player'][1]['transaction_data']['source_team_name']
                        tm_key = transactions[str(transaction)]['transaction'][1]['players']['0']['player'][1]['transaction_data'][0]['destination_team_key']
                        tm_real_nm = team_numbers[str(tm_key)]
                        player_name = players[str(player)]['player'][0][2]['name']['full']
                        status = tm_name, " (", tm_real_nm ,") dropped", player_name

                        # print(status)
                        # add code to append transaction to list, this was originalyl used to Tweet every transaction


                # TRADES
                elif tr_type == "trade":
                    pX_name = transactions[str(transaction)]['transaction'][1]['players']['0']['player'][0][2]['name']['full']
                    pX_pos = transactions[str(transaction)]['transaction'][1]['players']['0']['player'][0][4]['display_position']
                    pY_name = transactions[str(transaction)]['transaction'][1]['players']['1']['player'][0][2]['name']['full']
                    pY_pos = transactions[str(transaction)]['transaction'][1]['players']['1']['player'][0][4]['display_position']
                    trader = transactions[str(transaction)]['transaction'][0]['trader_team_name']
                    trader_key = transactions[str(transaction)]['transaction'][0]['trader_team_key']
                    trader_real_nm = team_numbers[str(trader_key)]
                    tradee = transactions[str(transaction)]['transaction'][0]['tradee_team_name']
                    tradee_key = transactions[str(transaction)]['transaction'][0]['tradee_team_key']
                    tradee_real_nm = team_numbers[str(tradee_key)]

                    trade = trader + " (" +trader_real_nm+ ") traded "+ pX_name+ \
                                "-"+ pX_pos+ " to "+ tradee+ " (" + tradee_real_nm +") for "+ pY_name+ "-"+ pY_pos
                    status = trade

                    # print(status)
                    # add code to append transaction to list, this was originalyl used to Tweet every transaction


                # ADD/DROP
                elif tr_type == "add/drop":
                    tm_name = transactions[str(transaction)]['transaction'][1]['players']['0']['player'][1]['transaction_data'][0]['destination_team_name']
                    tm_key = transactions[str(transaction)]['transaction'][1]['players']['0']['player'][1]['transaction_data'][0]['destination_team_key']
                    tm_real_nm = team_numbers[str(tm_key)]
                    pl_add = transactions[str(transaction)]['transaction'][1]['players']['0']['player'][0][2]['name']['full']
                    pl_add_pos = transactions[str(transaction)]['transaction'][1]['players']['0']['player'][0][4]['display_position']
                    pl_drop = transactions[str(transaction)]['transaction'][1]['players']['1']['player'][0][2]['name']['full']
                    pl_drop_pos = transactions[str(transaction)]['transaction'][1]['players']['1']['player'][0][4]['display_position']
                    try:
                        faab = transactions[str(transaction)]['transaction'][0]['faab_bid']
                    except:
                        faab = '0'
                    if int(faab) > 0:
                        faab = transactions[str(transaction)]['transaction'][0]['faab_bid']
                        faab = " || FAAB Spent: $"+ faab
                    else:
                        faab = ''

                    add_drop = tm_name + " (" + tm_real_nm + ") added " + \
                                pl_add + "-" + pl_add_pos + " and dropped " + pl_drop + "-" + pl_drop_pos + faab
                    status = add_drop

                    # print(status)
                    # add code to append transaction to list, this was originalyl used to Tweet every transaction

                # ADD
                elif tr_type == 'add':
                    players = transactions[str(transaction)]['transaction'][1]['players']
                    for player in range(0, len(players)-1):
                        tm_name = players[str(player)]['player'][1]['transaction_data'][0]['destination_team_name']
                        tm_key = players[str(player)]['player'][1]['transaction_data'][0]['destination_team_key']
                        tm_real_nm = team_numbers[str(tm_key)]
                        player_name = players[str(player)]['player'][0][2]['name']['full']
                        status = tm_name, " (", tm_real_nm, ") added", player_name

                        # print(status)
                        # add code to append transaction to list, this was originalyl used to Tweet every transaction

                # COMMISH
                elif tr_type == "commish":
                    status = "Commish made some changes to [Enter League Name Here]"

                    # print(status)
                    # add code to append transaction to list, this was originalyl used to Tweet every transaction

                transaction += transaction
            return;

    def UpdateLeague(self):
        # LEAGUE OVERVIEW
        yahoo_api._login()
        url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/'+game_key+'.l.'+league_id+'/'
        response = oauth.session.get(url, params={'format': 'json'})
        r = response.json()
        with open('league.json', 'w') as outfile:
            json.dump(r, outfile)
        return;

    def UpdateLeagueStandings(self):
        # STANDINGS
        yahoo_api._login()
        url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/'+game_key+'.l.'+league_id+'/standings'
        response = oauth.session.get(url, params={'format': 'json'})
        r = response.json()
        with open('standings.json', 'w') as outfile:
            json.dump(r, outfile)
        
        return;

    def UpdateScoreboards(self):
        # WEEKLY SCORE BOARD
        yahoo_api._login()
        week = 1
        while week < num_weeks+1: #assumes 16 week-schedule
            url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/'+game_key+'.l.'+league_id+'/scoreboard;week='+str(week)
            response = oauth.session.get(url, params={'format': 'json'})
            r = response.json()
            file_name = 'week_' + str(week) + 'scoreboard.json'
            with open('./weekly_scoreboard/'+file_name, 'w') as outfile:
                json.dump(r, outfile)
            week += 1
        return;

    def UpdateYahooLeagueInfo(self):
        # UPDATE LEAGUE GAME ID
        yahoo_api._login()
        url = 'https://fantasysports.yahooapis.com/fantasy/v2/game/nfl'
        response = oauth.session.get(url, params={'format': 'json'})
        r = response.json()
        with open('YahooGameInfo.json', 'w') as outfile:
            json.dump(r, outfile)
            
        global game_key
        game_key = r['fantasy_content']['game'][0]['game_key'] # game key as type-string
        return;


    def UpdateRosters(self):
        # WEEKLY ROSTERS - TAKES A WHILE
        yahoo_api._login()
        week = 1
        for week in range(1, num_weeks+1): #assumes 16-week schedule
            team = 1
            for team in range(1, num_teams+1): #assumes 12-team league
                url = 'https://fantasysports.yahooapis.com/fantasy/v2/team/'+game_key+'.l.'+league_id+'.t.'+str(team)+'/roster;week='+str(week)
                response = oauth.session.get(url, params={'format': 'json'})
                r = response.json()
                file_name = 'team_'+str(team)+'_wk_' + str(week) + '_roster.json'
                with open('./rosters/week_'+str(week)+'/'+ file_name, 'w') as outfile:
                    json.dump(r, outfile)
                team =+ 1
            print("Week",week, "roster update - done")
            week += 1
        return;

def CurrentWeek():
    current_week = 1
    #with open('./league.json', 'r') as fobj:
    #    info = json.load(fobj)
    #current_week = info['fantasy_content']['league'][0]['current_week']
    return current_week;



### WHERE ALL THE MAGIC HAPPENS #########

def main():
##### Get Yahoo Auth ####

    # Yahoo Keys
    with open('./auth/oauth2yahoo.json') as json_yahoo_file:
        auths = json.load(json_yahoo_file)
    yahoo_consumer_key = auths['consumer_key']
    yahoo_consumer_secret = auths['consumer_secret']
    yahoo_access_key = auths['access_token']
    #yahoo_access_secret = auths['access_token_secret']
    json_yahoo_file.close()

#### Declare Yahoo, and Current Week Variable ####


    global yahoo_api
    yahoo_api = Yahoo_Api(yahoo_consumer_key, yahoo_consumer_secret, yahoo_access_key)#, yahoo_access_secret)

    global current_week
    current_week = CurrentWeek()

    with open('./Initial_Setup/league_info_form.txt', 'r') as f:
        rosters = eval(f.read())

    global num_teams
    num_teams = rosters['num_teams']

    global num_weeks
    num_weeks = rosters['num_weeks']
    
    global league_id
    league_id = str(rosters['league_id'])

#### Where the tweets happen ####
    bot = Bot(yahoo_api)
    bot.run()


class Bot():
    def __init__(self, yahoo_api):
        self._yahoo_api = yahoo_api

    def run(self):
        # Data Updates
        UD = UpdateData()
                           
        UD.UpdateYahooLeagueInfo()
        print('Yahoo League Info Updated')
                           
        UD.UpdateLeague()
        print('League update - Done')
                           
        UD.UpdateLeagueStandings()
        print('Standings update - Done')
                           
        UD.UpdateScoreboards()
        print('Scoreboards update - Done')
                           
        UD.UpdateTransactions()
        print('Transactions update - Done')
                           
        UD.UpdateRosters()
        print('Rosters update - Done')
                           
        print('Update Complete')

if __name__ == "__main__":
    main()

    try:
        pass
    except Exception as e:
        raise
    else:
        pass
