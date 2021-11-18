from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class ResUser_HubSpot(models.Model):

    _inherit = "res.users"

    hubspot_user_id = fields.Char("HubSpot User Id")
    hubspot_user_imported = fields.Boolean(default=False, string="HubSpot es Importado")
    hubspot_crm_id = fields.Many2one('hubspot.crm', string="HubSpot Id")


    def get_user_data_from_hubspot(self, hubspot_crm, hubspot_user_id):
        self._cr.commit()
        try:
            user = False
            querystring = { "idProperty":"id","archived":"false" }
            response_status, response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("GET",("owners/%s" % hubspot_user_id), querystring)
            if response_status:
                user = self.env['res.users'].search([('hubspot_user_id', '=', response_data.get('id'))], limit=1)
                if not user:
                    user = self.env['res.users'].search([('login', '=', response_data.get('email')),('groups_id','=',8)], limit=1)
            return user
        except Exception as e:
            return False

