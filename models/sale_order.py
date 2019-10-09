from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    commission_percentage = fields.Float(
    )
    commission = fields.Monetary(
    )
    commissioned = fields.Boolean(default=False)
