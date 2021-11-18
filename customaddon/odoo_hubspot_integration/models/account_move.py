import logging

from datetime import datetime, timedelta
from odoo import fields, models, api
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

_logger = logging.getLogger("hubspot")


class AccountMove_HubSpot(models.Model):
    
    _inherit = "account.move"

    def action_post(self):
        toreturn = super(AccountMove_HubSpot, self).action_post()

        sale = self.env['sale.order'].search([('name','=',self.invoice_origin)])
        if sale.hubspot_order_id:
            amount_total = 0
            account_move = self.env['account.move'].search([('invoice_origin','=',self.invoice_origin)])
            for data in account_move:
                amount_total = amount_total + data.amount_total

            if sale.amount_total >= amount_total:
                self.update_hubspot_percent(sale, sale.hubspot_pipeline_id.percent_incomplete)
            else:
                self.update_hubspot_percent(sale, sale.hubspot_pipeline_id.percent_complete)

        return toreturn

    def update_hubspot_percent(self, sale, stage):
        if stage:
            hubspot_crm = self.env['hubspot.crm'].search([('id','!=',False)], limit=1)
            hubspot_operation = hubspot_crm.create_hubspot_operation('order','export',hubspot_crm,'Procesando...')

            payload = {
                "properties":{
                    "dealstage": stage
                }
            }
                            
            response_status, response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("PATCH","objects/deals/%s" % sale.hubspot_order_id,{}, payload)
            process_message = "Negocio actualizado en hubspot: {}".format(sale.name)
            hubspot_operation and hubspot_operation.write({'hubspot_message': "¡El proceso se completó con éxito!"})
            