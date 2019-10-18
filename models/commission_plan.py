from odoo import fields, models, _


class CommissionPlanRow(models.Model):
    _name = 'commission.plan.row'
    _description = '''Relation between percentage and margin.'''

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        default=lambda self: self.env.ref('base.main_company').currency_id.id,
    )
    margin = fields.Float(
        required=True,
        string=_('Difference from Target'),
    )
    percentage = fields.Float(
        required=True,
        string=_('%'),
    )
    commission_plan_id = fields.Many2one(
        comodel_name='commission.plan',
    )


class CommissionPlan(models.Model):
    _name = 'commission.plan'
    _description = '''Table of bonus percentages.'''

    name = fields.Char(
        required=True,
    )
    minimal_percentage = fields.Float(
        required=True,
    )
    initial_commission = fields.Float(
        required=True,
    )
    row_ids = fields.One2many(
        comodel_name='commission.plan.row',
        inverse_name='commission_plan_id',
        string='Rows',
    )
