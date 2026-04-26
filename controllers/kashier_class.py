import requests
import logging
_logger = logging.getLogger(__name__)
host_name = 'sita-pay.com'
import logging
import json
logger = logging.getLogger(__name__)

class Kashier():
    def __init__(self, apiUsername, apiPassword, secret_key, merchant_id, url, host_name,session_id):
        self.apiUsername = apiUsername
        self.apiPassword = apiPassword
        self.secret_key = secret_key
        self.merchant_id = merchant_id
        self.url = url
        self.order_currency = None
        self.order_amount = None
        self.checkout_mode = None
        self.result = None
        self.session_id = session_id
        # self.success_indicator = None
        # self.session_version = None
        # self.session_update_status = None
        self.host_name = host_name
        self.session_url = None
        # self.order_uid = None
        self.targetTransactionId = None

    def create_header(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"{self.secret_key}",
            "api-key": f"{self.apiPassword}",
        }
    def create_header_refund(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"{self.secret_key}",
            "accept": "application/json"
        }


    def authorize(self, order_currency, order_id, order_amount, expiration_date,base_url,customer_email,customer_reference):
        self.order_currency = str(order_currency)
        self.order_amount = str(order_amount)
        data = {
            "expireAt": expiration_date,
            "maxFailureAttempts": 3,
            "amount": self.order_amount,
            "currency": self.order_currency,
            "order": order_id,
            "display": "en",
            "type": "one-time", # to discuss
            "merchantId": self.merchant_id,
            "merchantRedirect": base_url + '/success_payment',
            "allowedMethods" : "card",
            "customer": {
                "email": customer_email,
                "reference": customer_reference
            }
        }
        url = self.url + "payment/sessions"
        print("url", url)
        response = requests.post(url, headers=self.create_header(), json=data)
        response_dict = response.json()
        print("response_dict", response_dict)
        _logger.info("response_dict %s", response_dict)
        try:
            self.session_id = response_dict.get('_id', None)
            self.session_url = response_dict.get('sessionUrl', None)
            self.targetTransactionId = response_dict.get('targetTransactionId', None)
            # self.order_uid = response_dict.get('orderId', None)

        except Exception as e:
            _logger.error("Exception in authorize Kashier", exc_info=True)
            pass
        return response_dict

    def retrieve_order(self):
        print("session_id in retrieve_order:", self.session_id)
        url = self.url + f"payment/sessions/{self.session_id}/payment"
        response = requests.get(url, headers=self.create_header())
        response_dict = response.json()
        print("retrieve_order_response", response_dict)
        return response_dict


    def refund_order(self,order,refund_amount):
        print("Refunding order with ID:", order.kashier_order_id, "and target transaction ID:", order.target_transaction_id)
        print("Refund amount:", refund_amount)
        print("order:", order.kashier_order_id)
        data = {
            "apiOperation": "REFUND",
            "reason": "Refunded",
            "transaction": {
                "amount": refund_amount,
                "targetTransactionId": order.target_transaction_id,
                "currency": order.currency_id.name,
            }
        }
        if order.account_id.api_url == 'https://test-api.kashier.io/v3/':
            url = f"https://test-fep.kashier.io/v3/orders/{order.kashier_order_id}"
        else:
            url = f"https://fep.kashier.io/v3/orders/{order.kashier_order_id}"
        print('Refund URL:', url)
        # try:
        headers = self.create_header_refund()
        print("Refund request headers:", headers)
        try:
            response = requests.put(url, headers=headers, json=data)
            print("Refund response status code:", response)
            # response_dict = response.json()
            # print("Refund response:", response_dict)
            # except Exception as e:
            #     _logger.error('Exception Pool Connection pool in Kashier %s', e)
            #     order.message_post(body="Exception done in refunded in Kasheier {}".format(e))
            # else:
            if response.status_code in (200, 201):
                try:
                    return response.json()
                except ValueError:
                    return {
                        "success": False,
                        "message": "Refund response is not valid JSON",
                        "raw_response": response.text,
                    }

            order.message_post(
                body="Refund failed in Kashier. Status: {} Response: {}".format(
                    response.status_code, response.text
                )
            )
            return False
        except requests.exceptions.RequestException as e:
            order.message_post(body="Exception done in refunded in Kashier {}".format(e))
            return False
