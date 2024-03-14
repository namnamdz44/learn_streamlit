from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import random as rd
import subprocess
import re
import requests
import json
import random

INPUT_RANGE_NAME = "input!A1:C"
OUTPUT_RANGE_NAME = "output!A1:F"
url = ""

PRJ_DIR = os.path.dirname(os.path.abspath(__file__))
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "1jZQTDzeWXk5r7W4Zsguu5dWmoGoKPEIbT_tDgJxo_kc"


def sheet_setup():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(os.path.join(PRJ_DIR,"google_sheet_auth" ,"token.json")):
        creds = Credentials.from_authorized_user_file(os.path.join(PRJ_DIR,"google_sheet_auth" ,"token.json"), SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(PRJ_DIR,"google_sheet_auth" ,"credential.json"), SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(os.path.join(PRJ_DIR,"google_sheet_auth" ,"token.json"), "w") as token:
            token.write(creds.to_json())
    return creds

def sheet_read(creds, SPREADSHEET_ID, RANGE_NAME):
    try:
        service = build("sheets", "v4", credentials=creds)
        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME)
            .execute()
        )
        values = result.get("values", [])
        return values
    except HttpError as e:
        print(f"An error occurred: {e}")
        return None
    
def sheet_write(creds, SPREADSHEET_ID, RANGE_NAME, data):
    try:
        service = build("sheets", "v4", credentials=creds)
        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .update(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME, valueInputOption="RAW", body={"values":data})
            .execute()
        )
        return result
    except HttpError as e:
        print(f"An error occurred: {e}")
        return None
    
def sheet_append(creds, SPREADSHEET_ID, RANGE_NAME, data):
    try:
        service = build("sheets", "v4", credentials=creds)
        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .append(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME, valueInputOption="RAW", body={"values":data})
            .execute()
        )
        return result
    except HttpError as e:
        print(f"An error occurred: {e}")
        return None
    
def update_input_data(data, range):
    sheet_write(sheet_setup(), SPREADSHEET_ID, range, [["id","question"]]+data.values.tolist())
def update_output_data(data, range):
    sheet_append(sheet_setup(), SPREADSHEET_ID, range, data.values.tolist())
    
def get_and_save_data(input_range_name, output_dir):
    if os.path.exists(output_dir):
        data = pd.read_csv(output_dir, header=0)
    else:
        raw_data = sheet_read(sheet_setup(), SPREADSHEET_ID, input_range_name)
        data = pd.DataFrame(raw_data[1:], columns=raw_data[0])
        data.to_csv(output_dir, index=False) 
    return data

def get_question(table: pd.DataFrame, index):
    if len(table[table["id"] == index]["question"].values) > 0:
        return table[table["id"] == index]["question"].values[0]
    raise Exception("Index not found")

def preprocess(result):
    pattern = "\[(.*?)\]"
    try:
        return list(eval(list(re.findall(pattern,result))[-1]))
    except Exception as e:
        return ["Xảy ra lỗi khi xử lý data: " + result]

def get_context(question, type="hybrid", field=True, similarity=0.2, top=10, top_rerank=5):
    return 

def get_answer(question, context, model, nums=7, temperature=0.7, path=""):
    return 
                   
