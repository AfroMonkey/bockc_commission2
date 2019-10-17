from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    commission_percentage = fields.Float(
    )
    commission = fields.Monetary(
    )
    commissionable_amount = fields.Monetary(
    )
    commissioned = fields.Boolean(default=False)
    fully_paid = fields.Boolean(
        compute='_get_fully_paid'
    )
    last_payment = fields.Date(
        compute='_get_last_payment'
    )
    gp_percentage = fields.Float(
        compute='_get_gp_percentage',
    )

    @api.depends('invoice_ids')
    def _get_fully_paid(self):
        for record in self:
            record.fully_paid = record.invoice_ids and all(invoice.state == 'paid' for invoice in record.invoice_ids)

    @api.depends('invoice_ids')
    def _get_last_payment(self):
        for record in self:
            payments = []
            for invoice in record.invoice_ids:
                payments.extend(invoice._get_payments_vals())
            payments.sort(key=lambda payment: payment['date'])
            if payments:
                record.last_payment = payments[-1]['date']

    @api.depends('amount_untaxed', 'margin')
    def _get_gp_percentage(self):
        for record in self:
            record.gp_percentage = 100 * record.margin / record.amount_untaxed if record.amount_untaxed else 0

    @api.onchange('gp_percentage')
    def _check_gp_percentage(self):
        settings = self.env['res.config.settings'].default_get('')
        minimal_gp = settings['minimal_gp_percentage']
        if self.amount_untaxed and self.gp_percentage < minimal_gp:
            return {
                'warning': {
                    'title': _('Minimal GP'),
                    'message': _('You are below the minimum required GP%% on this order. If you proceed you will not receive commission on this sale!'),
                }
            }
