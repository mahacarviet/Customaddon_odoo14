
from odoo import models, fields, api
import datetime

class hubspotOperation(models.Model):
    _name = "hubspot.operation"
    _order = 'id desc'
    _inherit = ['mail.thread']
    _description = "HubSpot Operation"
    
    name = fields.Char("Nombre")
    hubspot_operation = fields.Selection([
        ('account', 'Account'),
        ('product', 'Product'),
        ('contact', 'Contact'),
        ('contact_company', 'Contact Company'),
        ('order', 'Order'),
        ('user', 'User'),
        ], string="Operación")
    hubspot_operation_type = fields.Selection([
        ('export', 'Export'),
        ('import', 'Import'),
        ('update', 'Update'),
        ('delete', 'Cancel / Delete')], string="Tipo de Operación")
    company_id = fields.Many2one("res.company", "Compañia")
    operation_ids = fields.One2many("hubspot.operation.details", "operation_id", string="Operación")
    hubspot_crm_id = fields.Many2one('hubspot.crm', string="Configuración")
    hubspot_message = fields.Char("Mensaje")

    @api.model
    def create(self, vals):
        sequence = self.env.ref("odoo_hubspot_integration.seq_hubspot_operation_detail")
        name = sequence and sequence.next_by_id() or '/'
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        if type(vals) == dict:
            vals.update({'name': name, 'company_id': company_id})
        return super(hubspotOperation, self).create(vals)


class hubspotOperationDetail(models.Model):
    _name = "hubspot.operation.details"
    _rec_name = 'operation_id'
    _order = 'id desc'
    _description = "HubSpot Operation Details"

    operation_id = fields.Many2one("hubspot.operation", string="Operación HubSpot")
    hubspot_operation = fields.Selection([
        ('account', 'Account'),
        ('product', 'Product'),#
        ('contact', 'Contact'),#
        ('contact_company', 'Contact Company'),#
        ('order', 'Order'),
        ('user', 'User')
        ], string="Operación")
    hubspot_operation_type = fields.Selection([
        ('export', 'Export'),
        ('import', 'Import'),
        ('update', 'Update'),
        ('delete', 'Cancel / Delete')
        ], string="Tipo de Operación HubSpot")
    company_id = fields.Many2one("res.company", "Company")
    hubspot_request_message = fields.Char("Request")
    hubspot_response_message = fields.Char("Response")
    fault_operation = fields.Boolean("Error Obtenido", default=False)
    process_message = fields.Char("Mensaje")

    @api.model
    def create(self, vals):
        if type(vals) == dict:
            operation_id = vals.get('operation_id')
            operation = operation_id and self.env['hubspot.operation'].browse(operation_id) or False
            company_id = operation and operation.company_id.id or self.env.user.company_id.id
            vals.update({'company_id': company_id})
        return super(hubspotOperationDetail, self).create(vals)


class hubspotCreationData(models.Model):
    _name = "hubspot.creation.log"
    _order = 'id desc'
    _description = "HubSpot Operation"
    
    partner_id = fields.Many2one('res.partner', string="Cliente")
    product_id = fields.Many2one('product.product', string="Producto")
    sale_order_id = fields.Many2one('sale.order', string="Venta")
    data_type = fields.Selection([
        ('contact', 'Contacto'),
        ('product', 'Producto')
        ], string="Tipo de dato")

    def data_create(self, partner_id=False, product_id=False, sale_order_id=False):
        self.env['hubspot.creation.log'].create({
            'partner_id': partner_id,
            'product_id': product_id,
            'sale_order_id': sale_order_id,
            'data_type': 'contact' if partner_id else 'product'
        })