from decimal import Decimal
LOWER_WEIGHTS = {
                "SEVERE_TOXICITY": 0.3,
                "TOXICITY": 0.15,
                "THREAT": 0.2,
                "INSULT": 0.25,
                "PROFANITY": 0.15,
                "IDENTITY_ATTACK": 0.15,
                "SEXUALLY_EXPLICIT": 0.15,
            }

HIGH_WEIGHTS = {
                "SEVERE_TOXICITY": 0.3,
                "TOXICITY": 0.15,
                "THREAT": 0.2,
                "INSULT": 0.4,
                "PROFANITY": 0.3,
                "IDENTITY_ATTACK": 0.15,
                "SEXUALLY_EXPLICIT": 0.3,
            }

LOW_WEIGHT_THRESHOLD = 0.3

ATTRIBUTE_LIST = [
    'SEVERE_TOXICITY',
    'TOXICITY',
    'THREAT',
    'INSULT',
    'PROFANITY',
    'IDENTITY_ATTACK',
    'SEXUALLY_EXPLICIT',
]

TOX_FLAG_THRESHOLD = 50
PLAYER_SCORE_FACTOR = Decimal(2.5)
PLAYER_TOX_MULTIPLIER = Decimal(1.1)
PLAYER_MAX_TOX_MULTIPLIER = Decimal(1.5)
SPECIAL_CHARACTER_WEIGHT_MULTIPLIER = 6
REPETITION_WEIGHT_MULTIPLIER = 2
FOUL_PLAY_MAX_MULTIPLIER = 10
REDUCE_PLAYER_TOX_MULTIPLIER = Decimal(1.1)
MAX_TOX_SCORE_MESSAGE = 100