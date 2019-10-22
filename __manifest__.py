# -*- coding: utf-8 -*-
############################################################################
#    Coded by: Moisés Navarro (https://github.com/AfroMonkey)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'BOCKC Commission',
    'version': '1.5.2',
    'author': 'Moisés Navarro',
    'website': 'https://github.com/AfroMonkey',
    'depends': [
        'sale',
        'crm',
        'sale_margin',
    ],
    'data': [
        'security/ir.model.access.csv',
        'reports/wizard_sale_commission.xml',
        'reports/wizard_sale_commission_row.xml',
        'views/res_users.xml',
        'views/sale_order.xml',
        'views/wizard_sale_commission_row.xml',
        'views/wizard_sale_commission.xml',
        'views/res_config_settings.xml',
        'views/commission_plan.xml',
    ]
}
