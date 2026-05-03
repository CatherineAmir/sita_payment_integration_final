import requests
import json
import base64
from requests.structures import CaseInsensitiveDict
import urllib
import logging

_logger = logging.getLogger(__name__)
from ..tools.hashing_aaib import hash


class AAIB():
    def __init__(self, apiUsername, apiPassword, public_key, order_id, url, host_name):
        # todo
        self.apiUsername = apiUsername
        self.apiPassword = apiPassword
        # self.merchant = merchant
        self.order_id = order_id
        self.url = url
        self.public_key = public_key
        self.host_name = host_name

    def create_header(self):
        # todo
        # auth_string = f"{self.apiUsername}:{self.apiPassword}"
        # auth_encoded = base64.b64encode(auth_string.encode()).decode()
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        # headers["Authorization"] = f"Basic {auth_encoded}"
        return headers

    def authorize(self, order_currency, order_amount, customer_name, customer_email):
        # todo
        self.order_currency = str(order_currency)
        self.order_amount = str(order_amount)
        first_name, last_name = customer_name.split(" ", 1)
        hash_key = self.apiPassword
        order_title = "Reservation"
        data_hashed = [
            first_name,
            last_name,
            customer_email,
            order_title,
            self.order_amount,
            self.order_currency,
        ]
        print("data_hashed", data_hashed)
        concatenated = ''.join(data_hashed)
        signature = hash(concatenated , hash_key)
        print("signature", signature)
        data = {
            "token": self.public_key,
            "first_name": first_name,
            "last_name": last_name,
            "email": customer_email,
            "order_title": "Reservation",
            "order_amount": self.order_amount,
            "currency": self.order_currency,
            "signature": signature
        }
        # print("ordercallback", self.host_name + '/webhook_response')
        url = self.url + '/api/integration/init'
        try:
            response = requests.post(url, headers=self.create_header(), json=data)
            response_dict = response.json()
            print("response_dict", response_dict)
            return response_dict
        except requests.exceptions.RequestException as e:
            _logger.error('HTTPSConnection Pool Connection pool %s', e)
            return False

    def response_handler(self, content):
        result = urllib.parse.parse_qs(content)
        print("result", result)
        for k in result.keys():
            result[k] = result[k][0]
        return result

    def retrieve_order(self):
        return
