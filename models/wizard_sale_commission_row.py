from odoo import api, fields, models, _


class WizardSaleCommissionRow(models.TransientModel):
    _name = 'wizard_sale_commission.row'

    wizard_id = fields.Many2one(
        comodel_name='wizard_sale_commission',
        required=True,
        string='',
    )
    start = fields.Date(
        related='wizard_id.start'
    )
    end = fields.Date(
        related='wizard_id.end'
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        required=True,
        string='Salesman',
    )
    account_payment_ids = fields.Many2many(
        comodel_name='account.payment',
        string='Sales',
        compute='_get_account_payment_ids',
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        default=lambda self: self.env.ref('base.main_company').currency_id.id,
        store=False,
    )
    total_sales = fields.Monetary(
        currency_field='currency_id',
        compute='_get_total_sales',
    )
    sales_target = fields.Monetary(
        related='user_id.sales_target',
    )
    compliance_percentage = fields.Float(
        compute='_get_compliance_percentage',
    )
    bonus_percentage = fields.Float(
        compute='_get_bonus_percentage',
    )
    commission = fields.Monetary(
        currency_field='currency_id',
        compute='_get_commission',
    )

    @api.depends('start', 'end', 'user_id')
    def _get_account_payment_ids(self):
        for r in self:
            AccountPayment = self.env['account.payment']
            r.account_payment_ids = AccountPayment.search([
                ('invoice_ids.user_id', '=', r.user_id.id),
                ('state', '=', 'posted'),
                ('payment_date', '>=', r.start),
                ('payment_date', '<=', r.end),
            ])
    
    @api.depends('account_payment_ids')
    def _get_total_sales(self):
        for r in self:
            r.total_sales = sum(payment.amount for payment in r.account_payment_ids)
    
    @api.depends('total_sales', 'sales_target')
    def _get_compliance_percentage(self):
        for r in self:
            r.compliance_percentage = r.sales_target and 100 * r.total_sales / r.sales_target or 0

    @api.depends('compliance_percentage')
    def _get_bonus_percentage(self):
        for r in self:
            if r.compliance_percentage > 75.0:
                # TODO formula
                r.bonus_percentage = r.compliance_percentage
            else:
                r.bonus_percentage = 0

    @api.depends('bonus_percentage', 'total_sales')
    def _get_commission(self):
        for r in self:
            r.commission = r.total_sales * r.bonus_percentage / 100
