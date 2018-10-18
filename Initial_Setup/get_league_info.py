import pandas as pd
from yahoo_oauth import OAuth2
import logging
oauth_logger = logging.getLogger('yahoo_oauth')
oauth_logger.disabled = True
import json
from json import dumps
import datetime


class Yahoo_Api():
    def __init__(self, consumer_key, consumer_secret,
                access_token):
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        self._access_token = access_token
        self._authorization = None
    def _login(self):
        global oauth
        oauth = OAuth2(None, None, from_file='../auth/oauth2yahoo.json')
        if not oauth.token_is_valid():
            oauth.refresh_access_token()

class UpdateData():

    def UpdateYahooLeagueInfo(self):
        # UPDATE LEAGUE GAME ID
        yahoo_api._login()
        url = 'https://fantasysports.yahooapis.com/fantasy/v2/game/nfl'
        response = oauth.session.get(url, params={'format': 'json'})
        r = response.json()
        with open('YahooGameInfo.json', 'w') as outfile:
            json.dump(r, outfile)
            return;
def main():
##### Get Yahoo Auth ####

    # Yahoo Keys
    with open('../auth/oauth2yahoo.json') as json_yahoo_file:
        auths = json.load(json_yahoo_file)
    yahoo_consumer_key = auths['consumer_key']
    yahoo_consumer_secret = auths['consumer_secret']
    yahoo_access_token = auths['access_token']
    #yahoo_access_secret = auths['access_token_secret']
    json_yahoo_file.close()

#### Declare Yahoo Variable ####

    global yahoo_api
    yahoo_api = Yahoo_Api(yahoo_consumer_key,
                            yahoo_consumer_secret,
                            yahoo_access_token,
                            #yahoo_access_secret)
                                )
#### Where the magic happen ####
    bot = Bot(yahoo_api)
    bot.run()

class Bot():
    def __init__(self, yahoo_api):

        self._yahoo_api = yahoo_api

    def run(self):
        # Data Updates
        UD = UpdateData()
        UD.UpdateYahooLeagueInfo()
        print('Update Complete')

if __name__ == "__main__":
    main()
