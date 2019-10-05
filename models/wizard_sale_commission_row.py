from odoo import api, fields, models, _


class WizardSaleCommissionRow(models.TransientModel):
    _name = 'wizard_sale_commission.row'

    wizard_id = fields.Many2one(
        comodel_name='wizard_sale_commission',
        required=True,
    )
    start_date = fields.Date(
        related='wizard_id.start_date'
    )
    end_date = fields.Date(
        related='wizard_id.end_date'
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        required=True,
        string='Salesman',
    )
    sale_order_ids = fields.Many2many(
        comodel_name='sale.order',
        string='Sales',
        compute='_get_sale_order_ids',
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
    margin = fields.Monetary(
        currency_field='currency_id',
        compute='_get_margin',
    )

    @api.depends('start_date', 'end_date', 'user_id')
    def _get_sale_order_ids(self):
        for r in self:
            SaleOrder = self.env['sale.order']
            orders = SaleOrder.search([
                ('user_id', '=', r.user_id.id),
                ('confirmation_date', '>=', r.start_date),
                ('confirmation_date', '<=', r.end_date),
                ('invoice_status', '=', 'invoiced'),
            ])
            r.sale_order_ids = orders.filtered(lambda order: all(invoice.state == 'paid' for invoice in order.invoice_ids))
    
    @api.depends('sale_order_ids')
    def _get_total_sales(self):
        for r in self:
            r.total_sales = sum(order.amount_untaxed for order in r.sale_order_ids)
    
    @api.depends('total_sales', 'sales_target')
    def _get_compliance_percentage(self):
        for r in self:
            r.compliance_percentage = r.sales_target and 100 * r.total_sales / r.sales_target or 0
    
    @api.depends('total_sales', 'sales_target')
    def _get_margin(self):
        for r in self:
            r.margin = r.total_sales - r.sales_target

    @api.depends('compliance_percentage')
    def _get_bonus_percentage(self):
        for r in self:
            commission_plan = r.user_id.commission_plan_id
            if r.compliance_percentage >= commission_plan.minimal_percentage:
                r.bonus_percentage = commission_plan.initial_commission
                for row in commission_plan.row_ids:
                    if r.margin >= row.margin and r.bonus_percentage < row.percentage:
                        r.bonus_percentage = row.percentage
            else:
                r.bonus_percentage = 0
            for order in r.sale_order_ids:
                order.write({
                    'commission_percentage': r.bonus_percentage,
                    'commission': order.amount_untaxed * r.bonus_percentage / 100,
                })

    @api.depends('bonus_percentage', 'total_sales')
    def _get_commission(self):
        for r in self:
            r.commission = r.total_sales * r.bonus_percentage / 100
