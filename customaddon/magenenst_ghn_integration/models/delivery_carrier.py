from odoo import api, fields, models, _


class DeliveryCarrrier(models.Model):
    _inherit = 'delivery.carrier'

    service = fields.Selection([
        ('1', 'Express'),
        ('2', 'Standard'),
        ('4', 'Bulky and Heavy'),  # it not ready, just for some areas
    ], string='GHN Service', required=False, default='2',
        help="Choose your GHN shipping plan (Express, Standard or Bulky and Heavy)")

    delivery_type = fields.Selection(selection_add=[('ghn_shipping', 'GHN Shipping')],
                                     ondelete={'ghn_shipping': 'cascade'})
