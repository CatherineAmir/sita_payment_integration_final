import requests
import json
import base64
from requests.structures import CaseInsensitiveDict
import urllib
# host_name='localhost:8069'
from requests.auth import HTTPBasicAuth
import logging

_logger = logging.getLogger(__name__)
host_name = 'sita-pay.com'
import logging

logger = logging.getLogger(__name__)
"""
NBE FOR API VERSION 100 REST
"""

class Payment_REST():
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
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        return headers

    def authorize(self, order_currency, order_id, order_amount):
        self.order_currency = str(order_currency)
        self.order_amount = str(order_amount)


        payload = {
            "apiOperation": "INITIATE_CHECKOUT",
            "interaction": {
                "operation": "PURCHASE",
                "returnUrl": self.host_name + '/success_payment',
                "cancelUrl":self.host_name + '/cancel_payment',
                "merchant": {
                    "name": self.merchant
                }
            },
            "order": {
                "id": self.order_id,
                "amount": self.order_amount,
                "currency": self.order_currency,
                "description": "Hotel Reservation",
            },
            "checkoutMode": "WEBSITE"
        }

        print("payload", payload)
        auth = (self.apiUsername, self.apiPassword)

        print("auth", auth)
        print("headers", self.create_header())
        headers = self.create_header()
        # headers['Username'] = self.apiUsername
        # headers['Password'] = self.apiPassword
        print("headers", headers)
        if  self.url.endswith("/"):
            self.url=self.url[:-1]
        url=self.url+f"/merchant/{self.merchant}/session"
        print("url", url)
        target_url="https://test-nbe.gateway.mastercard.com/api/rest/version/100/merchant/TESTEGPTEST/session"
        print("target_url", target_url)
        print("check url",target_url==url)

        response = requests.post(
            url=url,
            auth=auth,
            headers=headers,
            json=payload,
            timeout=30,
        )
        print("response", response)
        response.raise_for_status()
        print(response.json())
        response_dict = response.json()
        # print("response", response)
        # response_dict = self.response_handler(response.content.decode())
        print("response_dict", response_dict)

        try:
            self.result = response_dict.get('result',"")
            self.session_id = response_dict.get('session',"").get("id",'')
            self.session_version = response_dict.get('session',"").get("version",'')

            self.success_indicator = response_dict.get('successIndicator')

            self.session_update_status =  response_dict.get('session',"").get("updateStatus",'')
        except Exception as e:
            _logger.error("Error in authorize %s", e)

            pass
        return response_dict

    def response_handler(self, content):
        result = urllib.parse.parse_qs(content)
        for k in result.keys():
            result[k] = result[k][0]
        return result
    # todo fix to json
    def retrieve_order(self):
        if not self.url.endswith("/"):
            self.url=self.url[:-1]
        url=self.url+f"/merchant/{self.merchant}/order/{self.order_id}"

        print("url rest",url)
        auth=(self.apiUsername, self.apiPassword)

        # payload = 'apiOperation=RETRIEVE_ORresponseDER&apiPassword=' + self.apiPassword + '&apiUsername=' + self.apiUsername + '&merchant=' + self.merchant + '&order.id=' + self.order_id
        try:
            response = requests.get(url, headers=self.create_header(), auth=auth)
            print("response",response)
        except Exception as e:
            _logger.error('HTTPSConnection Pool Connection pool %s', e)



        else:
            response_dict=response.json()
            print("response_dict", response_dict)
            # response_dict = self.response_handler(response.content.decode())

            return response_dict
        return False
    # todo fix to json
    def refund_order(self, order, refunded_amount):

        payload = ('apiOperation=REFUND&apiPassword=' + \
                   self.apiPassword + '&apiUsername=' + self.apiUsername + '&merchant=' + self.merchant +
                   '&order.id=' + self.order_id + '&transaction.amount=' + str(refunded_amount) +
                   '&transaction.currency=' + order.currency_id.name + '&transaction.id=' + order.auth_3d_transaction_id)

        try:
            response = requests.post(self.url, headers=self.create_header(), data=payload)
        except Exception as e:
            # print("Exception",e)
            _logger.error('Exception Pool Connection pool %s', e)
            order.message_post(body="Exception done in refunded {}".format(e))
        else:
            response_dict = self.response_handler(response.content.decode())
            # print("response_dict",response_dict)

            return response_dict
        return False
