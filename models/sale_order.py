from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    commission_percentage = fields.Float(
    )
    commission = fields.Monetary(
    )
    
