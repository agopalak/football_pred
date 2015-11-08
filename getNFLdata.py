__author__ = 'agopalak'

import nflgame
import csv
import getWeather
import stadium_info
import os.path
import json

# File Names
weatherJSON = 'gameweather.json'

# Years to process
years = [2010, 2011, 2012, 2013, 2014]

# Initializing Game Weather Dictionary
game_weather = {}
if os.path.exists(weatherJSON):
    with open(weatherJSON) as ifile:
        game_weather = json.load(ifile)
weather_lookedup = False

# For header initialization
startedProc = 0

f = open('nflData.csv', 'w+')

# Load data by year
for year in years:
    games = nflgame.games(year)

    # Create a dictionary of positions
    players = nflgame.combine_game_stats(games)
    position = {}
    for p in players:
        stats = [
            (p.passing_att, 'QB'),
            (p.rushing_att, 'RB'),
            (p.receiving_rec, 'WR'),
            (p.defense_tkl, 'DEF'),
            (p.defense_ast, 'DEF'),
            (p.kicking_fga, 'K'),
            (p.punting_yds, 'P'),
        ]
        position[p.playerid] = sorted(stats, reverse=True)[0][1]

    # Load data for each game
    for game in games:

        # Game Related Information
        gdate = str(game.schedule['month']) + '/' + str(game.schedule['day']) + '/' + str(game.schedule['year'])

        # All games are in the afternoon
        # OPEN: Handle exceptions with International Games
        gtime = game.schedule['time'] + ' PM'

        # Prepping Game Data
        gline = {
            'game_eid': game.eid,
            'game_week': game.schedule['week'],
            'game_wday': game.schedule['wday'],
            'game_date': gdate,
            'game_time': gtime,
            'home_team': game.home,
            'away_team': game.away,
            'score_home': game.score_home,
            'score_away': game.score_away,
            'home_stadium': stadium_info.teamStadium[game.home],
            'home_field': stadium_info.fieldType[game.home]
        }

        # Extract Weather Information
        print stadium_info.teamLocation[game.home], gdate, gtime
        if game.eid not in game_weather.keys():

            weather_lookedup = True

            # Calling weather subroutine
            game_weather[game.eid] = getWeather.fetchWeather(stadium_info.teamLocation[game.home], gdate, gtime)

            # Initializing Data if Absent
            if 'temperature' not in game_weather[game.eid].keys():
                game_weather[game.eid]['temperature'] = 0
            if 'windSpeed' not in game_weather[game.eid].keys():
                game_weather[game.eid]['windSpeed'] = 0
            if 'humidity' not in game_weather[game.eid].keys():
                game_weather[game.eid]['humidity'] = 0
            if 'apparentTemperature' not in game_weather[game.eid].keys():
                game_weather[game.eid]['apparentTemperature'] = game_weather[game.eid]['temperature']
            if 'summary' not in game_weather[game.eid].keys():
                game_weather[game.eid]['summary'] = 'None'
            print game_weather[game.eid]

        # Prepping Weather Data
        gline['game_temp'] = game_weather[game.eid]['temperature']
        gline['game_ftemp'] = game_weather[game.eid]['apparentTemperature']
        gline['game_weather'] = game_weather[game.eid]['summary']
        gline['game_wind'] = game_weather[game.eid]['windSpeed']
        gline['game_humid'] = game_weather[game.eid]['humidity']

        # Query player data per game
        plines = game.players.cummstats()

        # Header information
        hline = plines.pop(0)
        if startedProc == 0:
            # Dictionary Header Information
            fields = ['year', 'game_eid', 'game_week', 'game_wday', 'game_date', \
                      'game_time', 'home_team', 'away_team', 'score_home', 'score_away', \
                      'game_temp', 'game_ftemp', 'game_weather', 'game_wind', 'game_humid', \
                      'home_stadium', 'home_field'] \
                     + [key for key in hline]
            writer = csv.DictWriter(f, fields)
            writer.writeheader()
            startedProc = 1

        # Populating statline information
        # Includes Year, Game Information & Player Information
        for pline in plines:
            pline['pos'] = position[pline['id']]
            sline = {'year': year}
            sline.update(gline)
            sline.update(pline)
            writer.writerow(sline)

# Save JSON for weather information if new data accessed
# Avoid unnecessary pings forecastIO server
if weather_lookedup:
    with open(weatherJSON, 'w') as ofile:
        json.dump(game_weather, ofile)

f.close()
