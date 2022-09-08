# League Settings
import os

LEAGUE_ID = os.environ.get('LEAGUE_ID')
ROSTER_LIMIT = 14  # insert roster limit from league settings
IR_ELIGIBLE = ['Out', 'PUP', 'IR', 'COV']

# Twilio Settings
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
PHONE_FROM = os.environ.get('PHONE_FROM')
PHONE_TO = os.environ.get('PHONE_TO')
