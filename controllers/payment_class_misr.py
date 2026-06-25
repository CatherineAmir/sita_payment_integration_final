import time

import requests

from requests.structures import CaseInsensitiveDict
import urllib
import logging
from email.utils import formatdate
_logger = logging.getLogger(__name__)
import base64
import hashlib
import hmac
import json
class PaymentMisr():
    def __init__(self, apiUsername, apiPassword, merchant, order_id, url, host_name,secret_key):
        # todo
        self.apiUsername = apiUsername
        self.apiPassword = apiPassword
        self.merchant = merchant
        self.order_id = order_id
        self.url = url
        self.host_name = host_name
        self.secret_key = secret_key

    def _get_digest(self, body:str):
        body_bytes = body.encode("utf-8")
        digest = hashlib.sha256(body_bytes).digest()
        return "SHA-256=" + base64.b64encode(digest).decode("utf-8")


    def _get_signature_retrive_data(self, date,transaction_id,host_name):
        path = f"/tss/v2/transactions/{transaction_id}"
        method = "Get"
        signing_string = "\n".join([
            f"host: {host_name}",
            f"v-c-date: {date}",
            f"request-target: {method.lower()} {path}",
            f"v-c-merchant-id: {self.merchant}",
        ])
        secret_key_bytes = base64.b64decode(self.secret_key)
        sig_bytes = hmac.new(
            secret_key_bytes,
            signing_string.encode("utf-8"),
            hashlib.sha256
        ).digest()
        sig_b64 = base64.b64encode(sig_bytes).decode("utf-8")

        return (
            f'keyid="{self.apiPassword}", '
            f'algorithm="HmacSHA256", '
            f'headers="host v-c-date request-target v-c-merchant-id", '
            f'signature="{sig_b64}"'
        )

    def _get_signature(self, date, digest,host_name):
        path = "/uc/v1/sessions"
        method = "POST"
        signing_string = "\n".join([
            f"host: {host_name}",
            f"v-c-date: {date}",
            f"request-target: {method.lower()} {path}",
            f"digest: {digest}",
            f"v-c-merchant-id: {self.merchant}",
        ])
        print("secret_key", self.secret_key)
        secret_key_bytes = base64.b64decode(self.secret_key)
        sig_bytes = hmac.new(
            secret_key_bytes,
            signing_string.encode("utf-8"),
            hashlib.sha256
        ).digest()
        sig_b64 = base64.b64encode(sig_bytes).decode("utf-8")

        return (
            f'keyid="{self.apiPassword}", '
            f'algorithm="HmacSHA256", '
            f'headers="host v-c-date request-target digest v-c-merchant-id", '
            f'signature="{sig_b64}"'
        )
    def create_header(self,data,api_url):
        # todo
        # auth_string = f"{self.apiUsername}:{self.apiPassword}"
        # auth_encoded = base64.b64encode(auth_string.encode()).decode()
        if api_url == "https://apitest.cybersource.com":
            host_name = "apitest.cybersource.com"
        else:
            # todo when go live change to host live
            host_name = "apitest.cybersource.com"
        date = formatdate(usegmt=True)
        digest = self._get_digest(data)
        headers = CaseInsensitiveDict()
        signature = self._get_signature(date, digest,host_name)
        print("signature", signature)
        print("digest", digest)
        print("date", date)
        headers["host"] = host_name
        headers["Content-Type"] = "application/json"
        headers["v-c-merchant-id"] = str(self.merchant)
        headers["v-c-date"] = date
        headers["digest"] = digest
        headers["signature"] = signature
        return headers

    def create_header_retrive_data(self,transaction_id,api_url):
        # todo
        # auth_string = f"{self.apiUsername}:{self.apiPassword}"
        # auth_encoded = base64.b64encode(auth_string.encode()).decode()
        if api_url == "https://apitest.cybersource.com":
            host_name = "apitest.cybersource.com"
        else:
            # todo when go live change to host live
            host_name = "apitest.cybersource.com"
        date = formatdate(usegmt=True)
        headers = CaseInsensitiveDict()
        signature = self._get_signature_retrive_data(date,transaction_id,host_name)
        print("signature", signature)
        print("date", date)

        headers["host"] = host_name
        headers["v-c-merchant-id"] = str(self.merchant)
        headers["v-c-date"] = date
        headers["signature"] = signature
        return headers


    def authorize(self, order_currency, order_amount,api_url):
        # todo
        price_formatted = f"{order_amount:.2f}"
        self.order_currency = str(order_currency)
        self.order_amount = str(price_formatted)

        print("self.host_name",self.host_name)
        print("price_formatted",price_formatted)
        print("typeprice_formatted",type(price_formatted))
        print("order_currency",self.order_currency)
        origin = self.host_name.replace("http://", "https://") if self.host_name.startswith(
            "http://") else self.host_name if self.host_name.startswith("https://") else "https://" + self.host_name
        print("origin host", origin)
        data = {
            "targetOrigins": [
                origin
            ],
            "country": "EG",
            "locale": "ar_EG",
            "data": {
            "orderInformation": {
                "amountDetails": {
                    "totalAmount": self.order_amount,
                    "currency": self.order_currency,
                }
            }
        }
        }
        body_str = json.dumps(data)
        print("body_str", body_str)
        url = self.url + '/uc/v1/sessions'
        print("url", url)
        try:
            response = requests.post(url, headers=self.create_header(body_str,api_url), data=body_str)
            response_dict = response.content.decode()
            print("response_dict", response_dict)
            return response_dict
        except requests.exceptions.RequestException as e:
            _logger.error('HTTPSConnection Pool Connection pool %s', e)
            return False


    def retrieve_order(self,transaction_id,api_url):
        url = self.url + f'/tss/v2/transactions/{transaction_id}'
        print("url",url)
        max_tries = 5
        base_delay = 2
        for attempt in range(max_tries):
            try:
                response = requests.get(url, headers=self.create_header_retrive_data(transaction_id,api_url))
                response_dict = response.json()
                print(f"retrieve order attempt {attempt+1}: {response_dict}")
                if response_dict.get('applicationInformation',{}).get('status'):
                    return response_dict

                _logger.warning(
                    "Order %s not ready on attempt %s/%s — retrying in %ss",
                    transaction_id, attempt + 1, max_tries, base_delay
                )
            except requests.exceptions.RequestException as e:
                _logger.error('HTTPSConnection Pool Connection pool %s', e)

            if attempt < max_tries-1:
                time.sleep(base_delay)
                base_delay *= 2
        _logger.error("retrieve_order failed after %s attempts for transaction %s", max_tries, transaction_id)
        return None

    # def refund_order(self, order,refund_amount):
    #     real_amount_refund = f"{refund_amount:.2f}"
    #     data_hashed = (str(self.merchant) + str(order.fawry_ref) + str(real_amount_refund) + "Refund" + self.apiPassword)
    #     signature = hash(data_hashed)
    #     data = {
    #         "merchantCode": str(self.merchant),
    #         "referenceNumber": str(order.fawry_ref),
    #         "refundAmount": str(real_amount_refund),
    #         "reason": "Refund",
    #         "signature": signature
    #     }
    #     url = self.url + 'ECommerceWeb/Fawry/payments/refund'
    #     try:
    #     # response = requests.get(url, params = json.dumps(data))
    #         response = requests.post(url, headers=self.create_header(), json=data)
    #         _logger.info("Refund response %s", response)
    #
    #         status_response = response.json()
    #
    #         print("Refund response status codeqqq:", status_response)
    #         print("status_response.get('status_response')",status_response.get('statusCode'))
    #         if status_response.get('statusCode') in (200, 201):
    #
    #             try:
    #                 _logger.info("Refund response %s", response.json())
    #                 return response.json()
    #             except ValueError:
    #                 return {
    #                     "success": False,
    #                     "message": "Refund response is not valid JSON",
    #                     "raw_response": response.text,
    #                 }
    #         #
    #         order.message_post(
    #             body="Refund failed in Fawry. Status: {} Response: {}".format(
    #                 response.status_code, response.text
    #             )
    #         )
    #         return False
    #     except requests.exceptions.RequestException as e:
    #         order.message_post(body="Exception done in refunded in Fawry {}".format(e))
    #         return False
