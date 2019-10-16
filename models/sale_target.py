from datetime import date

from odoo import api, fields, models, _


class SaleTarget(models.Model):
    _name = 'sale.target'

    start_date = fields.Date(
        compute='_get_start_date',
        store=True,
    )
    end_date = fields.Date(
        compute='_get_end_date',
        store=True,
    )
    year = fields.Integer(
        default=fields.Date.today().year,
        required=True,
    )
    month = fields.Selection(
        [
            (1, _('January')),
            (2, _('February')),
            (3, _('March')),
            (4, _('April')),
            (5, _('May')),
            (6, _('June')),
            (7, _('July')),
            (8, _('August')),
            (9, _('September')),
            (10, _('October')),
            (11, _('November')),
            (12, _('December')),
        ],
        default=fields.Date.today().month,
        required=True,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        default=lambda self: self.env.ref('base.main_company').currency_id.id,
    )
    target = fields.Monetary(
        currency_field='currency_id',
        required=True,
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        required=True,
    )

    @api.depends('year', 'month')
    def _get_start_date(self):
        for record in self:
            record.start_date = date(record.year, record.month, 1)

    @api.depends('year', 'month')
    def _get_end_date(self):
        for record in self:
            if record.month == 12:
                record.end_date = date(record.year + 1, 1, 1)
            else:
                record.end_date = date(record.year, record.month + 1, 1)
