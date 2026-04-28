# -*- coding: utf-8 -*-
# from odoo import http
import sys
from unittest import result
import logging

_logger = logging.getLogger(__name__)
from odoo import http
from odoo.http import request
from .payment_class_NBE import Payment
from .payment_class_qnb import PaymentQNB
from .kashier_class import Kashier
from .payment_class_fawry import PaymentFawry
import requests
import jinja2
import os
from datetime import datetime
from datetime import timedelta
import pathlib

searchpath = pathlib.Path(__file__).parent.resolve()
templateLoader = jinja2.FileSystemLoader(searchpath=searchpath)
TEMPLATEENV = jinja2.Environment(loader=templateLoader)


class PaymentRequest(http.Controller):

    @http.route('/checkout/order-pay/<string:order_id>/', type='http', auth="public", methods=['GET'], website=True)
    def request_value(self, **kw):

        order_id = request.env['transaction'].sudo().search([('name', '=', kw['order_id'])], )
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if not order_id:
            return

        order_id = order_id[-1]
        link_created = order_id.link_created

        valid_till = order_id.link_validity
        link_type = order_id.account_id.api_url
        company_id = order_id.account_id.company_id
        context = {
            "company_id": company_id,
            "order_id": order_id,
            "account": order_id.account_id,
            "order": order_id,

        }

        if order_id.state == 'not_processed' or order_id.state == 'failed':

            if link_created:
                if link_created + timedelta(hours=valid_till) <= datetime.now():

                    order_id.link_active = False

                    return request.render("sita_payment_integration.link_expired", context)

                else:
                    account_id = order_id.account_id
                    bank = order_id.account_id.bank_name
                    try:
                        if bank == 'NBE':
                            return self.redirect_home_NBE(base_url, account_id, order_id, link_type, company_id)


                        elif bank == 'Kashier':
                            return self.redirect_home_Kashier(base_url, account_id, order_id, link_type, company_id)

                            # return request.render("sita_payment_integration.home_kashier", context)


                        elif bank == "QNB":
                            return self.redirect_home_QNB(base_url, account_id, order_id, link_type, company_id)

                        elif bank == "Fawry":
                            # todo
                            return self.redirect_home_Fawary(base_url, account_id, order_id, link_type, company_id)



                        else:
                            _logger.info("Unknown bank type for order_id %s", order_id.name)



                    except Exception as e:
                        _logger.error("bank session failed for order id %s", e,order_id.name)

                        context = {
                            'error': e,
                            'order_id': order_id,
                            "company_id": company_id,
                            "account": order_id.account_id,
                            "order": order_id,

                        }
                        return request.render("sita_payment_integration.session_failed", context)

        else:
            return self.handel_other_states(context)

    def handel_other_states(self, context):
        print("context", context)
        order_id = context.get('order_id')
        print("order_id.state", order_id.state)
        if order_id.state == 'done':
            template_name = "sita_payment_integration.payment_done"


        elif order_id.state == 'failed':
            template_name = "sita_payment_integration.payment_failed"

        elif order_id.state == 'pending':
            template_name = "sita_payment_integration.payment_pending"

        elif order_id.state == 'expired':
            template_name = "sita_payment_integration.link_expired"


        else:
            _logger.error("error can't recognise order state %s", order_id.state)
            template_name = "sita_payment_integration.payment_pending"

        return request.render(template_name, context)

    @http.route('/webhook_response', type='http', auth="none", methods=['GET', 'POST'], csrf=False)
    def webhook_response(self, **kw):
        print("webhook data", kw)

        # Always return 200
        # return request.make_response("OK", headers=[("Content-Type", "text/plain")])

    @http.route('/success_payment', type='http', auth="none", methods=['GET', 'POST'])
    def success_transaction(self, **kw):
        print("kwwwww", kw)
        print("kw.get("")", kw.get('merchantRefNumber'))
        if kw.get('merchantOrderId'):
            order_id = request.env['transaction'].sudo().search([('name', '=', kw.get('merchantOrderId'))],limit=1)
        elif kw.get('merchantRefNumber'):
            order_id = request.env['transaction'].sudo().search([('name', '=', kw.get('merchantRefNumber'))],limit=1)
        elif kw.get("order_id"):
            order_id = request.env['transaction'].sudo().search([('name', '=', kw.get("order_id"))],limit=1)
        else:
            result_indicator = kw.get('resultIndicator')
            order_id = request.env['transaction'].sudo().search([('success_indicator', '=', result_indicator)])
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        print("order_id",order_id)
        if order_id:
            context = {
                'order_id': order_id,
                "company_id": order_id.account_id.company_id,
                "account": order_id.account_id,
                "order": order_id,

            }
            # print("context", context)
            order_id.sudo().get_order_state()
            # print("order_id after update state", order_id.state)
            return self.handel_other_states(context)

    def redirect_home_NBE(self, base_url, account_id, order_id, link_type, company_id):
        try:
            valid_till = order_id.link_validity
            payment = Payment(account_id.integration_username, account_id.integration_password,
                              account_id.merchant_id, order_id.name, account_id.api_url, base_url)
            session_dict = payment.authorize(order_id.currency_id.name, order_id.name, order_id.amount)
            transaction_vals = {
                'session_id': payment.session_id if hasattr(payment, 'session_id') else None,
                'session_version': payment.session_version if hasattr(payment,
                                                                      'session_version') else None,
                'success_indicator': payment.success_indicator if hasattr(payment,
                                                                          'success_indicator') else None,
                'result': payment.result if hasattr(payment, 'result') else None,
            }

            order_id.write(transaction_vals)
            context = {
                'link_type': link_type,
                'session_id': payment.session_id,
                'order_id': order_id.name,
                'session_version': payment.session_version,
                'merchant_name': account_id.merchant_id,
                'amount': order_id.amount,
                'currency': order_id.currency_id.name,
                'description': order_id.payment_subject.replace("\n", "\t"),
                'client_name': order_id.client_name,
                'client_email': order_id.client_email,
                'reservation_id': order_id.reservation_id,
                "company_id": company_id,
                "account": order_id.account_id,
                "order": order_id,
                "test": True if 'test' in order_id.account_id.api_url else False,
            }

            return request.render("sita_payment_integration.home_nbe", context)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error("bank session NBE failed %s,%s,%s,%s,%s for order_id %s", e, exc_type, exc_obj, exc_tb,
                          order_id.name)

    def redirect_home_Kashier(self, base_url, account_id, order_id, link_type, company_id):
        try:
            valid_till = order_id.link_validity
            payment = Kashier(account_id.integration_username, account_id.integration_password,
                              account_id.secret_key, account_id.merchant_id, account_id.api_url, base_url,
                              session_id=None)
            _logger.info("payment %s",payment)
            expiration_date = (datetime.now() + timedelta(hours=valid_till)).isoformat()

            if not order_id.session_id:
                payment.authorize(order_id.currency_id.name, order_id.name, order_id.amount,
                                  expiration_date, base_url, order_id.client_email,
                                  order_id.client_mobile)
                transaction_vals = {
                    'session_id': payment.session_id if hasattr(payment, 'session_id') else None,
                    'session_url': payment.session_url if hasattr(payment, 'session_url') else None,
                    'target_transaction_id': payment.targetTransactionId if hasattr(payment,
                                                                                    'targetTransactionId') else None,
                }


                order_id.write(transaction_vals)


            context = {
                'link_type': link_type,
                'session_id': order_id.session_id,
                'order_id': order_id.name,
                'merchant_name': account_id.merchant_id,
                'amount': order_id.amount,
                'currency': order_id.currency_id.name,
                'description': order_id.payment_subject.replace("\n", "\t"),
                'client_name': order_id.client_name,
                "customer_email": order_id.client_email,
                "customer_reference": order_id.client_mobile,
                'reservation_id': order_id.reservation_id,
                "company_id": company_id,
                "account": order_id.account_id,
                "order": order_id,
                "session_url": order_id.session_url,
            }

            return request.render("sita_payment_integration.home_kashier", context)
        except Exception as e:

            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error("bank session NBE failed %s,%s,%s,%s,%s for order_id %s", e, exc_type, exc_obj, exc_tb,
                          order_id.name)

    def redirect_home_QNB(self, base_url, account_id, order_id, link_type, company_id):
        try:
            payment = PaymentQNB(account_id.integration_username, account_id.integration_password,
                                 account_id.merchant_id, order_id.name, account_id.api_url, base_url)

            session_dict = payment.authorize(order_id.currency_id.name, order_id.name, order_id.amount)

            transaction_vals = {
                'session_id': payment.session_id if hasattr(payment, 'session_id') else None,
                'session_version': payment.session_version if hasattr(payment,
                                                                      'session_version') else None,
                'success_indicator': payment.success_indicator if hasattr(payment,
                                                                          'success_indicator') else None,
                'result': payment.result if hasattr(payment, 'result') else None,
            }

            order_id.write(transaction_vals)
            context = {
                'link_type': link_type,
                'session_id': payment.session_id,
                'order_id': order_id.name,
                'session_version': payment.session_version,
                'merchant_name': account_id.merchant_id,
                'amount': order_id.amount,
                'currency': order_id.currency_id.name,
                'description': order_id.payment_subject.replace("\n", "\t"),
                'client_name': order_id.client_name,
                'client_email': order_id.client_email,
                'reservation_id': order_id.reservation_id,
                "company_id": company_id,
                "account": order_id.account_id,
                "order": order_id,
            }
            return request.render("sita_payment_integration.home_qnb", context)
        except Exception as e:

            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error("bank session QNB failed %s,%s,%s,%s,%s for order_id %s", e, exc_type, exc_obj, exc_tb,
                          order_id.name)


    def redirect_home_Fawary(self,base_url, account_id, order_id, link_type, company_id):

        try:
            # valid_till = order_id.link_validity
            payment = PaymentFawry(account_id.integration_username, account_id.integration_password,
                              account_id.merchant_id, order_id.name, link_type, base_url)
            session_dict = payment.authorize(order_id.currency_id.name, order_id.amount,order_id.client_mobile,order_id.client_email)
            context = {
                'link_type': link_type,
                'order_id': order_id.name,
                'merchant_name': account_id.merchant_id,
                'amount': order_id.amount,
                'currency': order_id.currency_id.name,
                'client_name': order_id.client_name,
                'client_email': order_id.client_email,
                'reservation_id': order_id.reservation_id,
                "company_id": company_id,
                "account": order_id.account_id,
                "order": order_id,
                "session_url": session_dict,
                "test": True if 'test' in order_id.account_id.api_url else False,
            }

            return request.render("sita_payment_integration.home_fawry", context)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error("fawry  failed %s,%s,%s,%s,%s for order_id %s", e, exc_type, exc_obj, exc_tb,
                          order_id.name)
