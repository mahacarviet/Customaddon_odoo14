from odoo import fields, models, api
from odoo.http import request
import logging
import time

_logger = logging.getLogger(__name__)

class ResPartner_HubSpot(models.Model):

    _inherit = "res.partner"

    hubspot_contact_id = fields.Char("Id HubSpot")
    hubspot_contact_synchronized = fields.Boolean(default=False, string="HubSpot esta Sincronizado")
    hubspot_write_date = fields.Datetime(string="HubSpot Fecha Modificación")


    @api.model_create_multi
    def create(self, vals_list):
        partners = super(ResPartner_HubSpot, self).create(vals_list)
        ################################################################
        hubspot_crm = self.env['hubspot.crm'].search([('id','!=',False)], limit=1)
        if hubspot_crm.contact_crud and request.params and request.params.get('method','') == 'create' and request.params.get('model','') == 'res.partner':
            self._cr.commit()
            try:
                self.contact_sincronize(partners)
            except Exception as e:
                _logger.info("Error al exportar hacia hubspot {}".format(e))
        ################################################################
        return partners


    def write(self, vals):
        partners = super(ResPartner_HubSpot, self).write(vals)
        ################################################################
        _logger.info(self._context)
        hubspot_crm = self.env['hubspot.crm'].search([('id','!=',False)], limit=1)
        if hubspot_crm.contact_crud and request.params and request.params.get('method','') == 'write' and request.params.get('model','') == 'res.partner':
            self._cr.commit()
            try:
                if partners == True:
                    contact = self.env['res.partner'].search([('id','=',self.id)])
                    self.contact_sincronize(contact)
            except Exception as e:
                _logger.info("Error al exportar hacia hubspot {}".format(e))
        ################################################################
        return partners


    def contact_sincronize(self, contact):
        try:
            hubspot_crm = self.env['hubspot.crm'].search([('id','!=',False)], limit=1)
            if contact.is_company == True:
                hubspot_operation = hubspot_crm.create_hubspot_operation('contact_company','export',hubspot_crm,'Procesando...')
                payload = {
                    "properties":{
                        "name": contact.name,
                        "phone": contact.phone or "",
                        "website": contact.website or "",
                        "address": contact.street or "",
                        "city": contact.city or "",
                        "country": contact.country_id.name if contact.country_id else "",
                        "state": contact.state_id.name if contact.state_id else "",
                        "zip": contact.zip or "",
                        "domain": contact.website or "",
                        "industry": contact.category_id.name or ""
                    }
                }
                                
                if not contact.hubspot_contact_id:
                    response_status, response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("POST","objects/companies",{}, payload)
                else:
                    response_status, response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("PATCH","objects/companies/%s" % contact.hubspot_contact_id,{}, payload)
                
                if response_status:
                    fecha_modificacion = response_data.get('properties').get('hs_lastmodifieddate')
                    fecha_modificacion = hubspot_crm.convert_date_iso_format(fecha_modificacion)

                    super(ResPartner_HubSpot, contact).write({
                        'hubspot_contact_id': response_data.get('id'),
                        'hubspot_contact_synchronized': True,
                        'hubspot_write_date': fecha_modificacion,
                    })
                    process_message = "Compañia creado en hubspot: {}".format(contact.name)
                    hubspot_crm.create_hubspot_operation_detail('contact_company', 'export', True, response_data, hubspot_operation, False, process_message)
                    hubspot_operation.write({'hubspot_message': "El proceso de exportación se realizo correctamente"})
                else:
                    process_message = "Error en la exportación de la compañia {}".format(contact.name)
                    hubspot_crm.create_hubspot_operation_detail('contact_company','export',response_data,process_message,hubspot_operation,True,process_message)
                    hubspot_operation.write({'hubspot_message': "El proceso aún no está completo, ocurrio un Error! %s" % (process_message)})
            else:
                hubspot_operation = hubspot_crm.create_hubspot_operation('contact','export',hubspot_crm,'Procesando...')
                payload = {
                    "properties":{
                        "firstname": contact.name,
                        "lastname": "",
                        "email": contact.email or "",
                        "phone": contact.phone or "",
                        "mobilephone": contact.mobile or "",
                        "website": contact.website or "",
                        "address": contact.street or "",
                        "city": contact.city or "",
                        "country": contact.country_id.name if contact.country_id else "",
                        "state": contact.state_id.name if contact.state_id else "",
                        "zip": contact.zip or "",
                        "company": contact.company_name or ""
                        }
                    }
                                
                if not contact.hubspot_contact_id:
                    response_status, response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("POST","objects/contacts",{}, payload)
                else:
                    response_status, response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("PATCH","objects/contacts/%s" % contact.hubspot_contact_id,{}, payload)

                if response_status:
                    fecha_modificacion = response_data.get('properties').get('lastmodifieddate')
                    fecha_modificacion = hubspot_crm.convert_date_iso_format(fecha_modificacion)

                    super(ResPartner_HubSpot, contact).write({
                        'hubspot_contact_id': response_data.get('id'),
                        'hubspot_contact_synchronized': True,
                        'hubspot_write_date': fecha_modificacion,
                    })
                    process_message = "Contacto creado en hubspot: {}".format(contact.name)
                    hubspot_crm.create_hubspot_operation_detail('contact', 'export', True, response_data, hubspot_operation, False, process_message)
                    hubspot_operation.write({'hubspot_message': "El proceso de exportación se realizo correctamente"})
                else:
                    process_message = "Error en la exportación del contacto {}".format(contact.name)
                    hubspot_crm.create_hubspot_operation_detail('contact','export',response_data,process_message,hubspot_operation,True,process_message)
                    hubspot_operation.write({'hubspot_message': "El proceso aún no está completo, ocurrio un Error! %s" % (process_message)})
        except Exception as e:
            process_message="Error en la respuesta de importación de contacto {}".format(e)
            _logger.info(process_message)
            hubspot_crm.create_hubspot_operation_detail('contact_company','import',response_data,process_message,hubspot_operation,True,process_message)
            hubspot_operation.write({'hubspot_message': "El proceso aún no está completo, ocurrio un Error! %s" % (e)})
        self._cr.commit()
    


    def get_company_data_from_hubspot(self, hubspot_operation, hubspot_crm, hubspot_company_id):
        try:
            payload = { "properties":["name","phone","domain","address","zip","cif"] }
            
            response_status, response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("GET",("objects/companies/%s" % hubspot_company_id), payload)
            if response_status:
                company = self.env['res.partner'].search([('hubspot_contact_id', '=', response_data.get('id'))], limit=1)
                if company:
                    process_message = "Contacto empresa encontrado por hubspotId: {0}".format(company.name)
                    hubspot_crm.create_hubspot_operation_detail('contact_company', 'import', False, response_data, hubspot_operation, False, process_message)
                    return company
                else:
                    company = self.env['res.partner'].search([('is_company','=',True),('vat','=',response_data.get('properties').get('cif'))], limit=1)
                    if company:
                        super(ResPartner_HubSpot, company).write({
                            'hubspot_contact_id': response_data.get('properties').get('hs_object_id'),
                            'hubspot_contact_synchronized': True,
                        })
                        process_message = "Contacto empresa actualizada por Cif: {0}".format(company.name)
                        hubspot_crm.create_hubspot_operation_detail('contact_company', 'import', False, response_data, hubspot_operation, False, process_message)
                        return company
                    else:
                        process_message = "Contacto empresa no encontrado cif: {0}".format(response_data.get('properties').get('cif'))
                        hubspot_crm.create_hubspot_operation_detail('contact_company', 'import', False, response_data, hubspot_operation, False, process_message)
                        return False
            else:
                process_message = "Error en la respuesta de importación de contacto empresa {}".format(response_data)
                hubspot_crm.create_hubspot_operation_detail('contact_company','import','',response_data,hubspot_operation,True,process_message)
                return False
        except Exception as e:
            process_message="Error en la respuesta de importación de contacto empresa {}".format(e)
            _logger.info(process_message)
            hubspot_crm.create_hubspot_operation_detail('contact_company','import',response_data,process_message,hubspot_operation,True,process_message)

    # Funcion no utilizado
    def get_contact_data_from_hubspot(self, hubspot_operation, hubspot_crm, hubspot_contact_id):
        try:
            payload = {
                "properties":["firstname","lastname","email","phone","website","address","zip"]
            }

            response_status, response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("GET",("objects/contacts/%s" % hubspot_contact_id),payload)
            if response_status:
                
                contact = self.env['res.partner'].search([('hubspot_contact_id', '=', response_data.get('id'))], limit=1)
                if not contact:
                    contact = self.env['res.partner'].search([('is_company','=',False),('email','=',response_data.get('properties').get('email'))], limit=1)
                
                if not contact:
                    contact = super(ResPartner_HubSpot, contact).create({
                        'name': response_data.get('properties').get('firstname','') + " " + (response_data.get('properties').get('lastname','') or ''),
                        'email': response_data.get('properties').get('email',False),
                        'phone': response_data.get('properties').get('phone',False),
                        'website': response_data.get('properties').get('website',False),
                        'street': response_data.get('properties').get('address',False),
                        'zip': response_data.get('properties').get('zip',False),
                        'company_type': 'person',
                        'hubspot_contact_id': response_data.get('properties').get('hs_object_id'),
                        'hubspot_contact_synchronized': True,
                    })
                    process_message = "Contacto Creado: {0}".format(contact.name)
                else:
                    super(ResPartner_HubSpot, contact).write({
                        'name': response_data.get('properties').get('firstname','') + " " + (response_data.get('properties').get('lastname','') or ''),
                        'email': response_data.get('properties').get('email',False),
                        'phone': response_data.get('properties').get('phone',False),
                        'website': response_data.get('properties').get('website',False),
                        'street': response_data.get('properties').get('address',False),
                        'zip': response_data.get('properties').get('zip',False),
                        'company_type': 'person',
                        'hubspot_contact_id': response_data.get('properties').get('hs_object_id'),
                        'hubspot_contact_synchronized': True,
                    })
                    process_message = "Contacto Actualizada: {0}".format(contact.name)
                    
                hubspot_crm.create_hubspot_operation_detail('contact', 'import', False, response_data, hubspot_operation, False, process_message)
            else:
                process_message = "Error en la respuesta de importación de contacto {}".format(response_data)
                hubspot_crm.create_hubspot_operation_detail('contact','import','',response_data,hubspot_operation,True,process_message)
            
        except Exception as e:
            process_message="Error en la respuesta de importación de contacto {}".format(e)
            _logger.info(process_message)
            hubspot_crm.create_hubspot_operation_detail('contact','import',response_data,process_message,hubspot_operation,True,process_message)
        return contact