import logging
import requests

from django.conf import settings
logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.INFO)

def send_slack_notification(message):
    logger.info('Sending Slack Notification')
    response = requests.post(
        settings.BACKEND_NOTIFICATION_SLACK_CHANNEL,
        json={
            "text": message
        }
    )
    logger.info(response.text)
    return response.text

    