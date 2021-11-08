from yahoo_oauth import OAuth2
import json


def login_yahoo_api():
    global oauth
    oauth = OAuth2(None, None, from_file='./auth/oauth2yahoo.json')
    if not oauth.token_is_valid():
        oauth.refresh_access_token()


def update_transactions():
    # TRANSACTIONS
    # Convert existing 'Transactions_new.json' into 'Transactions_old.json' before
    with open('transactions/Transaction_new.json', 'r') as load_file:  # load new_transactions
        new_transactions = json.load(load_file)

    with open('transactions/Transaction_old.json', 'w') as outfile:  # save the new_transactions as old
        json.dump(new_transactions, outfile)

    login_yahoo_api() # get the newest transactions and write over the existing new_transactions
    url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/{}.l.{}/transactions'.format(game_key, league_id)
    response = oauth.session.get(url, params={'format': 'json'})
    r = response.json()
    with open('transactions/Transaction_new.json', 'w') as outfile:
        json.dump(r, outfile)


def update_league():
    login_yahoo_api()
    url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/{}.l.{}/'.format(game_key, league_id)
    response = oauth.session.get(url, params={'format': 'json'})
    r = response.json()
    with open('league.json', 'w') as outfile:
        json.dump(r, outfile, indent=4)


def update_standings():
    login_yahoo_api()
    url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/{}.l.{}/standings'.format(game_key, league_id)
    response = oauth.session.get(url, params={'format': 'json'})
    r = response.json()
    with open('standings.json', 'w') as outfile:
        json.dump(r, outfile, indent=4)


def update_scoreboards():
    login_yahoo_api()
    week = 1
    while week < num_weeks+1:
        url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/{}.l.{}/scoreboard;week={}'.format(game_key, league_id, week)
        response = oauth.session.get(url, params={'format': 'json'})
        r = response.json()
        file_name = 'week_' + str(week) + 'scoreboard.json'
        with open('weekly_scoreboard/' + file_name, 'w') as outfile:
            json.dump(r, outfile, indent=4)
        week += 1


def update_yahoo_league_info():
    # UPDATE LEAGUE GAME ID
    login_yahoo_api()
    url = 'https://fantasysports.yahooapis.com/fantasy/v2/game/nfl'
    response = oauth.session.get(url, params={'format': 'json'})
    r = response.json()
    with open('YahooGameInfo.json', 'w') as outfile:
        json.dump(r, outfile, indent=4)

    global game_key
    game_key = r['fantasy_content']['game'][0]['game_key'] # game key as type-string


def update_rosters():
    # WEEKLY ROSTERS - TAKES A WHILE
    login_yahoo_api()
    for week in range(1, num_weeks+1):
        for team in range(1, num_teams+1):
            url = 'https://fantasysports.yahooapis.com/fantasy/v2/team/{}.l.{}.t.{}/roster;week={}'.format(game_key, league_id, team, week)
            response = oauth.session.get(url, params={'format': 'json'})
            r = response.json()
            file_name = 'team_{}_wk_{}_roster.json'.format(team, week)
            with open('rosters/week_{}/{}'.format(week, file_name), 'w') as outfile:
                json.dump(r, outfile, indent=4)
        print('Week {} roster update - done'.format(week))


def get_current_week():
    current_week = 1
    #with open('./league.json', 'r') as fobj:
    #    info = json.load(fobj)
    #current_week = info['fantasy_content']['league'][0]['current_week']
    return current_week


def main():
    global current_week
    current_week = get_current_week()

    with open('./Initial_Setup/league_info_form.txt', 'r') as f:
        rosters = eval(f.read())

    global num_teams
    num_teams = rosters['num_teams']

    global num_weeks
    num_weeks = rosters['num_weeks']
    
    global league_id
    league_id = str(rosters['league_id'])

    update_all()


def update_all():
    update_yahoo_league_info()
    print('Yahoo League Info Updated')

    update_league()
    print('League update - Done')

    update_standings()
    print('Standings update - Done')

    update_scoreboards()
    print('Scoreboards update - Done')

    update_transactions()
    print('Transactions update - Done')

    update_rosters()
    print('Rosters update - Done')

    print('Update Complete')


if __name__ == '__main__':
    main()
