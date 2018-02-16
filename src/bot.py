"""Bot to send messages over Slack."""
import os
import logging

from config import _credentials
from slackclient import SlackClient

logger = logging.getLogger(__name__)


class SlackBot:
    """Send messages via Slack."""

    def __init__(self, nest, network_analysis, channel):
        """Initialize SlackBot."""
        self._sc = SlackClient(_credentials['slack'])
        self._channel = channel
        self.upload_file(filepath='./data/sankey.png',
                         title='City Flows - Sankey Diagram',
                         text=f'```{nest.click_params} ```\n '
                              f'```{network_analysis.plot_url} ```\n ')

    def send_msg(self, txt):
        """Send Slack message."""
        res = self._sc.api_call(
            'chat.postMessage',
            channel=self._channel,
            username='Mr.bot',
            text=txt
        )
        if not res['ok']:
            logger.error(f"Send message failed: {res['error']}")
        else:
            logger.info("Message sent successfully")

    def upload_file(self, filepath, title, text):
        """Upload file to Slack."""
        with open(filepath, 'rb') as f:
            res = self._sc.api_call(
                'files.upload',
                channels=self._channel,
                title=title,
                filename=os.path.basename(filepath),
                username='Mr.bot',
                initial_comment=text,
                file=f
            )
            if 'ok' not in res or not res['ok']:
                logger.error(f"File upload failed: {res['error']}")
            else:
                logger.info(f"Uploaded {filepath}")