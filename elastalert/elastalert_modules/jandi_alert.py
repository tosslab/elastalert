import json
import requests
from requests.exceptions import RequestException
from alerts import Alerter
from util import EAException
from util import elastalert_logger


class JandiAlerter(Alerter):
    """ Creates a JANDI room message for each alert """
    required_options = frozenset(['jandi_webhook_url'])

    def __init__(self, rule):
        super(JandiAlerter, self).__init__(rule)
        self.jandi_webhook_url = self.rule['jandi_webhook_url']
        self.jandi_connect_color = self.rule.get('jandi_connect_color', '#D23F31')

    def format_body(self, body):
        body = body.encode('UTF-8')
        body = body.replace('&', '&amp;')
        body = body.replace('<', '&lt;')
        body = body.replace('>', '&gt;')
        return body

    def alert(self, matches):
        title = u'⚠ %s ⚠ ' % (self.create_title(matches))
        body = self.create_alert_body(matches)
        body = self.format_body(body)
        # post to jandi
        headers = {'content-type': 'application/json', 'accept': 'application/vnd.tosslab.jandi-v2+json'}
        payload = {
            'body': title,
            'connectColor': self.jandi_connect_color,
            'connectInfo': [
                {
                    'description': body
                }
            ]
        }

        try:
            response = requests.post(self.jandi_webhook_url, data=json.dumps(payload), headers=headers)
            response.raise_for_status()
        except RequestException as e:
            raise EAException("Error posting to jandi: %s" % e)
        elastalert_logger.info("Alert sent to Jandi")

    def get_info(self):
        return {'type': 'jandi',
                'jandi_webhook_url': self.jandi_webhook_url}