from basketball_reference_web_scraper import client
from basketball_reference_web_scraper.data import OutputType

import requests
from lxml import html

from bs4 import BeautifulSoup
from bs4 import Comment

from datetime import timedelta
import csv

shortnames = {
    'Atlanta Hawks': 'ATL',
    'Brooklyn Nets': 'BRK',
    'Boston Celtics': 'BOS',
    'Charlotte Hornets': 'CHO',
    'Chicago Bulls': 'CHI',
    'Cleveland Cavaliers': 'CLE',
    'Dallas Mavericks': 'DAL',
    'Denver Nuggets': 'DEN',
    'Detroit Pistons': 'DET',
    'Golden State Warriors': 'GSW',
    'Houston Rockets': 'HOU',
    'Indiana Pacers': 'IND',
    'Los Angeles Clippers': 'LAC',
    'Los Angeles Lakers': 'LAL',
    'Memphis Grizzlies': 'MEM',
    'Miami Heat': 'MIA',
    'Milwaukee Bucks': 'MIL',
    'Minnesota Timberwolves': 'MIN',
    'New Orleans Pelicans': 'NOP',
    'New York Knicks': 'NYK',
    'Oklahoma City Thunder': 'OKC',
    'Orlando Magic': 'ORL',
    'Philadelphia 76ers': 'PHI',
    'Phoenix Suns': 'PHO',
    'Portland Trail Blazers': 'POR',
    'Sacramento Kings': 'SAC',
    'San Antonio Spurs': 'SAS',
    'Toronto Raptors': 'TOR',
    'Utah Jazz': 'UTA',
    'Washington Wizards': 'WAS',
    'New Orleans Hornets': 'NOH',
    'Charlotte Bobcats': 'CHA',
    'Seattle SuperSonics': 'SEA',
    'Vancouver Grizzlies': 'VAN',
    'New Jersey Nets': 'NJN',
    'New Orleans/Oklahoma City Hornets': 'NOK'
}

memoized_average_box_scores = {}


def team_average_box_scores(team, season):
    if team in memoized_average_box_scores:
        return memoized_average_box_scores[team]
    url = "https://www.basketball-reference.com/teams/" + team + "/" + str(season) + ".html"
    team_req = requests.get(url)
    team_soup = BeautifulSoup(team_req.content, "html.pa      rser")
    # Cute hack because the page stores the table in an HTML comment.
    team_comments = team_soup.find_all(string=lambda text: isinstance(text, Comment))
    for item in team_comments:
        if "Team and Opponent Stats" in item:
            comment = BeautifulSoup(item, "html.parser")
            table_row = comment.find("table", id="team_and_opponent").find_all("tr")[2].find_all("td")[2:]
            stats = [float(td.text) for td in table_row]
            memoized_average_box_scores[team] = stats
            return stats


def format_date_for_url(year, month, day):
    new_year = str(year)
    new_month = str(month)
    new_day = str(day)
    if month <= 9:
        new_month = '0' + new_month
    if day <= 9:
        new_day = '0' + new_day
    return new_year, new_month, new_day


