from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder_HubSpot(models.Model):
    
    _inherit = "purchase.order"

    hubspot_so_id = fields.Char("Id HubSpot")
    x_compute = fields.Char("Computar", compute="compute_get_hubspot_id")

    def compute_get_hubspot_id(self):
        for record in self:
            record.hubspot_so_id = ''
            record.x_compute = ''
            if record.origin:
                sale = self.env['sale.order'].search([('name','=',record.origin)])
                record.hubspot_so_id = sale.hubspot_order_id
