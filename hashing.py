# import hashlib
# def generate_signature_refund(
#     merchant_code: str,
#     ref_num: str,
#     refund_amount: str,
#     reason: str ,
#     secure_hash_key: str,
# ) -> str:
#     """
#     Generates a SHA-256 request signature.
#
#     Concatenation order:
#     merchantCode + merchantRefNum + customerProfileId + returnUrl + itemId + quantity + price + secureHashKey
#     """
#
#     # Format price to exactly 2 decimal places
#     # price_formatted = f"{price:.2f}"
#
#     # Concatenate all fields in the required order
#     raw_string = (
#         merchant_code +
#         ref_num +
#         refund_amount +# Empty string "" if not provided
#         reason +
#         secure_hash_key
#     )
#     print("raw_string", raw_string)
#     # Hash using SHA-256
#     signature = hashlib.sha256(raw_string.encode("utf-8")).hexdigest()
#
#     return signature
# def get_generate_signature(
#     merchant_code: str,
#     merchant_ref_num: str,
#     secure_hash_key: str,
#     # return_url: str,
#     # item_id: str,
#     # quantity: str | int,
#     # price: float =,
#
#     # customer_profile_id: str = ""  # Optional, defaults to empty string
# ) -> str:
#     """
#     Generates a SHA-256 request signature.
#
#     Concatenation order:
#     merchantCode + merchantRefNum + customerProfileId + returnUrl + itemId + quantity + price + secureHashKey
#     """
#
#     # Format price to exactly 2 decimal places
#     # price_formatted = f"{price:.2f}"
#
#     # Concatenate all fields in the required order
#     raw_string = (
#         merchant_code +
#         merchant_ref_num +
#         # customer_profile_id +      # Empty string "" if not provided
#         # return_url +
#         # item_id +
#         # str(quantity) +
#         # price_formatted +
#         secure_hash_key
#     )
#
#     # Hash using SHA-256
#     signature = hashlib.sha256(raw_string.encode("utf-8")).hexdigest()
#
#     return signature
# def generate_signature(
#     merchant_code: str,
#     merchant_ref_num: str,
#     return_url: str,
#     item_id: str,
#     quantity: str | int,
#     price: float ,
#     secure_hash_key: str,
#     customer_profile_id: str = ""  # Optional, defaults to empty string
# ) -> str:
#     """
#     Generates a SHA-256 request signature.
#
#     Concatenation order:
#     merchantCode + merchantRefNum + customerProfileId + returnUrl + itemId + quantity + price + secureHashKey
#     """
#
#     # Format price to exactly 2 decimal places
#     price_formatted = f"{price:.2f}"
#
#     # Concatenate all fields in the required order
#     raw_string = (
#         merchant_code +
#         merchant_ref_num +
#         customer_profile_id +# Empty string "" if not provided
#         return_url +
#         item_id +
#         str(quantity) +
#         price_formatted +
#         secure_hash_key
#     )
#     print("raw_string", raw_string)
#     # Hash using SHA-256
#     signature = hashlib.sha256(raw_string.encode("utf-8")).hexdigest()
#
#     return signature
#
#
# # ── Example Usage ──────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     # sig = generate_signature(
#     #     merchant_code="770000013917",
#     #     merchant_ref_num="ord0000000116",
#     #     return_url="https://f5f9-197-47-137-59.ngrok-free.app/success_payment",
#     #     item_id="Reservation",
#     #     quantity=1,
#     #     price=50.00,
#     #     secure_hash_key="1e76ec5b-ae12-497f-b58b-ed9fca686f6c",
#     #     customer_profile_id=""   # omit or pass "" if not applicable
#     # )
#     # sig_two = "770000013917"+"231246546415"+ "1e76ec5b-ae12-497f-b58b-ed9fca686f6c"
#     #
#     #
#     # sig_2=hashlib.sha256(sig_two).hexdigest()
#     # merchantCode = "770000013917"
#     # merchantRefNumber = "231246546415"
#     # merchant_sec_key = "1e76ec5b-ae12-497f-b58b-ed9fca686f6c"
#     # signature = hashlib.sha256((merchantCode + merchantRefNumber + merchant_sec_key).encode("utf-8")).hexdigest()
#     #
#     # print("Signature:", signature)
#     # print("Signature: ", sig)
#     # importing the requests library
#     import requests
#     # importing Hash Library
#     # import hashlib
#
#     # FawryPay Get Payment Status api-endpoint
#     # URL = "https://atfawry.fawrystaging.com/ECommerceWeb/Fawry/payments/status/v2"
#
#     # Payment Data
#     # merchantCode = "770000013917"
#     # merchantRefNumber = "231246546416"
#     # merchant_sec_key = "1e76ec5b-ae12-497f-b58b-ed9fca686f6c"
#     # signature = hashlib.sha256((merchantCode + merchantRefNumber + merchant_sec_key).encode("utf-8")).hexdigest()
#     #
#     # defining a params dict for the parameters to be sent to the API
#     # PaymentData = {'merchantCode': merchantCode, 'merchantRefNumber': merchantRefNumber, 'signature': signature}
#
#     # sending get request and saving the response as response object
#     # status_request = requests.get(url=URL, params=PaymentData)
#
#     # extracting data in json format
#     # status_response = status_request.json()
#     # print("Status Code: ", status_response)
#     # merchantCode = '770000013917'
#     # referenceNumber = '781408588'
#     # refundAmount = '100.0'
#     # reason = 'Refund'
#     # merchant_sec_key = '1e76ec5b-ae12-497f-b58b-ed9fca686f6c'
#     # data = (merchantCode + referenceNumber + refundAmount + reason + merchant_sec_key)
#     # print("data", data)
#     # signature = hashlib.sha256((merchantCode + referenceNumber + refundAmount + reason + merchant_sec_key).encode('utf-8')).hexdigest()
#     # print("signature", signature)
#     sig = generate_signature_refund(
#         merchant_code="770000013917",
#         ref_num="781491088",
#         refund_amount="100.",
#         reason='Refund',
#         secure_hash_key="1e76ec5b-ae12-497f-b58b-ed9fca686f6c",
#     )
#     print("sig", sig)

