
# coding: utf-8

# In[17]:


import pandas as pd
import json
import sys
from yahoo_oauth import OAuth2
from json import dumps
from pandas.io.json import json_normalize
import seaborn

with open('../auth/oauth2yahoo.json') as json_yahoo_file:
    auths = json.load(json_yahoo_file)
yahoo_consumer_key = auths['consumer_key']
yahoo_consumer_secret = auths['consumer_secret']
yahoo_access_key = auths['access_token']

json_yahoo_file.close()

oauth = OAuth2(None, None, from_file='../auth/oauth2yahoo.json')
if not oauth.token_is_valid():
    oauth.refresh_access_token()

###############################################################
##### CREATE NEW DATAFRAME TO STORE WEEKLY LEAGUE ROSTERS #####
##### AND PLAYER POINTS PER WEEK                          #####
###############################################################
with open('../Initial_Setup/league_info_form.txt', 'r') as f:
    rosters = eval(f.read())

league_id = str(rosters['league_id'])

with open('../YahooGameInfo.json', 'r') as f:
    yahoo_info = json.load(f)
game_key = yahoo_info['fantasy_content']['game'][0]['game_key']


columns = ['first', 'last', 'full', 'team',
           'manager_name', 'ros_pos', 'position',
           'player_key', 'player_id', 'player_points']

#new_index= ['QB', 'WR1', 'WR2', 'WR3',
#            'RB1', 'RB2', 'TE', 'W/R/T',
#            'BN1', 'BN2', 'BN3', 'BN4', 'BN5', 'BN6',
#'BN7', 'BN8', 'BN9', 'BN10', 'K', 'DEF']

new_index = rosters['roster']

# insert lookup for team number

df_wk_players = pd.DataFrame(columns = ['player_points', 'player_key'])
df_wk_players = df_wk_players.set_index('player_key')
df_wk_points = pd.DataFrame(index = new_index)

# import dictionary of Yahoo Manager Names to Real Life Nicknames
with open('../teams/team_mapping_full.txt', 'r') as f:
    name_dict = dict(eval(f.read()))

