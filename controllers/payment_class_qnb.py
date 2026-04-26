import requests
import json
import base64
from requests.structures import CaseInsensitiveDict
import urllib
import logging
_logger = logging.getLogger(__name__)

import logging

logger = logging.getLogger(__name__)


# to do replace with QNB

class PaymentQNB():
    def __init__(self, apiUsername, apiPassword, merchant, order_id, url, host_name):
        self.apiUsername = apiUsername
        self.apiPassword = apiPassword
        self.merchant = merchant
        self.order_id = order_id
        self.url = url
        self.order_currency = None
        self.order_amount = None
        self.checkout_mode = None
        self.result = None
        self.session_id = None
        self.success_indicator = None
        self.session_version = None
        self.session_update_status = None
        self.host_name = host_name

    def create_header(self):
        auth_string = f"{self.apiUsername}:{self.apiPassword}"
        auth_encoded = base64.b64encode(auth_string.encode()).decode()
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        headers["Authorization"] = f"Basic {auth_encoded}"
        return headers

    def authorize(self, order_currency, order_id, order_amount):
        self.order_currency = str(order_currency)
        self.order_amount = str(order_amount)
        data = {"apiOperation": "INITIATE_CHECKOUT",
                "interaction": {
                    "operation": "PURCHASE",
                    "merchant": {
                        "name": self.merchant,
                    },
                    "returnUrl": self.host_name+'/success_payment'

                },
                "order": {
                    "currency": self.order_currency,
                    "amount": self.order_amount,
                    "id": self.order_id,
                    "description": "order_description",
                }

                }
        url = self.url + f'api/rest/version/100/merchant/{self.merchant}/session'
        response = requests.post(url, headers=self.create_header(), data=json.dumps(data,ensure_ascii=False))
        response_dict = response.json()


        try:
            self.result = response_dict['result']

            self.session_id = response_dict['session']['id']
            self.session_version = response_dict['session']['version']

            self.success_indicator = response_dict['successIndicator']

            self.session_update_status = response_dict['session']['updateStatus']
        except Exception as e:
            _logger.error("Exception in authorize QNB %s %s",e,e.with_traceback())
            pass
        return response_dict

    def response_handler(self, content):
        result = urllib.parse.parse_qs(content)
        for k in result.keys():
            result[k] = result[k][0]
        return result

    def retrieve_order(self):

        url=self.url+ f"/api/rest/version/100/merchant/{self.merchant}/order/{self.order_id}"

        try:
            response = requests.get(url, headers=self.create_header())

        except Exception as e:
            _logger.error('HTTPSConnection Pool Connection pool %s', e)

        else:
            response_dict = response.json()

            return response_dict
        return False

    def refund_order(self, order,refunded_amount):

        payload = ('apiOperation=REFUND&apiPassword=' + \
                   self.apiPassword + '&apiUsername=' + self.apiUsername + '&merchant=' + self.merchant +
                   '&order.id=' + self.order_id + '&transaction.amount=' + str(refunded_amount) +
                   '&transaction.currency=' + order.currency_id.name + '&transaction.id=' + order.auth_3d_transaction_id)
        data={
            'apiOperation':"REFUND",
            'transaction':{
                'amount': refunded_amount,
                'currency': order.currency_id.name,

            }

        }
        url=self.url+ f"/api/rest/version/100/merchant/{self.merchant}/order/{self.order_id}/transaction/{order.auth_3d_transaction_id}"
        try:
            response = requests.put(url, headers=self.create_header(), data=json.dumps(data, ensure_ascii=False))
        except Exception as e:
            _logger.error('Exception Pool Connection pool %s', e)
            order.message_post(body="Exception done in refunded {}".format(e))
        else:
            response_dict=response.json()
            return response_dict
        return False
