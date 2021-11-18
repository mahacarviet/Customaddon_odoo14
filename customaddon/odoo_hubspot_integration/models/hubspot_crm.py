import datetime
import json
import logging
import time
from odoo import models, fields, api, _
from requests import request

_logger = logging.getLogger("hubSpot")

class hubspotPipelines(models.Model):

    _name = "hubspot.pipeline"
    _description = "Hubspot Pipeline"

    pipeline_id = fields.Char("Pipeline Id", required=True)
    stage_win = fields.Char("Estapa ganada", required=True)
    percent_incomplete = fields.Char("Invoiced < 100%")
    percent_complete = fields.Char("Invoiced 100%")
    company_id = fields.Many2one('res.company', string="Compañia", required=True)
    hubspot_crm_id = fields.Many2one('hubspot.crm', string='Hubspot CRM', required=True)

class hubspotCredentailDetails(models.Model):
    
    _name = "hubspot.crm"
    _description = "HubSpot CRM"
    
    name = fields.Char("Nombre", required=True)
    hubspot_api_key = fields.Char("HubSpot API Key", required=True, help="Go in the hubspot back office and get Key.")

    contact_crud =  fields.Boolean(string="Crear y Modificar inmediatamente", default=True)
    product_crud =  fields.Boolean(string="Crear y Modificar inmediatamente", default=True)
    product_create =  fields.Boolean(string="Crear al importar", default=True)
    sale_import = fields.Boolean(string="Importar Ventas", default=True)
    
    pipeline = fields.One2many("hubspot.pipeline", "hubspot_crm_id", string="Pipelines")

    def create_hubspot_operation(self, operation, operation_type, hubspot_crm_id, log_message):
        vals = {
            'hubspot_operation': operation,
            'hubspot_operation_type': operation_type,
            'hubspot_crm_id': hubspot_crm_id and hubspot_crm_id.id,
            'hubspot_message': log_message,
        }
        operation_id = self.env['hubspot.operation'].create(vals)
        return operation_id

    def create_hubspot_operation_detail(self, operation, operation_type, req_data, response_data, operation_id, fault_operation=False, process_message=False):
        vals = {
            'hubspot_operation': operation,
            'hubspot_operation_type': operation_type,
            'hubspot_request_message': '{}'.format(req_data),
            'hubspot_response_message': '{}'.format(response_data),
            'operation_id': operation_id.id,
            'fault_operation': fault_operation,
            'process_message': process_message,
        }
        operation_detail_id = self.env['hubspot.operation.details'].create(vals)
        return operation_detail_id

    def send_get_request_from_odoo_to_hubspot(self, action, api_url, querystring={}, payloadstring={}):
        try:
            url = "https://api.hubapi.com/crm/v3/%s" % (api_url)
            headers = {
                'accept': "application/json",
                'content-type': "application/json"
            }
            #headers = {'accept': 'application/json'}
            querystring["hapikey"] = self.hubspot_api_key
            payloadstring = json.dumps(payloadstring)

            response_data = request(method=action, url=url, headers=headers, params=querystring, data=payloadstring)
            if response_data.status_code in [200, 201]:
                result = response_data.json()
                _logger.info("hubspot API Response Data (%s): %s" % (url, result))
                return True, result
            else:
                _logger.info("hubspot API Response Data (%s): %s" % (url, response_data.text))
                return False, response_data.text
        except Exception as e:
            _logger.info("hubspot API Response Data : %s" % (e))
            return False, e

    def action_product_import(self):
        Producto_obj = self.env['product.template']
        Producto_obj.hubsport_to_odoo_import_product_all(self)
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Productos importados exitosamente',
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }

    def action_product_export(self):
        Producto_obj = self.env['product.template']
        Producto_obj.hubsport_to_odoo_export_product_all(self)
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Productos exportados exitosamente',
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }

    def action_sale_import(self):
        sale_obj = self.env['sale.order']
        sale_obj.hubspot_to_odoo_import_orders(self)
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Ventas exportadas exitosamente',
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }
    


    def convert_date_iso_format(self, dt_str):
        dt, _, us = dt_str.partition(".")
        if us == '':
            dt = dt.replace('Z','')
            us = "0Z"
        dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
        us = int(us.rstrip("Z"), 10)
        return dt + datetime.timedelta(microseconds=us)



    def auto_sincronize_hubspot_odoo(self):
        if self == self.env['hubspot.crm']:
            data = self.env['hubspot.crm'].search([], limit=1)
            self.env['sale.order'].hubspot_to_odoo_import_orders(data)
        else:
            self.env['sale.order'].hubspot_to_odoo_import_orders(self)

    def sincronize_product_hubspot_odoo(self):
        self.env['product.template'].hubsport_to_odoo_import_product_all(self)
        # time.sleep(5)
        # self.env['product.template'].hubsport_to_odoo_export_product_all(self)  YA NO EXPORTAR A HUBSPOT