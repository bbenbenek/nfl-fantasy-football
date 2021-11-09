from yahoo_oauth import OAuth2
import time
import sys
import json
TEAMS = ['Popcorn', 'Quads', 'Dynasty', 'Doinkers', 'Booze', 'Kickitungs', 'Mustard', 'Sandbags', 'Squirt', 'Sauce',
         'BONEZONE', 'Fútbol']


def parse_data(response):
    if 'error' in response:
        return None
    matchups = response['fantasy_content']['league'][1]['scoreboard']['0']['matchups']
    data = {}
    for i in range(6):
        teams = matchups[str(i)]['matchup']['0']['teams']
        for j in range(2):
            data_list = teams[str(j)]['team']
            team_name = ''
            win_probability = 0.0
            points = 0.0
            proj_points = 0.0
            for item in data_list[0]:
                if 'name' in item:
                    team_name = item['name']
            if 'win_probability' in data_list[1]:
                win_probability = data_list[1]['win_probability']
                points = data_list[1]['team_points']['total']
                proj_points = data_list[1]['team_projected_points']['total']
            data.update({team_name: {'win_probability': win_probability, 'points': points, 'proj_points': proj_points}})
    return data


class Fantasy:
    def __init__(self, week, reset=False):
        self.oauth = OAuth2(None, None, from_file='./auth/oauth2yahoo.json')
        self.base_url = 'https://fantasysports.yahooapis.com/fantasy/v2/'
        self.game_key = self.update_yahoo_game_key()
        self.league_id = '29020'
        self.week = week
        self.interval = 30
        self.output_path = 'week_{}_scores.csv'.format(self.week)
        if reset:
            self.initialize_file()
        self.string_check = []
        self.current_string = ''

    def refresh_token(self):
        if not self.oauth.token_is_valid():
            self.oauth.refresh_access_token()

    def get_json_response(self, url):
        self.refresh_token()
        response = self.oauth.session.get(url, params={'format': 'json'})
        return response.json()

    def update_yahoo_game_key(self):
        r = self.get_json_response('{}game/nfl'.format(self.base_url))
        game_key = r['fantasy_content']['game'][0]['game_key']
        return game_key

    def initialize_file(self):
        print_string = 'Timestamp'
        for name in TEAMS:
            for field in ['PTS', 'PROJ', 'WPCT']:
                print_string += ',{} {}'.format(name, field)
        print_string += '\n'
        with open(self.output_path, 'w') as new_file:
            new_file.write(print_string)

    def is_data_changing(self):
        self.string_check.append(self.current_string)
        while len(self.string_check) > 20:
            self.string_check.pop(0)
        if len(set(self.string_check)) == 20:
            print('Data is not changing. Stopping loop.')
            return False
        return True

    def collect_data(self):
        start_time = time.time()
        while self.is_data_changing():
            response = self.get_json_response('{}league/{}.l.{}/scoreboard;week={}'.format(self.base_url, self.game_key, self.league_id, self.week))
            with open('test_jason.json', 'w') as test:
                json.dump(response, test, indent=4)
            timestamp = int(time.time())
            print_string = str(timestamp)
            data = parse_data(response)
            if data:
                for name in TEAMS:
                    for team in data:
                        if name in team:
                            name = team
                    print_string += ',' + str(data[name]['points'])
                    print_string += ',' + str(data[name]['proj_points'])
                    print_string += ',' + str(data[name]['win_probability'])
                    self.current_string += ',' + str(data[name]['points'])
                    self.current_string += ',' + str(data[name]['proj_points'])
                    self.current_string += ',' + str(data[name]['win_probability'])
                print_string += '\n'
                with open(self.output_path, 'a') as out_file:
                    out_file.write(print_string)
            time.sleep(self.interval)
        print('Elapsed time: {}'.format(time.time() - start_time))


def main(week, reset):
    fantasy = Fantasy(week, reset)
    fantasy.collect_data()


if __name__ == '__main__':
    argv = sys.argv
    reset_flag = False
    if len(argv) >= 2:
        week_num = str(argv[1])
        if '-r' in argv:
            reset_flag = True
        main(week_num, reset_flag)
    else:
        print('Argument error')
