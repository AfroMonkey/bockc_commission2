from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    minimal_gp_percentage = fields.Float(
        config_parameter='bockc_commission.minimal_gp',
        string=_('Minimal GP %'),
    )