##### LOOP THROUGH ALL WEEKS, TEAMS, AND PLAYERS #####
#for week in range(1, 2): # TEST
for week in range(1, rosters['num_weeks']+1): #16 weeks total
    df_wk_roster = pd.DataFrame(index = new_index)
    df_wk_points = pd.DataFrame(index = new_index)


    print('\nWeek %s: Team:' % week, end=" ")
    ##### START TEAM LOOP #####
    for team in range(1, rosters['num_teams']+1): #assuming 12 teams
        print(team, end=" ")
        tm_wk = 'team_'+str(team)+'_wk_' + str(week) + '_roster.json'
        path = '../rosters/week_'+str(week)+'/'
        file_name = path + tm_wk

        load_file = open(file_name) # load roster JSON from initial data scrape
        roster = json.load(load_file)
        load_file.close()

        df_team = pd.DataFrame(columns=columns, index = new_index) # create dataframe with specified column names
        #df_team = df_team.set_index('position')
        df_manager_team = pd.DataFrame(columns=['manager_name'], index = new_index)
        #df_manager_team = df_manager_team.set_index('position')
        df_players = pd.DataFrame(columns=['player_key'], index = new_index)
        df_points = pd.DataFrame(columns=['player_points'], index = new_index)

        team_number = int(roster['fantasy_content']['team'][0][1]['team_id'])
        manager_name = roster['fantasy_content']['team'][0][19]['managers'][0]['manager']['nickname']

        player_num = 0
        player_index = roster['fantasy_content']['team'][1]['roster']['0']['players'] # in case a manager does not have all 16 roster spots filled

        ##### START PLAYER LOOP #####
        
        player_list = []
        for player_num in range(0, len(player_index)-1): 
            player = roster['fantasy_content']['team'][1]['roster']['0']['players'][str(player_num)]
            player_key = player['player'][0][0]['player_key']
            player_list.append(player_key)
        # Join all player keys so they can all be called at the same time from the API
        all_players_string = ", ".join(player_list)
        
        url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/'+game_key+'.l.'+league_id+'/players;player_keys='+all_players_string+'/stats;type=week;week='+str(week)
        response = oauth.session.get(url, params={'format': 'json'})
        player_points_json = response.json()
        
        
        
        wr_count = 1
        rb_count = 1
        bn_count = 1
        for player_num in range(0, len(player_index)-1):
            player = roster['fantasy_content']['team'][1]['roster']['0']['players'][str(player_num)]
            first_name = player['player'][0][2]['name']['first']
            last_name = player['player'][0][2]['name']['last']
            full_name = player['player'][0][2]['name']['full']
            #team_abbr = player['player'][0][6]['editorial_team_abbr']
            roster_position = player['player'][1]['selected_position'][1]['position']
            player_key = player['player'][0][0]['player_key']
            player_id = player['player'][0][1]['player_id'] #STRING, not INT

            # Team abbreviations are not in the same location in each JSON file...
            try:
                team_abbr = player['player'][0][6]['editorial_team_abbr']
            except:
                pass
            try:
                team_abbr = player['player'][0][7]['editorial_team_abbr']
            except:
                pass
            try:
                team_abbr = player['player'][0][8]['editorial_team_abbr']
            except:
                pass
            
            # We already grabbed all the players points all at once before this for loop started. Now we can get each
            # players points without needing an API call each time. This equals SPEEEEED
            player_points = float(player_points_json['fantasy_content']['league'][1]['players'][str(player_num)]['player'][1]['player_points']['total'])

            # replace data in dataframe based on index of roster position
                # this needs to happen because the BN position is not consistant.
                # it can be out of order if there is more than 1 K or DEF or if
                # a player is  not started in a roster position

            player_full_stats = pd.Series({'first': first_name,
                                                'last': last_name,
                                                'full': full_name,
                                                'team': team_abbr,
                                                'manager_name': full_name, #This will be joined to weekly roster df
                                                'ros_pos': roster_position,
                                                'player_key': player_key,
                                                'player_id': player_id,
                                                'player_points': player_points
                                                           })

            if roster_position == 'QB':
                df_team.loc['QB'] = player_full_stats
                df_manager_team.loc['QB'] = pd.Series({'manager_name': full_name}) # contains managers name and the players full name
                df_points.loc['QB'] = pd.Series({'player_points': player_points})
                # Master list of players and Scores
                df_players.loc['QB'] = pd.Series({'player_key': player_key})

            elif roster_position == 'WR':
                wr_index = 'WR' + str(wr_count)
                wr_count += 1
                df_team.loc[wr_index] = player_full_stats
                df_manager_team.loc[wr_index] = pd.Series({'manager_name': full_name}) # contains managers name and the players full name
                df_points.loc[wr_index] = pd.Series({'player_points': player_points})
                # Master list of players and Scores
                df_players.loc[wr_index] = pd.Series({'player_key': player_key})

            elif roster_position == 'RB':
                rb_index = 'RB' + str(rb_count)
                rb_count += 1
                df_team.loc[rb_index] = player_full_stats
                df_manager_team.loc[rb_index] = pd.Series({'manager_name': full_name}) # contains managers name and the players full name
                df_points.loc[rb_index] = pd.Series({'player_points': player_points})
                # Master list of players and Scores
                df_players.loc[rb_index] = pd.Series({'player_key': player_key})

            elif roster_position == 'TE':
                df_team.loc['TE'] = player_full_stats
                df_manager_team.loc['TE'] = pd.Series({'manager_name': full_name}) # contains managers name and the players full name
                df_points.loc['TE'] = pd.Series({'player_points': player_points})
                # Master list of players and Scores
                df_players.loc['TE'] = pd.Series({'player_key': player_key})

            elif roster_position == 'W/R/T':
                df_team.loc['W/R/T'] = player_full_stats
                df_manager_team.loc['W/R/T'] = pd.Series({'manager_name': full_name}) # contains managers name and the players full name
                df_points.loc['W/R/T'] = pd.Series({'player_points': player_points})
                # Master list of players and Scores
                df_players.loc['W/R/T'] = pd.Series({'player_key': player_key})

            elif roster_position == 'K':
                df_team.loc['K'] = player_full_stats
                df_manager_team.loc['K'] = pd.Series({'manager_name': full_name}) # contains managers name and the players full name
                df_points.loc['K'] = pd.Series({'player_points': player_points})
                # Master list of players and Scores
                df_players.loc['K'] = pd.Series({'player_key': player_key})

            elif roster_position == 'DEF':
                df_team.loc['DEF'] = player_full_stats
                df_manager_team.loc['DEF'] = pd.Series({'manager_name': full_name}) # contains managers name and the players full name
                df_points.loc['DEF'] = pd.Series({'player_points': player_points})
                # Master list of players and Scores
                df_players.loc['DEF'] = pd.Series({'player_key': player_key})

            elif roster_position == 'BN':
                bn_index = 'BN' + str(bn_count)
                bn_count += 1
                df_team.loc[bn_index] = player_full_stats
                df_manager_team.loc[bn_index] = pd.Series({'manager_name': full_name}) # contains managers name and the players full name
                df_points.loc[bn_index] = pd.Series({'player_points': player_points})
                # Master list of players and Scores
                df_players.loc[bn_index] = pd.Series({'player_key': player_key})




            #### END PLAYER FOR LOOP ####
            #### CONTINUE TEAM LOOP  ####
        #df_wk_players = pd.concat([df_wk_players, df_players], axis=0) # add new players to running list of players

        df_manager_team.rename(columns = {'manager_name':manager_name}, inplace = True) #change name to match current manager name
        df_points.rename(columns = {'player_points': manager_name}, inplace = True)

        df_wk_roster = pd.concat([df_wk_roster, df_manager_team], axis=1) # join the full league weekly roster with managers name
        df_wk_points = pd.concat([df_wk_points, df_points], axis=1)
        team += 1
        #### END TEAM FOR LOOP  ####
        #### CONTINUE WEEK LOOP ####

    #print(df_wk_players.shape)
    #*************************************
    #***** CREATE WEEKLY LEAGUE ROSTER ***
    #*************************************

    wk_roster = 'wk_' + str(week) + '_roster.csv'
    path = './weekly_rosters/'
    file_name = path + wk_roster
    df_wk_roster.to_csv(file_name, sep=',', encoding='utf-8')

    wk_scores = 'wk_' + str(week) + '_scores.csv'
    path = './weekly_scores/'
    file_name = path + wk_scores
    df_wk_points.to_csv(file_name, sep=',', encoding='utf-8')

#len(df_wk_players['player_key'].unique())
print('\nFinished')
