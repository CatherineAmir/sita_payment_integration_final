
import requests
import json
import base64
from requests.structures import CaseInsensitiveDict
import urllib
import logging
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

    def authorize(self, order_currency, order_amount):
        # todo
        self.order_currency = str(order_currency)
        self.order_amount = float(order_amount)
        price_formatted = f"{self.order_amount:.2f}"
        # return_url = self.host_name+f'/success_payment/?order_id={self.order_id}'

        return_url = self.host_name + '/success_payment'
        print("return_url", return_url)
        data = (self.merchant + self.order_id + ""+ return_url + "Reservation" + "1" + price_formatted + self.apiPassword)
        # print("data", data)
        signature = hash(data)
        # print("signature", signature)
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
            "returnUrl": return_url,
            "orderWebHookUrl":return_url,
            "signature": signature
        }
        # print("data", data)
        url = self.url + 'fawrypay-api/api/payments/init'
        response = requests.post(url, headers=self.create_header(), json=data)
        # response_dict = response.json()
        response_dict = response.content.decode()
        # print("response_dict", response_dict)
        # try:
        #     self.result = response_dict['result']
        #
        #     self.session_id = response_dict['session']['id']
        #     self.session_version = response_dict['session']['version']
        #
        #     self.success_indicator = response_dict['successIndicator']
        #
        #     self.session_update_status = response_dict['session']['updateStatus']
        # except Exception as e:
        #     _logger.error("Exception in authorize QNB %s %s",e,e.with_traceback())
        #     pass
        # link
        return response_dict

    def response_handler(self, content):
        result = urllib.parse.parse_qs(content)
        print("result", result)
        for k in result.keys():
            result[k] = result[k][0]
        return result

    def retrieve_order(self):
        url = self.url + 'ECommerceWeb/Fawry/payments/status/v2'
        data = (self.merchant + self.order_id + self.apiPassword)
        signature = hash(data)
        # print("url", url)
        # print("signature", signature)
        PaymentData = {'merchantCode': self.merchant, 'merchantRefNumber': self.order_id, 'signature': signature}

        status_request = requests.get(url=url, params=PaymentData)
        status_response = status_request.json()
        # print("Status Code: ", status_response)
        return status_response

        # url=self.url+ f"/api/rest/version/100/merchant/{self.merchant}/order/{self.order_id}"
        #
        # try:
        #     response = requests.get(url, headers=self.create_header())
        #
        # except Exception as e:
        #     _logger.error('HTTPSConnection Pool Connection pool %s', e)
        #
        # else:
        #     response_dict = response.json()
        #
        #     return response_dict
        # return False

    def refund_order(self, order,refunded_amount):
        # refund order in fawry
        # todo
        #
        # payload = ('apiOperation=REFUND&apiPassword=' + \
        #            self.apiPassword + '&apiUsername=' + self.apiUsername + '&merchant=' + self.merchant +
        #            '&order.id=' + self.order_id + '&transaction.amount=' + str(refunded_amount) +
        #            '&transaction.currency=' + order.currency_id.name + '&transaction.id=' + order.auth_3d_transaction_id)
        # data={
        #     'apiOperation':"REFUND",
        #     'transaction':{
        #         'amount': refunded_amount,
        #         'currency': order.currency_id.name,
        #
        #     }
        #
        # }
        # url=self.url+ f"/api/rest/version/100/merchant/{self.merchant}/order/{self.order_id}/transaction/{order.auth_3d_transaction_id}"
        # try:
        #     response = requests.put(url, headers=self.create_header(), data=json.dumps(data, ensure_ascii=False))
        # except Exception as e:
        #     _logger.error('Exception Pool Connection pool %s', e)
        #     order.message_post(body="Exception done in refunded {}".format(e))
        # else:
        #     response_dict=response.json()
        #     return response_dict
        return False