from odoo import fields, models, api


class Partner(models.Model):
    _inherit = 'res.partner'
    transaction_ids=fields.One2many("transaction","partner_id",auto_join=True)



