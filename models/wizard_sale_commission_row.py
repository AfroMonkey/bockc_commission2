from odoo import api, fields, models


class WizardSaleCommissionRow(models.TransientModel):
    _name = 'wizard_sale_commission.row'
    _description = '''Relation between salesperson and their commissions.'''

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
    sale_order_paid_ids = fields.Many2many(
        comodel_name='sale.order',
        string='Sales Paid',
        compute='_get_sale_order_paid_ids',
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
        compute='_get_sales_target',
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
    commission_estimated = fields.Monetary(
        currency_field='currency_id',
        compute='_get_commission_estimated',
    )
    margin = fields.Monetary(
        currency_field='currency_id',
        compute='_get_margin',
    )
    all_sale_order_ids = fields.One2many(
        related='user_id.sale_order_ids2',
    )

    @api.depends('user_id', 'start_date', 'end_date')
    def _get_sales_target(self):
        for record in self:
            sale_target = record.user_id.sales_target_ids.search([
                ('user_id', '=', record.user_id.id),
                ('start_date', '=', record.start_date),
                ('end_date', '=', record.end_date),
            ])
            record.sales_target = sale_target.target if sale_target else 0

    @api.depends('start_date', 'end_date', 'user_id')
    def _get_sale_order_ids(self):
        for record in self:
            SaleOrder = self.env['sale.order']
            record.sale_order_ids = SaleOrder.search([
                '|',
                ('user_id', '=', record.user_id.id),
                ('team_id', 'in', record.user_id.led_team_ids.ids),
                ('confirmation_date', '>=', record.start_date),
                ('confirmation_date', '<', record.end_date),
                # ('invoice_status', '=', 'invoiced'),
            ])

    @api.depends('sale_order_ids')
    def _get_sale_order_paid_ids(self):
        for record in self:
            SaleOrder = self.env['sale.order']
            orders = SaleOrder.search([
                '|',
                ('user_id', '=', record.user_id.id),
                ('team_id', 'in', record.user_id.led_team_ids.ids),
                # ('invoice_status', '=', 'invoiced'),
            ])
            record.sale_order_paid_ids = orders.filtered(lambda order: order.fully_paid and order.last_payment >= record.start_date and order.last_payment < record.end_date)

    @api.depends('sale_order_ids')
    def _get_total_sales(self):
        for record in self:
            record.total_sales = sum(order.amount_untaxed for order in record.sale_order_ids)

    @api.depends('total_sales', 'sales_target')
    def _get_compliance_percentage(self):
        for record in self:
            record.compliance_percentage = record.sales_target and 100 * record.total_sales / record.sales_target or 0

    @api.depends('total_sales', 'sales_target')
    def _get_margin(self):
        for record in self:
            record.margin = record.total_sales - record.sales_target

    @api.depends('compliance_percentage')
    def _get_bonus_percentage(self):
        for record in self:
            commission_plan = record.user_id.commission_plan_id
            if record.compliance_percentage >= commission_plan.minimal_percentage:
                record.bonus_percentage = commission_plan.initial_commission
                for row in commission_plan.row_ids:
                    if record.margin >= row.margin and record.bonus_percentage < row.percentage:
                        record.bonus_percentage = row.percentage
            else:
                record.bonus_percentage = 0
            for order in record.sale_order_ids:
                amount = sum(payment.amount for invoice in order.invoice_ids for payment in invoice.payment_ids)
                settings = self.env['res.config.settings'].default_get('')
                minimal_gp = settings['minimal_gp_percentage']
                order.write({
                    'commission_percentage': record.bonus_percentage,
                    'commission': amount * record.bonus_percentage / 100 if order.fully_paid and order.gp_percentage >= minimal_gp else 0,
                    'commissioned': True,
                })

    @api.depends('sale_order_paid_ids')
    def _get_commission(self):
        for record in self:
            record.commission = sum([order.commission for order in record.sale_order_paid_ids])

    @api.depends('bonus_percentage', 'total_sales')
    def _get_commission_estimated(self):
        for record in self:
            record.commission_estimated = record.total_sales * record.bonus_percentage / 100
