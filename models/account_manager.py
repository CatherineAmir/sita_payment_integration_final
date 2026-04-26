# -*- coding: utf-8 -*-

from odoo import models, fields, api


class account_manager(models.Model):
    "account manger model"
    _name = 'account_manager'
    _inherit = ["mail.thread"]
    _description = 'Account Manager'

    name = fields.Char(string='Account Name',compute='_compute_name',store=True)
    company_id=fields.Many2one('res.company',required=True, readonly=False, default=lambda self: self.env.company,tracking=True)
    currency_id=fields.Many2one('res.currency',required=True, readonly=False,tracking=True,default=lambda self :  self.env.company.currency_id)
    integration_username=fields.Char(string='API User Name',tracking=True,compute='compute_api_user_name',store=True)
    integration_password=fields.Char(string='API User Password',required=True,tracking=True)
    merchant_name=fields.Char(string='Merchant Name',required=True,tracking=True)
    merchant_id=fields.Char(string='Merchant ID',required=True,tracking=True)
    bank_name = fields.Selection(string='Bank Name', required=True, selection=[('NBE', 'NBE'), ("QNB", "QNB"),("Kashier","Kashier"),("Fawry","Fawry")], tracking=True)
    bank_logo = fields.Binary(string='Bank Logo', required=False)
    api_url = fields.Selection(selection=[
        ('https://test-nbe.gateway.mastercard.com/api/nvp/version/65', 'Test NBE'),
        ('https://nbe.gateway.mastercard.com/api/nvp/version/65', 'LIVE NBE'),
        ('https://qnbalahli.test.gateway.mastercard.com/', 'TEST QNB'),
        ('https://qnbalahli.gateway.mastercard.com/', 'LIVE QNB'),
        ('https://test-api.kashier.io/v3/', 'TEST KASHIER'),
        ('https://api.kashier.io/v3/', 'LIVE KASHIER'),
        ("",""),
        ("","")


    ], default='https://test-nbe.gateway.mastercard.com/api/nvp/version/65', required=False, tracking=True)

    secret_key=fields.Char(string='Secret Key')
    active=fields.Boolean(string='Active', default=True, tracking=True)

    @api.depends('company_id','currency_id')
    def _compute_name(self):
        if self.company_id and self.currency_id:
            self.name=self.company_id.name +" " + self.currency_id.name
        else :
            self.name=''


    @api.depends('merchant_id')
    def compute_api_user_name(self):
        if self.merchant_id:
            self.integration_username='merchant.'+self.merchant_id
        else:
            self.merchant_id=False







