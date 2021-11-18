from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class ProjectProject_HubSpot(models.Model):
    
    _inherit = "project.project"

    hubspot_so_id = fields.Char("Id HubSpot")
    x_compute = fields.Char("Computar", compute="compute_get_hubspot_id")

    def compute_get_hubspot_id(self):
        for record in self:
            record.hubspot_so_id = ''
            record.x_compute = ''
            if record.sale_order_id and record.sale_order_id.hubspot_order_id:
                record.hubspot_so_id = record.sale_order_id.hubspot_order_id
        