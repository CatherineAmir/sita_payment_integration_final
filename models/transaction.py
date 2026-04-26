import sys
from email.policy import default

from odoo import api, fields, models, _
from datetime import datetime
from datetime import timedelta

from ..controllers.kashier_class import Kashier
from ..controllers.payment_class_NBE import Payment
from ..controllers.payment_class_qnb import PaymentQNB
from odoo.exceptions import ValidationError
import urllib.parse as parse
import logging


_logger = logging.getLogger(__name__)


# todo: add
# todo domain account company
# add user id and user see all transaction or hiw own transactions
# website logo
# website footer
# remove contact us
# remove
# sign in

class Transaction(models.Model):
    _name = 'transaction'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'details for transaction'
    _order = 'created_on desc'
    name = fields.Char(string="Transaction", copy=False)
    account_id = fields.Many2one('account_manager', string="Account", tracking=True, readonly=False,
                                 store=True)
    company_id = fields.Many2one('res.company', string="Hotel Name", default=lambda self: self.env.company.id,
                                 readonly=True)
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user.id)
    created_on = fields.Datetime(default=lambda self: datetime.now(), string='Created on date')
    verified_on = fields.Datetime(string='Verified on', tracking=True, )
    failed_on = fields.Datetime(string='Failed  on', tracking=True)
    link_created = fields.Datetime(string='Link Creation Date', tracking=True)
    client_name = fields.Char('Guest Name', tracking=True, )

    client_email = fields.Char('Guest Email', tracking=True, )

    client_mobile = fields.Char('Guest Mobile', tracking=True)

    reservation_id = fields.Char('Reservation Number', tracking=True)
    amount = fields.Monetary('Amount', tracking=True,
                             )

    state = fields.Selection(selection=[
        ('not_processed', 'New'),
        ('done', 'Paid'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
        ('expired', "Expired"),
        ('refunded', "Refunded"),
        ('partially_refunded', "Partially Refunded"),

    ], string='state', tracking=True, default='not_processed', copy=False, store=True)
    payment_subject = fields.Text('Service  Description', default='Hotel Reservation', required=True, readonly=True,
                                  )

    payment_link = fields.Char(copy=False, tracking=True)
    currency_id = fields.Many2one('res.currency', related='account_id.currency_id', store=True)
    session_id = fields.Char(string='Session ID', copy=False, tracking=True)
    session_version = fields.Char(string='Session Version', copy=False, tracking=True)
    success_indicator = fields.Char(string="Success Indicator", copy=False, tracking=True)
    result = fields.Char(string=" Result", copy=False, tracking=True)
    authentication_status = fields.Char(string='Authentication Status', copy=False, tracking=True)

    amount_charged = fields.Monetary('Amount Charged')
    auth_3d_transaction_id = fields.Char()
    certainty = fields.Char()
    chargeback_amount = fields.Monetary('Charge back amount')
    chargeback_currency = fields.Char('Charge back Currency')

    error_cause = fields.Char('Error Cause')
    error_explanation = fields.Char('Error Explanation')
    link_active = fields.Boolean(default=False)
    link_validity = fields.Integer(default=72, string="Link expiration after (in hours)")
    payment_state = fields.Char('Transaction State')

    internal_note = fields.Text("Internal Notes")
    active = fields.Boolean("Active", default=True)

    # refund fields
    order_amount = fields.Float(" Original Order Amount", tracking=True)
    order_chargeback_amount = fields.Float("Chargeback Order Amount", tracking=True)
    order_last_updated_time = fields.Datetime("Last Updated Time", tracking=True)
    last_status = fields.Char("Last Status", tracking=True, default="")
    order_refunded_amount = fields.Float("Refunded Amount", tracking=True)
    response_gateway_code = fields.Char("Gateway Code", tracking=True)
    refund_result = fields.Char("Refund Result", tracking=True)
    refund_try = fields.Char("Refund Try", tracking=True)
    refund_error = fields.Char("Refund Error", tracking=True)
    refund_error_explanation = fields.Char("Refund Error Explanation", tracking=True)
    expire_on = fields.Datetime("Expiration Date", tracking=True, compute='_compute_expire_on', store=True)
    refund_amount = fields.Float('Actual Refund Amount')
    refunded_amount = fields.Float(string=' Requested Refund Amount', tracking=True)


    #kashier fields
    # customer_reference = fields.Char("Customer Reference")
    # customer_email = fields.Char("Customer Email")
    bank_name = fields.Selection(related='account_id.bank_name', string='Bank Name')
    session_url = fields.Char(string="Session URL", copy=False, tracking=True)
    payment_status = fields.Char(string="Payment Status", copy=False, tracking=True)
    order_id = fields.Char(string="Order ID", copy=False, tracking=True)
    kashier_refund_amount = fields.Float('Kashier Refund Amount')
    target_transaction_id = fields.Char(string="Target Transaction ID")
    kashier_order_id = fields.Char(string="Kashier Order ID", copy=False, tracking=True)


    # kashier_refund_amount_reminder = fields.Float(string='Kashier Refund Amount Reminder')

    @api.constrains('kashier_refund_amount')
    def _check_kashier_refund_amount(self):
        for rec in self:
            if rec.kashier_refund_amount > rec.amount:
                raise ValidationError(_("Refund amount cannot be greater than the charged amount."))

    @api.depends('link_validity', 'link_created')
    def _compute_expire_on(self):
        for r in self:
            if r.link_created:
                r.expire_on = r.link_created + timedelta(hours=r.link_validity)

    def send_whatsapp(self):

        link = "https://web.whatsapp.com/send?phone=" + self.client_mobile
        if self.client_mobile.startswith("01") and len(self.client_mobile) == 11:

            link = "https://wa.me/" + "+2" + self.client_mobile
        elif self.client_mobile.startswith('+'):
            link = "https://wa.me/" + "+2" + self.client_mobile
        elif len(self.client_mobile) < 11:
            raise ValidationError(_("Client Mobile should be minimum 11 charachers"))
        else:
            raise ValidationError(_("Client Mobile should Start with + and country code if the client is not Egyptian"))

        message_string = """
        *Hello {}* 
        
        *Your reservation description* : {}
        *Your Total Amount is:* {} {} 
        *You can pay by the following link:*
        *{}*
        *This Link is valid for:* {} Hours         
        """.format(self.client_name, self.payment_subject, self.amount, self.currency_id.name
                   , self.payment_link, self.link_validity)

        return {
            'type': 'ir.actions.act_url',
            'name': "Whatsapp",
            'url': link + "?text=" + parse.quote(message_string),
            'target': 'new'
        }

    def get_kashier_payment_status(self,base_url,account_id,order_id):
        # account_id = order_id.account_id
        payment = Kashier(account_id.integration_username, account_id.integration_password,
                          account_id.secret_key, account_id.merchant_id,
                          account_id.api_url, base_url,order_id.session_id)
        order_state = payment.retrieve_order()

        try:
            if order_state['message'] == 'success' and order_state['data']['status'] == 'PAID':
                payment_status = 'done'
            elif order_state['message'] == 'success' and order_state['data']['status'] == 'PENDING':
                payment_status = 'pending'
            elif order_state['message'] == 'success' and order_state['data']['status'] == 'FAILED':
                payment_status = 'failed'
            elif order_state['message'] == 'success' and order_state['data']['status'] == 'PARTIALLY_REFUNDED':
                payment_status = 'partially_refunded'
            elif order_state['message'] == 'success' and order_state['data']['status'] == 'REFUNDED':
                payment_status = 'refunded'
            else:
                payment_status = 'not_processed'

            _logger.info("payment_status in kashier %s", payment_status)
            payment_details = {
                'amount_charged': float(order_state['data']['amount']),

                'state': payment_status,
                'payment_status': payment_status,
                'kashier_order_id': str(order_state['data']['orderId']),
                'target_transaction_id': str(order_state['data']['targetTransactionId'])

            }
            order_id.sudo().write(payment_details)

        except Exception as e:
            _logger.error("Exception in Get Kashier Order State %s ", e)

        return True

    def get_state_NBE(self,base_url,account_id,order_id):
        try:
            payment = Payment(account_id.integration_username, account_id.integration_password,
                              account_id.merchant_id,
                              order_id.name, account_id.api_url, base_url)
            order_state = payment.retrieve_order()
            if order_state["result"] == "ERROR":
                raise ValidationError(_("Error in get order state : %s", order_state["error.explanation"]))
            flag = 0
            # kashier status is different

            if order_state['result'] == 'SUCCESS' and order_state['status'] == 'CAPTURED':
                payment_status = 'done'
                flag = 1
            elif order_state['result'] == 'SUCCESS' and order_state['status'] in ['AUTHORIZED']:
                payment_status = 'pending'
                flag = 1
            elif order_state['result'] == 'SUCCESS' and order_state['status'] == 'AUTHENTICATION_UNSUCCESSFUL':
                payment_status = 'failed'
                flag = 1
            elif order_state['status'] == 'FAILED':
                payment_status = 'failed'
                flag = 1

            elif order_state['status'] == 'REFUNDED':
                payment_status = 'refunded'
                flag = 1
            elif order_state['status'] == 'PARTIALLY_REFUNDED':
                payment_status = 'partially_refunded'
                flag = 1
            else:
                payment_status = order_id.state

            if flag:
                datetime_str = order_state['creationTime']
                date_time_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                payment_details = {
                    'amount_charged': float(order_state.get('totalCapturedAmount', 0)),
                    'auth_3d_transaction_id': order_state.get('authentication', {}).get('3ds', {}).get('transactionId', ""),
                    'chargeback_amount': float(order_state.get('chargeback.amount', 0.0)),
                    'chargeback_currency': order_state.get('chargeback.currency', ""),
                    'verified_on': date_time_obj,
                    'result': order_state.get('result', ""),
                    'state': payment_status,
                    'authentication_status': order_state.get('authenticationStatus', ""),
                    'payment_state': order_state.get('paymentState', ""),
                }

                order_id.write(payment_details)
            else:
                try:

                    date_time_obj = datetime.now()
                    if order_state['result'] == 'ERROR':
                        payment_status = 'not_processed'
                        payment_details = {
                            'error_cause': order_state['error']['cause'],
                            'error_explanation': order_state['error']['explanation'],
                            'result': order_state['result'],
                            'state': payment_status,
                            'failed_on': date_time_obj,

                        }

                        order_id.write(payment_details)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()

                    _logger.error("Exception in Get Order State NBE %s, %s, %s,%s for order_id %s", e, exc_type,
                                  exc_obj, exc_tb, order_id.name)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error("Exception in Get Order State NBE  %s, %s, %s,%s for order_id %s", e, exc_type,
                          exc_obj, exc_tb, order_id.name)


    def get_state_QNB(self,base_url,account_id,order_id):
        try:
            payment = PaymentQNB(account_id.integration_username, account_id.integration_password,
                                 account_id.merchant_id,
                                 order_id.name, account_id.api_url, base_url)
            order_state = payment.retrieve_order()

            if order_state["result"] == "ERROR":
                raise ValidationError(_("Error in get order state : %s", order_state["error"]["explanation"]))
            flag = 0
            # kashier status is different

            if order_state['result'] == 'SUCCESS' and order_state['status'] == 'CAPTURED':
                payment_status = 'done'
                flag = 1
            elif order_state['result'] == 'SUCCESS' and order_state['status'] in ['AUTHORIZED']:
                payment_status = 'pending'
                flag = 1
            elif order_state['result'] == 'SUCCESS' and order_state['status'] == 'AUTHENTICATION_UNSUCCESSFUL':
                payment_status = 'failed'
                flag = 1
            elif order_state['status'] == 'FAILED':
                payment_status = 'failed'
                flag = 1

            elif order_state['status'] == 'REFUNDED':
                payment_status = 'refunded'
                flag = 1
            elif order_state['status'] == 'PARTIALLY_REFUNDED':
                payment_status = 'partially_refunded'
                flag = 1
            else:
                payment_status = order_id.state

            if flag:
                datetime_str = order_state['creationTime']
                date_time_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                payment_details = {
                    'amount_charged': float(order_state.get('totalCapturedAmount', 0.0)),
                    'auth_3d_transaction_id': order_state.get('authentication', {}).get('3ds', {}).get('transactionId',
                                                                                                       "{}"),
                    'chargeback_amount': float(order_state.get('chargeback', {}).get('amount', 0.0)),
                    'chargeback_currency': order_state.get('chargeback', {}).get('currency', ""),
                    'verified_on': date_time_obj,
                    'result': order_state.get('result'),
                    'state': payment_status,
                    'authentication_status': order_state.get('authenticationStatus', ""),
                    'payment_state': order_state.get('status', "")
                }
                # print("payment_details", payment_details)
                order_id.write(payment_details)
            else:
                try:

                    date_time_obj = datetime.now()
                    if order_state['result'] == 'ERROR':
                        payment_status = 'not_processed'
                        payment_details = {
                            'error_cause': order_state['error']['cause'],
                            'error_explanation': order_state['error']['explanation'],
                            'result': order_state['result'],
                            'state': payment_status,
                            'failed_on': date_time_obj,

                        }

                        order_id.write(payment_details)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()

                    _logger.error("Exception in Get Order State QNB %s, %s, %s,%s for order_id %s", e,exc_type, exc_obj, exc_tb ,order_id.name )

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error("Exception in Get Order State QNB  %s, %s, %s,%s for order_id %s", e, exc_type, exc_obj, exc_tb,order_id.name)



    def get_state_Fawry(self,base_url,account_id,order_id):
        # todo
        _logger.info("Fawry integration is not implemented yet for transaction_id %s", order_id.name)
        return

    def get_order_state(self):

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        self.check_link_validity()
        for order_id in self:

            account_id = order_id.account_id
            bank = order_id.account_id.bank_name
            if bank == 'NBE':
                _logger.info("in get_order_state for NBE for transaction_id %s", order_id.name)
                self.get_state_NBE(base_url, account_id, order_id)

            elif bank == 'Kashier':
                _logger.info("in get_order_state for Kashier for transaction_id %s", order_id.name)

                return self.get_kashier_payment_status(base_url, account_id, order_id)


            elif bank=="QNB":
                _logger.info("in get_order_state for QNB for transaction_id %s", order_id.name)
                self.get_state_QNB(base_url, account_id, order_id)

            elif bank == "Fawry":
                _logger.info("Fawry integration is not implemented yet for transaction_id %s", order_id.name)
                self.get_state_Fawry(base_url, account_id, order_id)


            else:
                _logger.error("Unknown bank name %s for order id %s", bank , order_id.name )

    @api.constrains('amount')
    def check_amount(self):
        if self.amount <= 0.0:
            raise ValidationError(_("Order amount must be a positive number Greater than zero"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].with_company(self.company_id).next_by_code('transaction.sequence') or _('New')
        return super(Transaction, self).create(vals_list)

    def create_payment_link(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for transaction in self:
            if transaction.state == 'not_processed':
                link = base_url + '/checkout/order-pay/' + transaction.name
                transaction.payment_link = link
                transaction.link_created = datetime.now()
                transaction.link_active = True
                valid_till = transaction.link_validity

    @api.model
    def check_link_validity(self):
        order_ids = self.env['transaction'].sudo().search([("state", "not in", ["expired", "done"])])
        for order_id in order_ids:
            link_created = order_id.link_created
            valid_till = order_id.link_validity

            if link_created:
                if link_created + timedelta(hours=valid_till) <= datetime.now():

                    order_id.link_active = False
                    if not order_id.verified_on:
                        order_id.state = 'expired'
                    # else:
                    #     order_id.get_order_state()


            else:

                order_id.link_active = False
    def refund_NBE(self,base_url,account_id,order_id):
        try:
            payment = Payment(account_id.integration_username, account_id.integration_password,
                              account_id.merchant_id,
                              order_id.name, account_id.api_url, base_url)
            refund_response = payment.refund_order(order_id, order_id.refunded_amount)

            if refund_response:
                if 'error' in refund_response:
                    order_id.write({
                        "refund_result": refund_response["result"],
                        "refund_try": True,
                        "refund_error": refund_response["error.cause"],
                        "refund_error_explanation": refund_response["error.explanation"],

                    })
                else:
                    datetime_str = refund_response['order.lastUpdatedTime']
                    date_time_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                    order_id.write({
                        "order_amount": float(refund_response["order.amount"]),
                        "order_chargeback_amount": float(refund_response["order.chargeback.amount"]),
                        "order_last_updated_time": date_time_obj,
                        "last_status": refund_response["order.status"],
                        "state": 'refunded' if refund_response["order.status"] == "REFUNDED" else order_id.state,
                        "order_refunded_amount": float(refund_response["order.totalRefundedAmount"]),
                        "response_gateway_code": refund_response["response.gatewayCode"],
                        "refund_result": refund_response["result"],
                        "refund_try": True,
                    })
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error("Exception in Refund NBE %s, %s, %s,%s for order_id %s", e,e, exc_type, exc_obj, exc_tb,order_id.name)
            return True

    def refund_Kashier(self,base_url,account_id,order_id):
        try:
            payment = Kashier(account_id.integration_username, account_id.integration_password,
                              account_id.secret_key, account_id.merchant_id,
                              account_id.api_url, base_url, order_id.session_id)
            if order_id.refunded_amount <= 0.0:
                raise ValidationError(_("Refund amount must be a positive number Greater than zero"))
            refund_response = payment.refund_order(order_id, order_id.refunded_amount)
            _logger.info("refund_response from Kashier %s", refund_response)
            if refund_response:
                if refund_response['response']['result'] == 'SUCCESS':
                    order_state = payment.retrieve_order()
                    if order_state['message'] == 'success' and order_state['data']['status'] == 'REFUNDED':
                        payment_status = 'refunded'
                    elif order_state['message'] == 'success' and order_state['data']['status'] == 'PARTIALLY_REFUNDED':
                        payment_status = 'partially_refunded'
                    else:
                        payment_status = order_id.state

                    order_id.write({
                        "order_amount": float(order_state['data']['amount']),
                        "order_last_updated_time": datetime.now(),
                        "last_status": order_state['data']['status'],
                        "state": payment_status,
                        "order_refunded_amount": float(order_state['data']['refundedAmount']),
                        "response_gateway_code": refund_response['response']['result'],
                        "refund_result": refund_response['response']['result'],
                        "refund_try": True,
                        "payment_status": order_state['data']['status'],

                    })
                    return {
                        'effect': {
                            'fadeout': 'slow',
                            'message': f'Refunded Processed Successfully',
                            'type': 'rainbow_man',
                        }
                    }
                else:
                    _logger.error("Success response Failed from Kashier for order_id %s ,the refund response %s", order_id,refund_response)
            else:
                _logger.error("No Refund response from Kashier for order_id %s", order_id)
                return True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error("Exception in Refund Kashier %s, %s, %s,%s for order_id %s", e,e, exc_type, exc_obj, exc_tb,order_id.name)
            return True

    def refund_QNB(self,base_url,account_id,order_id):
        try:
            payment = PaymentQNB(account_id.integration_username, account_id.integration_password,
                                 account_id.merchant_id,
                                 order_id.name, account_id.api_url, base_url)

            refund_response = payment.refund_order(order_id, order_id.refunded_amount)

            if refund_response:
                if 'error' in refund_response:
                    order_id.write({
                        "refund_result": refund_response["result"],
                        "refund_try": True,
                        "refund_error": refund_response["error"]["cause"],
                        "refund_error_explanation": refund_response["error"]["explanation"],
                    })


                else:

                    datetime_str = refund_response['order']['lastUpdatedTime']
                    date_time_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                    order_id.write({
                        "order_amount": float(refund_response["order"]["amount"]),
                        "order_chargeback_amount": float(refund_response["order"]["chargeback"]["amount"]),
                        "order_last_updated_time": date_time_obj,
                        "last_status": refund_response["order"]["status"],
                        "state": 'refunded' if refund_response["order"]["status"] == "REFUNDED" else order_id.state,
                        "order_refunded_amount": float(refund_response["order"]["totalRefundedAmount"]),
                        "response_gateway_code": refund_response["response"]["gatewayCode"],
                        "refund_result": refund_response["result"],
                        "refund_try": True,
                    }
                    )
            else:
                _logger.error("No Refund response from QNB for order_id %s", order_id)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error("Error in refund QNB %s %s %s  , %s for order_id %s", exc_type, exc_obj, exc_tb,e, order_id)

    def refund_Fawry(self,base_url,account_id,order_id):
        # todo
        _logger.info("Fawry integration is not implemented yet for transaction_id %s", order_id.name)
        return


    def refund_transaction(self):

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for order_id in self:

            account_id = order_id.account_id
            bank = account_id.bank_name
            if bank == 'NBE':
                self.refund_NBE(base_url, account_id, order_id)
            elif bank == 'Kashier':
                self.refund_Kashier( base_url, account_id, order_id)

            elif bank == 'QNB':
                self.refund_QNB(base_url, account_id, order_id)


            elif bank == 'Fawry':
                self.refund_Fawry(base_url, account_id, order_id)
            else:
                _logger.error("Unknown bank name %s for order id %s", bank, order_id.name)

