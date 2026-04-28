
import requests
import json
import base64
from requests.structures import CaseInsensitiveDict
import urllib
import logging
import hashlib
_logger = logging.getLogger(__name__)
from ..tools.hashing_fawry import hash


class PaymentFawry():
    def __init__(self, apiUsername, apiPassword, merchant, order_id, url, host_name):
        # todo
        self.apiUsername = apiUsername
        self.apiPassword = apiPassword
        self.merchant = merchant
        self.order_id = order_id
        self.url = url
        # self.order_currency = None
        # self.order_amount = None
        # self.checkout_mode = None
        # self.result = None
        # self.session_id = None
        # self.success_indicator = None
        # self.session_version = None
        # self.session_update_status = None
        self.host_name = host_name

    def create_header(self):
        # todo
        # auth_string = f"{self.apiUsername}:{self.apiPassword}"
        # auth_encoded = base64.b64encode(auth_string.encode()).decode()
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        # headers["Authorization"] = f"Basic {auth_encoded}"
        return headers

    def authorize(self, order_currency, order_amount,customer_mobile=None,customer_email=None):
        # todo
        self.order_currency = str(order_currency)
        self.order_amount = float(order_amount)
        price_formatted = f"{self.order_amount:.2f}"
        return_url = self.host_name + f'/success_payment/?order_id={self.order_id}'
        data_hashed = (self.merchant + self.order_id + ""+ return_url + "Reservation" + "1" + price_formatted + self.apiPassword)
        signature = hash(data_hashed)
        data = {
            "merchantCode": self.merchant,
            "merchantRefNum": self.order_id,
            "language": "en-gb",
            "chargeItems": [
                {
                    "itemId": "Reservation",
                    "description": "Reservation Details",
                    "price": order_amount,
                    "quantity": 1,
                }
            ],
            "customerMobile": customer_mobile if customer_mobile else "",
            "customerEmail": customer_email if customer_email else "",
            "returnUrl": return_url,
            "signature": signature
        }

        url = self.url + 'fawrypay-api/api/payments/init'
        try:
            response = requests.post(url, headers=self.create_header(), json=data)
            response_dict = response.content.decode()
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
        url = self.url + 'ECommerceWeb/Fawry/payments/status/v2'
        data = (str(self.merchant) + str(self.order_id) + self.apiPassword)
        signature = hash(data)
        PaymentData = {'merchantCode': self.merchant, 'merchantRefNumber': self.order_id, 'signature': signature}
        try:
            status_request = requests.get(url=url, params=PaymentData)
            status_response = status_request.json()
            return status_response
        except requests.exceptions.RequestException as e:
            _logger.error('HTTPSConnection Pool Connection pool %s', e)



    def refund_order(self, order,refund_amount):
        real_amount_refund = f"{refund_amount:.2f}"
        data_hashed = (str(self.merchant) + str(order.fawry_ref) + str(real_amount_refund) + "Refund" + self.apiPassword)
        signature = hash(data_hashed)
        data = {
            "merchantCode": str(self.merchant),
            "referenceNumber": str(order.fawry_ref),
            "refundAmount": str(real_amount_refund),
            "reason": "Refund",
            "signature": signature
        }
        url = self.url + 'ECommerceWeb/Fawry/payments/refund'
        try:
        # response = requests.get(url, params = json.dumps(data))
            response = requests.post(url, headers=self.create_header(), json=data)
            status_response = response.json()
            print("Refund response status codeqqq:", status_response)
            print("status_response.get('status_response')",status_response.get('statusCode'))
            if status_response.get('statusCode') in (200, 201):

                try:
                    print("in return")
                    return response.json()
                except ValueError:
                    return {
                        "success": False,
                        "message": "Refund response is not valid JSON",
                        "raw_response": response.text,
                    }
            #
            order.message_post(
                body="Refund failed in Fawry. Status: {} Response: {}".format(
                    response.status_code, response.text
                )
            )
            return False
        except requests.exceptions.RequestException as e:
            order.message_post(body="Exception done in refunded in Fawry {}".format(e))
            return False