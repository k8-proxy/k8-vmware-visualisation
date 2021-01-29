import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# Include this path if working in Google Colab
#d = '/content/gdrive/My Drive/k8-vmware/'
# If not
d = ''


sheet_scopes = ['https://www.googleapis.com/auth/spreadsheets']
drive_scopes = ['https://www.googleapis.com/auth/drive']
slide_scope = ['https://www.googleapis.com/auth/presentations']


SCOPES = sheet_scopes + drive_scopes + slide_scope

def check_credentials(SCOPES=SCOPES, path='modules/credentials.json'):
	"""
	Check credentials, if none, request access.

	:param SCOPES: scopes
	:param path: path to client secret credentials
	:return: credentials
	"""
	creds = None
	if os.path.exists(d + 'token.pickle'):
		with open(d + 'token.pickle', 'rb') as token:
			creds = pickle.load(token)
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				d + path, SCOPES)
			creds = flow.run_local_server(port=0)
		with open(d + 'token.pickle', 'wb') as token:
			pickle.dump(creds, token)
	return creds

