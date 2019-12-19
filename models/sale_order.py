from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    commission_percentage = fields.Float(
    )
    commission = fields.Float(
        compute='_get_commission_values',
    )
    commission_percentage_lead = fields.Float(
    )
    commission_lead = fields.Float(
        compute='_get_commission_lead_values',
    )
    commissionable_amount = fields.Float(
        compute='_get_commissionable_amount',
        # store=True,
    )
    fully_paid = fields.Boolean(
        compute='_get_fully_paid'
    )
    last_payment = fields.Date(
        compute='_get_last_payment'
    )
    gp_percentage = fields.Float(
        compute='_get_gp_percentage',
    )
    commission_estimated = fields.Float(
        compute='_get_commission_values',
    )
    commission_estimated_lead = fields.Float(
        compute='_get_commission_lead_values',
    )
    lead_id = fields.Many2one(
        related='team_id.user_id',
    )

    @api.depends('commission_percentage')
    def _get_commission_values(self):
        settings = self.env['res.config.settings'].default_get('')
        minimal_gp = settings['minimal_gp_percentage']
        for record in self:
            record.commission = (record.commissionable_amount * record.commission_percentage / 100
                                 if record.fully_paid and record.gp_percentage >= minimal_gp else 0)
            record.commission_estimated = record.amount_untaxed * record.commission_percentage / 100

    @api.depends('commission_percentage_lead')
    def _get_commission_lead_values(self):
        settings = self.env['res.config.settings'].default_get('')
        minimal_gp = settings['minimal_gp_percentage']
        for record in self:
            record.commission_lead = (record.commissionable_amount * record.commission_percentage_lead / 100
                                      if record.fully_paid and record.gp_percentage >= minimal_gp else 0)
            record.commission_estimated_lead = record.amount_untaxed * record.commission_percentage_lead / 100

    @api.depends('invoice_ids')
    def _get_commissionable_amount(self):
        for record in self:
            record.commissionable_amount = sum(payment.amount
                                               for invoice in record.invoice_ids
                                               for payment in invoice.payment_ids) - sum(invoice.amount_tax for invoice in record.invoice_ids)

    @api.depends('invoice_ids')
    def _get_fully_paid(self):
        for record in self:
            record.fully_paid = (all(invoice.state == 'paid' for invoice in record.invoice_ids)
                                 if record.invoice_ids else False)

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
            record.gp_percentage = (100 * record.margin / record.amount_untaxed
                                    if record.amount_untaxed else 0)

    @api.onchange('gp_percentage')
    def _check_gp_percentage(self):
        settings = self.env['res.config.settings'].sudo().default_get('')
        minimal_gp = settings['minimal_gp_percentage']
        if self.amount_untaxed and self.gp_percentage < minimal_gp:
            return {
                'warning': {
                    'title': _('Minimal GP'),
                    'message': _('You are below the minimum required GP%% on this order. If you proceed you will not receive commission on this sale!'),
                }
            }