def main():
    # Start by including the headers.
    examples = [
        ['outcome', 'team0_sn_fg', 'team0_sn_fga', 'team0_sn_fgp', 'team0_sn_3pfg', 'team0_sn_3pfga', 'team0_sn_fg_3pfgp',
         'team0_sn_2pfg', 'team0_sn_2pfga', 'team0_sn_2pfgp', 'team0_sn_ft', 'team0_sn_fta', 'team0_sn_ftp', 'team0_sn_orb',
         'team0_sn_drb', 'team0_sn_trb', 'team0_sn_ast', 'team0_sn_stl', 'team0_sn_blk', 'team0_sn_tov', 'team0_sn_pf', 'team0_sn_pts',
         'team1_sn_fg', 'team1_sn_fga', 'team1_sn_fgp', 'team1_sn_3pfg', 'team1_sn_3pfga', 'team1_sn_fg_3pfgp',
         'team1_sn_2pfg', 'team1_sn_2pfa', 'team1_sn_2pfgp', 'team1_sn_ft', 'team1_sn_fta', 'team1_sn_ftp', 'team1_sn_orb',
         'team1_sn_drb', 'team1_sn_trb', 'team1_sn_ast', 'team1_sn_stl', 'team1_sn_blk', 'team1_sn_tov', 'team1_sn_pf', 'team1_sn_pts',
         'team0_matchup_fg', 'team0_matchup_fga', 'team0_matchup_fgp', 'team0_matchup_3pfg', 'team0_matchup_3pfga', 'team0_matchup_fg_3pfgp',
         'team0_matchup_ft', 'team0_matchup_fta', 'team0_matchup_ftp', 'team0_matchup_orb', 'team0_matchup_drb',
         'team0_matchup_trb', 'team0_matchup_ast', 'team0_matchup_stl', 'team0_matchup_blk', 'team0_matchup_tov', 'team0_matchup_pf', 'team0_matchup_pts',
         'team1_matchup_fg', 'team1_matchup_fga', 'team1_matchup_fgp', 'team1_matchup_3pfg', 'team1_matchup_3pfga', 'team1_matchup_fg_3pfgp',
         'team1_matchup_ft', 'team1_matchup_fta', 'team1_matchup_ftp', 'team1_matchup_orb', 'team1_matchup_drb',
         'team1_matchup_trb', 'team1_matchup_ast', 'team1_matchup_stl', 'team1_matchup_blk', 'team1_matchup_tov',
         'team1_matchup_pf', 'team1_matchup_pts'
         ]
    ]

    for season in range(1998, 2020):  # The 1997-2000 season until the 2017-2018 season.
        season_schedule = client.season_schedule(season_end_year=season)
        url = 'https://www.basketball-reference.com/playoffs/NBA_' + str(season) + '.html'
        playoff_outcomes = requests.get(url)
        data = list(html.fromstring(playoff_outcomes.content)
                    .xpath('//table[@id="all_playoffs"]'
                           '/tbody'
                           '/tr[not(contains(@class, "thead") or contains(@class, "toggleable"))]'
                           '/td/a/text()')
                    )
        data = [d for d in data if d != 'Series Stats']
        it = iter(data)
        data = list(zip(it, it))
        teams_appearing_in_playoffs = list(set([series[0] for series in data] + [series[1] for series in data]))
        print(teams_appearing_in_playoffs)
        # Get the winning team's season average box scores
        for series in data:
            if series[0] not in shortnames or series[1] not in shortnames or series[0] == 'Charlotte Hornets' or series[1] == 'Charlotte Hornets':
                continue
            print("Parsing series: " + str(series))
            team1_averages = team_average_box_scores(shortnames[series[0]], season)
            team2_averages = team_average_box_scores(shortnames[series[1]], season)
            team1_season_matchup_averages = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            team2_season_matchup_averages = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            games_played = 0

            for game in season_schedule:
                if game['home_team'].value.lower() == series[0].lower() and game['away_team'].value.lower() == series[1].lower():
                    date = game['start_time']
                    url_date = format_date_for_url(date.date().year, date.date().month, date.date().day)
                    url = 'https://www.basketball-reference.com/boxscores/' + url_date[0] + url_date[1] + url_date[2] + '0' + shortnames[series[0]] + '.html'
                    match = requests.get(url)
                    game_soup = BeautifulSoup(match.content, "html.parser")
                    if match.status_code == 404 or series[1] + " at " + series[0] not in game_soup.find("div", id="content").find("h1").text:
                        date -= timedelta(1)
                        url_date = format_date_for_url(date.date().year, date.date().month, date.date().day)
                        url = 'https://www.basketball-reference.com/boxscores/' + url_date[0] + url_date[1] + url_date[2] + '0' + shortnames[series[0]] + '.html'
                        match = requests.get(url)
                        game_soup = BeautifulSoup(match.content, "html.parser")
                        if match.status_code == 404 or series[1] + " at " + series[0] not in game_soup.find("div", id="content").find("h1").text:
                            continue
                    game_soup = BeautifulSoup(match.content, "html.parser")
                    home_team_score_elements = game_soup.find("table", id="box-" + shortnames[series[0]] + "-game-basic")\
                        .find("tfoot").find_all("td")[1:-1]
                    home_team_scores = [td.text for td in home_team_score_elements]
                    away_team_score_elements = game_soup.find("table", id="box-" + shortnames[series[1]] + "-game-basic")\
                        .find("tfoot").find_all("td")[1:-1]
                    away_team_scores = [td.text for td in away_team_score_elements]
                    for i in range(18):
                        team1_season_matchup_averages[i] += float(home_team_scores[i])
                        team2_season_matchup_averages[i] += float(away_team_scores[i])
                    games_played += 1
                    print(home_team_scores)
                    print(away_team_scores)
                elif game['home_team'].value.lower() == series[1].lower() and game['away_team'].value.lower() == series[0].lower():
                    date = game['start_time']
                    url_date = format_date_for_url(date.date().year, date.date().month, date.date().day)
                    url = 'https://www.basketball-reference.com/boxscores/' + str(date.date().year) + url_date[0] + url_date[1] + url_date[2] + '0' + shortnames[series[1]] + '.html'
                    match = requests.get(url)
                    game_soup = BeautifulSoup(match.content, "html.parser")
                    if match.status_code == 404 or series[0] + " at " + series[1] not in game_soup.find("div", id="content").find("h1").text:
                        date -= timedelta(1)
                        url_date = format_date_for_url(date.date().year, date.date().month, date.date().day)
                        url = 'https://www.basketball-reference.com/boxscores/' + url_date[0] + url_date[1] + url_date[2] + '0' + shortnames[series[1]] + '.html'
                        match = requests.get(url)
                        game_soup = BeautifulSoup(match.content, "html.parser")
                        if match.status_code == 404 or series[0] + " at " + series[1] not in game_soup.find("div", id="content").find("h1").text:
                            continue
                    game_soup = BeautifulSoup(match.content, "html.parser")
                    home_team_score_elements = game_soup.find("table",
                                                              id="box-" + shortnames[series[1]] + "-game-basic") \
                                                   .find("tfoot").find_all("td")[1:-1]
                    home_team_scores = [td.text for td in home_team_score_elements]
                    away_team_score_elements = game_soup.find("table",
                                                              id="box-" + shortnames[series[0]] + "-game-basic") \
                                                   .find("tfoot").find_all("td")[1:-1]
                    away_team_scores = [td.text for td in away_team_score_elements]
                    for i in range(18):
                        team1_season_matchup_averages[i] += float(away_team_scores[i])
                        team2_season_matchup_averages[i] += float(home_team_scores[i])
                    games_played += 1
                else:
                    continue
            # Compute averages
            team1_season_matchup_averages = [stat / games_played for stat in team1_season_matchup_averages]
            team2_season_matchup_averages = [stat / games_played for stat in team2_season_matchup_averages]
            data_point1 = [0] + team1_averages + team2_averages + team1_season_matchup_averages + team2_season_matchup_averages
            data_point2 = [1] + team2_averages + team1_averages + team2_season_matchup_averages + team1_season_matchup_averages
            examples.append(data_point1)
            examples.append(data_point2)
    # Store examples in CSV.
    with open("training_examples_1997-2019.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(examples)


main()
