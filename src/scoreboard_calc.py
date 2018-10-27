import requests
from ranking import Ranking, FRACTIONAL # RUN: pip3 install ranking


category_dict = {
    "0": "Points",
    "1": "Blocks",
    "2": "Steals",
    "3": "Assists",
    "6": "Rebounds",
    "17": "3 Pointers",
    "19": "FG Percentage",
    "20": "FT Percentage",
}
team_dict = {}


def get_espn_rankings():
    cookies = {
        'espn_s2': 'AEAhpegzkCC6fD8MN%2FiHxcLibIJkwvgf3Y2ncG%2BLh5jJ4rX6qJ3yb8c%2BGO7v1bu0G3dyikSTsROtjTn2%2Fy2zog4VCe9Vurm7ospcCSw0HjBiyTiJ1kwCZSrTRI%2BpNQwxz%2Fk%2F1L%2FXQif1r2IYngDrVFxyjvHqCj%2Fo64I9ZtZj%2F2%2BgqvdWcWWQAgkk17U7KNg%2FFQO25xn0WURomTtL4lEAlKBLLeOtnzUJzUhwSmyw0sHlii5os2%2B1AnXMx0uqtJyPTF0%3D',
        'swid': '332308E2-095B-41DB-B9A3-2FACFFC8DAFA',
    }
    headers = {
        'accept': 'application/json',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en-US,en;q=0.9',
        'connection': 'keep-alive',
        'cookie': 'espn_s2=AEAhpegzkCC6fD8MN%2FiHxcLibIJkwvgf3Y2ncG%2BLh5jJ4rX6qJ3yb8c%2BGO7v1bu0G3dyikSTsROtjTn2%2Fy2zog4VCe9Vurm7ospcCSw0HjBiyTiJ1kwCZSrTRI%2BpNQwxz%2Fk%2F1L%2FXQif1r2IYngDrVFxyjvHqCj%2Fo64I9ZtZj%2F2%2BgqvdWcWWQAgkk17U7KNg%2FFQO25xn0WURomTtL4lEAlKBLLeOtnzUJzUhwSmyw0sHlii5os2%2B1AnXMx0uqtJyPTF0%3D; swid=332308E2-095B-41DB-B9A3-2FACFFC8DAFA',
        'if-none-match': '"0a2da05e1a6aff012d38696d244f0b264"',
        'referer': 'http://fantasy.espn.com/basketball/league/scoreboard?leagueId=109275&matchupPeriodId=1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'x-fantasy-filter': '{"players":{}}',
        'x-fantasy-platform': 'kona-PROD-755f83fb384a6c15e1e599e9582054d00c1ec6b3',
        'x-fantasy-source': 'kona',
    }
    params = (
        ('view', ['mMatchupScore', 'mScoreboard', 'mSettings', 'mTeam', 'modular', 'mNav']),
    )
    response = requests.get('http://fantasy.espn.com/apis/v3/games/fba/seasons/2019/segments/0/leagues/109275', headers=headers, params=params, cookies=cookies)

    return response

def calculate_espn_rankings(current_week):
    response = get_espn_rankings()
    result = response.json()
    matchups = result["schedule"]

    teams = result["teams"]
    for team in teams:
        team_dict[team["id"]] = team["location"] + team["nickname"]

    print(f'Teams: {team_dict}')

    print(f'Calculating rankings for week: {current_week}')

    current_week_schedule = list(filter((lambda x: x["matchupPeriodId"] == current_week), matchups))

    team_scores = {}

    # Create dictionary of categories to player tuples ()
    weekly_score_dict = {}

    for matchup in current_week_schedule:
        away = matchup["away"]
        away_scores = away["cumulativeScore"]["scoreByStat"]
        away_team_id = away["teamId"]

        for stat_value, score_obj in away_scores.items():
            if score_obj["result"] is not None:

                if (stat_value == "19") or (stat_value == "20"):
                    formatted_score = round(score_obj["score"], 3)
                else:
                    formatted_score = score_obj["score"]

                if stat_value in weekly_score_dict:
                    weekly_score_dict[stat_value].append(tuple((away_team_id, formatted_score)))
                else:
                    score_tuple = tuple((away_team_id, formatted_score))
                    weekly_score_dict[stat_value] = [score_tuple]


        home = matchup["home"]
        home_scores = home["cumulativeScore"]["scoreByStat"]
        home_team_id = home["teamId"]

        for stat_value, score_obj in home_scores.items():
            if score_obj["result"] is not None:

                if (stat_value == "19") or (stat_value == "20"):
                    formatted_score = round(score_obj["score"], 3)
                else:
                    formatted_score = score_obj["score"]

                if stat_value in weekly_score_dict:
                    weekly_score_dict[stat_value].append(tuple((home_team_id, formatted_score)))
                else:
                    score_tuple = tuple((away_team_id, formatted_score))
                    weekly_score_dict[stat_value] = [score_tuple]


    # Sorting categories and iterating through categories with index to rank points
    for category, category_list in weekly_score_dict.items():
        category_name = category_dict[category]
        category_list.sort(key=lambda tup: tup[1], reverse=True)

        for index, category_tuple in Ranking(category_list, strategy=FRACTIONAL, key=lambda x: x[1]):
            team_rank = index + 1
            team_id = category_tuple[0]
            team_name = team_dict[team_id]
            team_category_value = category_tuple[1]
            # if team_name == "TeamBansal":
            #     rank_val = 11 - team_rank
            #     print(f"({rank_val}) {category_name} {team_category_value}")
            if team_name in team_scores:
                team_scores[team_name] = team_scores[team_name] + (11 - team_rank)
            else:
                team_scores[team_name] = (11 - team_rank)

    category_scores = print_all_category_scores(weekly_score_dict)
    sorted_total = print_all_sorted_totals(team_scores)

    return (sorted_total, category_scores)

def print_all_category_scores(weekly_score_dict):
    category_value_map = {}
    for category, category_list in weekly_score_dict.items():
        category_name = category_dict[category]

        category_string = f"<< {category_name} >>"
        for index, category_tuple in Ranking(category_list, strategy=FRACTIONAL, key=lambda x: x[1]):
            team_rank = index + 1
            team_id = category_tuple[0]
            team_name = team_dict[team_id]
            team_category_value = category_tuple[1]
            category_string += f' ({team_rank}) {team_name} {team_category_value} |'
        category_value_map[category_name] = category_string
        print(category_string)

    return category_value_map

def print_all_sorted_totals(team_scores):
    scores = [(k, v) for k, v in team_scores.items()]
    scores.sort(key=lambda tup: tup[1], reverse=True)
    total_score_string = f"| Total Scores:"
    for score in scores:
        team_name = score[0]
        total_score_value = score[1]
        total_score_string += f' {team_name} {total_score_value} |'
    print(total_score_string)

    return total_score_string
