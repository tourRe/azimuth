import requests
import csv
import httplib2
import os

from requests.auth import HTTPBasicAuth
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

def csvToList(path):
    """
    Converts a .csv file to a List, each line containing a dictionnary

    Returns:
        Result, the resulting List of dictionnaries
    """
    reader = csv.reader(path, delimiter=',')
    result = []
    for dict in reader:
        result.append(dict)
    return result

def fetch_Angaza():
    """
    Fetches User and Accounts data on Angaza server

    Returns:
        a dictionary containing both tables as lists
    """

    #Credentials
    login = 'op=alex@azimuth-solar.com'
    pw = 'raw=Lapoudre2009'
    url1 = 'https://payg.angazadesign.com/api/snapshots/accounts'
    url2 = 'https://payg.angazadesign.com/api/snapshots/users'

    with requests.Session() as s:
         print('Downloading user data from ' + url2)
         download = s.get(url2, auth=(login,pw))
         decoded_content = download.content.decode('utf-8')
         users_raw = csvToList(decoded_content.splitlines())
         print('Downloading account data from ' + url1)
         download = s.get(url1, auth=(login,pw))
         decoded_content = download.content.decode('utf-8')
         accounts_raw = csvToList(decoded_content.splitlines())
    return {'accounts': accounts_raw, 'users': users_raw}

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://spreadsheets.google.com/feeds'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API'

def get_credentials():
    """
    Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
            'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)

    print('Storing credentials to ' + credential_path)
    return credentials

def main():
    #Spreadsheet credentials
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
            'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
            discoveryServiceUrl=discoveryUrl)
    spreadsheetId = '1CzgD3EnnNj9ZXSmPIUwppH7yjxe5CI5oLRCXZK2vw1M'

    #Fetching Angaza data
    data = fetch_Angaza()

    #Defining update requests
    
    request_body_users = {
          "valueInputOption": 'RAW',
          "data": [{
              "range": "agents!A1:AA500",
              "values": data['users']
              }],
          "includeValuesInResponse": False,
          "responseValueRenderOption": 'UNFORMATTED_VALUE',
          "responseDateTimeRenderOption": 'FORMATTED_STRING',
          }
    request_users = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheetId, 
            body=request_body_users)

    request_body_accounts = {
          "valueInputOption": 'RAW',
          "data": [{
              "range": "accounts!A1:BA5000",
              "values": data['accounts']
              }],
          "includeValuesInResponse": False,
          "responseValueRenderOption": 'UNFORMATTED_VALUE',
          "responseDateTimeRenderOption": 'FORMATTED_STRING',
          }
    request_accounts = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheetId, 
            body=request_body_accounts)

    response_users = request_users.execute()
    response_accounts = request_accounts.execute()

if __name__ == '__main__':
    main()
