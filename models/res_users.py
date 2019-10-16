from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    sales_target_ids = fields.One2many(
        comodel_name='sale.target',
        inverse_name='user_id',
    )
    sale_order_ids2 = fields.One2many(
        string=u'Sale Orders',
        comodel_name='sale.order',
        inverse_name='user_id',
    )
    commission_plan_id = fields.Many2one(
        comodel_name='commission.plan',
        required=True,
        string=_('Commission plan'),
    )
    led_team_ids = fields.One2many(
        comodel_name='crm.team',
        inverse_name='user_id',
    )
