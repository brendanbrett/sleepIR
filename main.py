import json
from datetime import datetime
from os.path import exists
from twilio.rest import Client
from sleeper_wrapper import League, Players

import config

LEAGUE_ID = config.LEAGUE_ID
ROSTER_LIMIT = config.ROSTER_LIMIT
IR_ELIGIBLE = config.IR_ELIGIBLE
FORCED_UPDATE = 0

if __name__ == '__main__':

    run_date = datetime.now().strftime('%Y-%m-%d')

    league = League(LEAGUE_ID)

    try:
        league_rosters = League.get_rosters(league)
        len(league_rosters)
    except TypeError:
        print('No response from API')
        exit(1)

    users = League.get_users(league)

    # Get current players
    # File is saved to disk to avoid hitting API rate limit
    if not exists(f'./data/{run_date}_all_players.json') or FORCED_UPDATE:
        print(f'Players file for {run_date} does not exist. Fetching from API...')
        players = Players()
        all_players = players.get_all_players()
        with open(f'./data/{run_date}_all_players.json', 'w') as outfile:
            json.dump(all_players, outfile)

    with open(f'./data/{run_date}_all_players.json', 'r') as infile:
        print(f'Loading players file for {run_date}...')
        all_players = json.load(infile)

    # Map player data from all_players to league players
    for roster in league_rosters:
        roster['players'] = [all_players[player_id] for player_id in roster['players']]
        roster['ir'] = [player for player in roster['players'] if player['injury_status'] in IR_ELIGIBLE]
        roster['active'] = [player for player in roster['players'] if player['injury_status'] not in IR_ELIGIBLE]
        roster['active_count'] = len(roster['active'])
        roster['ir_count'] = len(roster['ir'])
        roster['total_count'] = roster['active_count'] + roster['ir_count']
        roster['user'] = [user for user in users if user['user_id'] == roster['owner_id']][0]
        roster['over_limit'] = 'Yes' if ((roster['total_count'] - roster['ir_count']) > ROSTER_LIMIT) else 'No'

    # Sort rosters by IR count
    league_rosters.sort(key=lambda x: x['ir_count'], reverse=True)
    # Print a header line with user display_name, active count, IR count, total count, and IR eligible players
    print(f'{"User":<20} {"Active":<7} {"IR":<7} {"Total":<7} {"Violation":<10} {"IR Eligible":<50} ')
    for roster in league_rosters:
        print(
            f'{roster["user"]["display_name"]:<20} {roster["active_count"]:<7} {roster["ir_count"]:<7} {roster["total_count"]:<7} {roster["over_limit"]:<10} {", ".join([player["full_name"] for player in roster["ir"]]):<50} ')

    if config.TWILIO_ACCOUNT_SID and config.TWILIO_AUTH_TOKEN and config.PHONE_FROM and config.PHONE_TO:
        # Identify any teams with a violation and send a text via Twilio
        violation_rosters = [roster for roster in league_rosters if roster['over_limit'] == 'Yes']
        if violation_rosters:
            print('Sending violation notification...')
            violation_users = [roster['user']['display_name'] for roster in violation_rosters]
            client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f'Roster violations found for the following teams: {", ".join(violation_users)}',
                from_=config.PHONE_FROM,
                to=config.PHONE_TO
            )
            print(message.sid)
