from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ResUsers(models.Model):
    _inherit = 'res.users'

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        default=lambda self: self.env.ref('base.main_company').currency_id.id,
    )
    sales_target = fields.Monetary(
        currency_field='currency_id',
    )
    sale_order_ids2 = fields.One2many(
        string=u'Sale Orders',
        comodel_name='sale.order',
        inverse_name='user_id',
    )
    

    @api.constrains('sales_target')
    def _check_sales_target_no_negative(self):
        for r in self:
            if r.sales_target < 0:
                raise ValidationError(_('The sale target can not be negative.'))
