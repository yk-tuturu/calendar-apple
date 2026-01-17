from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle

# Calendar API scope: full access
SCOPES = ['https://www.googleapis.com/auth/calendar']

# OAuth flow
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

# Save token for later use
with open('token.pkl', 'wb') as token_file:
    pickle.dump(creds, token_file)