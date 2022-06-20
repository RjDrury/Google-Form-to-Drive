import json
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import time

SCOPES = ['https://www.googleapis.com/auth/drive']

service_account_info = json.load(open('credentials.json'))#
creds=Credentials.from_service_account_info(
    service_account_info, scopes=SCOPES)

def getCurrentDateMinusOneHourInZuluTime():
    d = datetime.utcnow() - timedelta(hours=1) # <-- get time in UTC
    return d.isoformat("T") + "Z"

def getFormResponses():
    form_service = build('forms', 'v1', credentials=creds)
    q = 'timestamp >= ' + getCurrentDateMinusOneHourInZuluTime()
    form_responses = form_service.forms().responses().list(formId='1FJKYYeUNz4j6WxEOKW1Kaw85RW2DNQH3FINKryyPDKs',filter=q).execute()


    for form_response in form_responses['responses']:
        name = form_response['answers']['3d1352aa']['textAnswers']['answers'][0]['value']
        resume = form_response['answers']['311da79b']['fileUploadAnswers']['answers'][0]
        createFolderAndMoveFiles(name,resume)

def createFolderAndMoveFiles(userName, fileToMove):
    drive_service = build('drive', 'v3', credentials=creds)
    destination_folder_id = '15X8apI-3_POGrQKR3_rfwE7BpT2CiTQO'
    
    file_metadata = {
    'name' : userName,
    'parents' : [destination_folder_id],
    'mimeType' : 'application/vnd.google-apps.folder'
    }
    file = drive_service.files().create(body=file_metadata,
                                    fields='id').execute()
    id = file.get('id')
    test = drive_service.files().get(fileId=fileToMove['fileId'],fields='parents').execute()
    previous_parents = ",".join(test.get('parents'))
    drive_service.files().update(fileId=fileToMove['fileId'],addParents=id,removeParents=previous_parents).execute()


while True:
    getFormResponses()
    print('Uploaded a round of cvs')
    time.sleep(3600)