from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WizardSaleCommission(models.TransientModel):
    _name = 'wizard_sale_commission'
    _description = '''Assistant for commission list.'''

    start_date = fields.Date(
        required=True,
    )
    end_date = fields.Date(
        required=True,
    )
    row_ids = fields.One2many(
        comodel_name='wizard_sale_commission.row',
        inverse_name='wizard_id',
        string='Rows',
        readonly=True,
    )

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date > record.end_date:
                raise ValidationError(_('End date must be greater than start date.'))

    @api.multi
    def get_commissions(self):
        '''Compute commission rows'''
        self.row_ids.unlink()
        for user in self.env['res.users'].search([]):
            self.row_ids += self.env['wizard_sale_commission.row'].create({
                'wizard_id': self.id,
                'user_id': user.id,
            })
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
