import logging
import ipdb
import json
import requests
from decimal import Decimal
from django.conf import settings
import re
from emoji import demojize, emoji_list, emojize
from equalizer.models import Session, Player, PerspectiveAnalysis, ChatMessage, FlaggedMessage
from equalizer.bad_word_matrix import USER_COLOR_MATRIX, EMOJI_BLACK_LIST
from equalizer.weight_matrix import LOW_WEIGHT_THRESHOLD, HIGH_WEIGHTS, LOWER_WEIGHTS, ATTRIBUTE_LIST, PLAYER_SCORE_FACTOR, \
     TOX_FLAG_THRESHOLD, PLAYER_TOX_MULTIPLIER, PLAYER_MAX_TOX_MULTIPLIER, SPECIAL_CHARACTER_WEIGHT_MULTIPLIER, REPETITION_WEIGHT_MULTIPLIER, \
     REDUCE_PLAYER_TOX_MULTIPLIER, FOUL_PLAY_MAX_MULTIPLIER, MAX_TOX_SCORE_MESSAGE, TOX_FLAG_HIGH_THRESHOLD


logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.INFO)

class PerspectiveUtil:

    def __init__(self, debug) -> None:
        self.debug = debug

    @staticmethod
    def get_perspective_raw(text, api_key):
        url = f"https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={api_key}"
    
        payload = json.dumps({
        "comment": {
            "text": text
        },
        "languages": [
            "en"
        ],
        "requestedAttributes": {
            'TOXICITY':{},
            'SEVERE_TOXICITY':{}, 
            'IDENTITY_ATTACK':{}, 
            'INSULT':{}, 
            'PROFANITY':{},
            'UNSUBSTANTIAL':{}, 
            'THREAT':{},
            'SEXUALLY_EXPLICIT': {},
        }
        })
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, data=payload)
        response_data = response.json()
        return response_data
    
    # Black List and While List related settings

    def read_json(self, filelocation):
        with open(filelocation) as f:
            return json.load(f)
    
    def transform_text(self, text):
        if self.debug:
            ipdb.set_trace()

        # De-Emojise
        emoji_in_text = emoji_list(text)
        text = demojize(text)
        
        for emoji in emoji_in_text:
            emoji_text = demojize(emoji['emoji'])
            if EMOJI_BLACK_LIST.get(emoji_text, None):
                text = text.replace(emoji_text, EMOJI_BLACK_LIST.get(emoji_text))

        words = text.lower().split(' ')
        bad_words_dict = self.read_json(settings.BAD_WORD_JSON_FILE_LOCATION)
        white_list_dict = self.read_json(settings.WHITE_LIST_JSON_FILE_LOCATION)
        
        for i,w in enumerate(words):
            if w.strip() in USER_COLOR_MATRIX:
                words[i] = USER_COLOR_MATRIX[w.strip()]
            if w.strip() in bad_words_dict:
                words[i] = bad_words_dict[w.strip()]
            if w.strip() in white_list_dict:
                words[i] = white_list_dict[w.strip()]
        

        return ' '.join(words)
    
    def foul_play_score(self, text):
        if self.debug:
            ipdb.set_trace()
        score = 1
        words = text.lower().split(' ')
        # pattern = '[^,.a-zA-Z]+'
        # pattern = r"\b\w*[^'\w\s]\w*\b"
        pattern = r"\b\w*[a-zA-Z][^a-zA-Z\s'’]+[a-zA-Z]*\w*\b"
        regexp = re.compile(pattern)
        for w in words:
            if regexp.search(w.strip()):
                if emojize(w) == w:
                    score = score * SPECIAL_CHARACTER_WEIGHT_MULTIPLIER
                    break

        # repeated letters or numbers
        pattern = r'\b\w*([a-zA-Z])\1{2,}\w*\b'
        regexp = re.compile(pattern)
        for w in words:
            if regexp.search(w.strip()):
                if emojize(w) == w:
                    score = score * REPETITION_WEIGHT_MULTIPLIER
                    break

        return min(score, FOUL_PLAY_MAX_MULTIPLIER)

    def summarize_score(self, data):
        if self.debug:
            ipdb.set_trace()
        attribute_list = ATTRIBUTE_LIST
        result_data = {}
        for item in attribute_list:
            result_data[item] = data['attributeScores'][item]['summaryScore']['value']
            # logger.info(f"{item}: {result_data[item]}")
        return result_data
    
    def weighted_tox_score(self, data):
        if self.debug:
            ipdb.set_trace()
        weights = HIGH_WEIGHTS
        if data['SEVERE_TOXICITY']< LOW_WEIGHT_THRESHOLD:
            weights = LOWER_WEIGHTS
       
        attribute_list = ATTRIBUTE_LIST
        weighted_score = 0
        for item in attribute_list:
            weighted_score += weights[item] * data[item]
        weighted_score = int(weighted_score*140)
        # logger.info(min(weighted_score, 100))
        return min(weighted_score, 100)
    

    def calculate_tox_score(self, perspective_raw, foul_play_weight=1 ):
        if self.debug:
            ipdb.set_trace()

        # summarize perspective data -- debug --remove later
        summarized_data = self.summarize_score(data=perspective_raw)

        # get weighted tox_score
        tox_score = self.weighted_tox_score(data=summarized_data) * foul_play_weight
        

        return min(tox_score, MAX_TOX_SCORE_MESSAGE), summarized_data
    
        # return 80, {"SEVERE_TOXICITY": 0.16960317, "TOXICITY": 0.509388, "THREAT": 0.44942492, "INSULT": 0.31740165, "PROFANITY": 0.26735115, "IDENTITY_ATTACK": 0.047190998, "SEXUALLY_EXPLICIT": 0.35285118}
    
    def get_toxicity_type(self, data):
        data.pop('TOXICITY')
        data.pop('SEVERE_TOXICITY')
        max_key = max(data, key=data.get)
        return max_key

    def player_tox_score(self, sessionId, playerId, playerName, text, user, debug_mode=False):
        if self.debug:
            ipdb.set_trace()
        perspective_raw = None
        try:
            session, _ = Session.objects.get_or_create(user=user, sessionId=sessionId)
            player, _ = Player.objects.update_or_create(
                user=user,
                playerId=playerId,
                defaults={
                    'playerName': playerName
                }
            )
            # filter word list
            transformed_text = self.transform_text(text)
            
            # Fetch Perspective Response
            perspective_raw = self.get_perspective_raw(text=transformed_text, api_key=settings.PERSPECTIVE_API_KEY)
            foul_play_weight = self.foul_play_score(text=transformed_text)
            tox_score, perspective_data = self.calculate_tox_score(perspective_raw=perspective_raw, foul_play_weight=foul_play_weight)
            assigned_tox_score = min(tox_score * player.tox_weight , MAX_TOX_SCORE_MESSAGE) 
            if (tox_score > TOX_FLAG_THRESHOLD):
                # update player tox score and tox weight if message is toxic
                player_tox_score = int(((tox_score * PLAYER_SCORE_FACTOR) + player.player_tox_score) * Decimal(0.5) * player.tox_weight)
                player.player_tox_score = player_tox_score
                player.tox_weight = min(player.tox_weight * PLAYER_TOX_MULTIPLIER, PLAYER_MAX_TOX_MULTIPLIER)

                # update session toxicity if message is toxic
                session.session_tox_score = int((session.session_tox_score + tox_score) * Decimal(0.5) *  player.tox_weight)
                session.save()
            else:
                # reduce player tox weight if message is not toxic
                player.tox_weight = (player.tox_weight/ REDUCE_PLAYER_TOX_MULTIPLIER) if (player.tox_weight/ REDUCE_PLAYER_TOX_MULTIPLIER) > 1.0 else 1.0
                assigned_tox_score = tox_score * player.tox_weight
            player.save()
            
            chat_message = ChatMessage.objects.create(
                user=user,
                player=player,
                session=session,
                message=text,
                tox_score=tox_score,
                assigned_tox_score=assigned_tox_score,
                flagged=assigned_tox_score > TOX_FLAG_THRESHOLD
            )

            # optional I guess
            PerspectiveAnalysis.objects.create(
                chat_message=chat_message,
                raw_data = json.dumps(perspective_data),
            )

            # create Incident if Flagged
            if chat_message.flagged:

                FlaggedMessage.objects.create(
                    user=user,
                    chat_message=chat_message,
                    playerName=player.playerName,
                    session=session,
                    sessionId=sessionId,
                    tox_type=self.get_toxicity_type(data=perspective_data),
                    severity='HIGH' if chat_message.assigned_tox_score > TOX_FLAG_HIGH_THRESHOLD else 'LOW'
                )

            if debug_mode:
                return {
                    'flagged': chat_message.assigned_tox_score > TOX_FLAG_THRESHOLD,
                    'message_tox_score': chat_message.tox_score,
                    'assigned_tox_score': int(chat_message.assigned_tox_score),
                    'player_tox_score': player.player_tox_score,
                    'session_tox_score': session.session_tox_score,
                    'perspective_toxicity': perspective_data.get('TOXICITY'),
                    'perspective_flagged': perspective_data.get('TOXICITY') > 0.8
                }, False
            
            
            return {
                    'flagged': chat_message.assigned_tox_score > TOX_FLAG_THRESHOLD,
                    'pro_tox_score': int(chat_message.assigned_tox_score),
                    'player_tox_score': player.player_tox_score if player.player_tox_score < 1000 else 1000,
                    'session_tox_score': session.session_tox_score if session.session_tox_score < 1000 else 1000,
                }, False
        except Exception as e:
            logger.error(e)
            if debug_mode:
                return {
                    'error': str(e),
                    'perspecitive_raw': perspective_raw
                }, True
            return {
                'error': 'Unknown Error',
            }, True
            
    def simple_tox_score(self, text, user, debug_mode=False):
        if self.debug:
            ipdb.set_trace()
        perspective_raw = None
        try:
            # filter word list
            transformed_text = self.transform_text(text)
            
            # Fetch Perspective Response
            perspective_raw = self.get_perspective_raw(text=transformed_text, api_key=settings.PERSPECTIVE_API_KEY)
            foul_play_weight = self.foul_play_score(text=transformed_text)
            tox_score, _ = self.calculate_tox_score(perspective_raw=perspective_raw, foul_play_weight=foul_play_weight)
            
            
            ChatMessage.objects.create(
                user=user,
                message=text,
                tox_score=tox_score,
                flagged=tox_score > TOX_FLAG_THRESHOLD
            )

            return {
                'flagged': tox_score > TOX_FLAG_THRESHOLD,
                'message_tox_score': tox_score,
            }, False
        except Exception as e:
            logger.error(e)
            if debug_mode:
                return {
                    'error': str(e),
                    'perspecitive_raw': perspective_raw
                }, True
            return {
                'error': 'Unknown Error Occured'
            }, True
        
    
