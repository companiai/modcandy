import logging
import json
import ipdb
import time
import requests
from django.conf import settings
import pandas as pd
from equalizer.bad_word_matrix import BAD_WORD_JSON
from equalizer.models import BadWordShortForm, ChatMessage, Player, PerspectiveAnalysis, Session
from equalizer.serializers import ChatMessageSerializer

logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.INFO)


class EqualizerUtil:

    def __init__(self, debug) -> None:
        self.debug = debug
        self.profane_words_file = settings.PROFANE_WORD_CSV_FILE_LOCATION
        self.tox_analysis_endpoint = settings.BACKEND_DOMAIN + '/api/v1/tox-analysis/'


    def import_bad_word_csv(self):
        if self.debug:
            ipdb.set_trace()
        df = pd.read_csv(self.profane_words_file)
        df = df.fillna('')
        for _, row in df.iterrows():
            bad_word = BadWordShortForm.objects.update_or_create(
                text=row['text'],
                defaults={
                    'full_form':row['full_form'],
                    'real_form':row['real_form'],
                }
                
            )
            logger.info(bad_word)

    def import_from_json(self, reset=False):
        if self.debug:
            ipdb.set_trace()
        if reset:
            BadWordShortForm.objects.all().delete()
        data = {}
        with open(settings.BAD_WORD_JSON_FILE_LOCATION) as f:
            data = json.load(f)
        for key, value in data.items():
            bad_word = BadWordShortForm.objects.update_or_create(
                text=key,
                defaults={
                    'full_form':value,
                }
                
            )
            logger.info(bad_word)

    def dump_json_from_matrix(self):
        if self.debug:
            ipdb.set_trace()
        with open(settings.BAD_WORD_JSON_FILE_LOCATION, 'w') as f:
            json.dump(BAD_WORD_JSON, f)

    def dump_json_from_db(self):
        if self.debug:
            ipdb.set_trace()
        bad_word_json = {}
        for bad_word in BadWordShortForm.objects.all():
            bad_word_json[bad_word.text] = bad_word.full_form
        with open(settings.BAD_WORD_JSON_FILE_LOCATION, 'w') as f:
            json.dump(bad_word_json, f)
    
    def get_tox_analysis(self, userid, message, sessionid, username):
        if self.debug:
            ipdb.set_trace()

        payload = json.dumps({
            "text": message,
            "playerID": int(userid),
            "sessionID": int(sessionid),
            "playerName": username
        })
        headers = {
        'Content-Type': 'application/json'
        }
        
        response = requests.request("POST", self.tox_analysis_endpoint, headers=headers, data=payload)
        return response.json()
    
    def get_dataframe(self, test_file_location):
        if self.debug:
            ipdb.set_trace()
        df = pd.read_csv(test_file_location)
        
        df = df[[ 'UserID', 'Message', 'SessionID', 'User Name']]
        
        df['message_tox_score'] = 0
        
        df['flagged']=False
        
        df['perspective_flagged']=False
        df['perspective_toxicity']=0.0
        
        df['assigned_tox_score'] = 0
        df['latency'] = 0.0
        
        return df
    
    def run_test(self, test_file_location, export_file_location, sleeptime=1):
        errors = 0
        df = self.get_dataframe(test_file_location=test_file_location)
        for index, row in df.iterrows():
            start = time.time()
            data = self.get_tox_analysis(
                userid=row['UserID'], 
                message=row['Message'],
                sessionid=row['SessionID'],
                username=row['User Name']
            )
            if(data.get('error', None)):
                logger.error(data)
                errors +=1
            df.loc[index, 'message_tox_score'] = data.get('message_tox_score')
            df.loc[index, 'flagged'] = data.get('flagged')
            df.loc[index, 'perspective_flagged'] = data.get('perspective_flagged')
            df.loc[index, 'perspective_toxicity'] = data.get('perspective_toxicity')
            df.loc[index, 'assigned_tox_score'] = data.get('assigned_tox_score')
            end = time.time()
            df.loc[index, 'latency'] = end-start
            
            time.sleep(sleeptime)
            if index%100 == 0:
                logger.info(f"{index},{data.get('message_tox_score')}, {df.iloc[index]['Message']}")
        
        df.to_csv(export_file_location, index=False)
        return errors
    

    def reset_data(self):
        if self.debug:
            ipdb.set_trace()
        ChatMessage.objects.all().delete()
        PerspectiveAnalysis.objects.all().delete()
        Player.objects.all().delete()
        Session.objects.all().delete()


    def get_recent_messages(self, user):
        if self.debug:
            ipdb.set_trace()
        chat_messages = ChatMessage.objects.filter(user=user).order_by('-created')[:10]
        return ChatMessageSerializer(chat_messages, many=True).data
    




    

