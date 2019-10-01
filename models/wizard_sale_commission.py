from odoo import api, fields, models, _

class WizardSaleCommission(models.TransientModel):
    _name = 'wizard_sale_commission'

    start = fields.Date(
        required=True,
    )
    end = fields.Date(
        required=True,
    )

    @api.multi
    def get_commissions(self):
        pass # TODO
