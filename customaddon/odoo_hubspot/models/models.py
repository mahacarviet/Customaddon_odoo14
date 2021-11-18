from odoo import _, api, fields, models, modules, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError
from datetime import datetime
import datetime
import time
import requests
import json
import urllib
import logging

_logger = logging.getLogger(__name__)


class Integration(models.TransientModel):
    _inherit = 'res.config.settings'

    hubspot_key = fields.Char('Hubspot Key')
    company = fields.Boolean('Company', strore=True)
    contact = fields.Boolean('Contact', strore=True)
    deal = fields.Boolean('Deal', strore=True)

    def set_values(self):
        res = super(Integration, self).set_values()
        self.env['ir.config_parameter'].set_param('odoo_hubspot.hubspot_key', self.hubspot_key)
        self.env['ir.config_parameter'].set_param('odoo_hubspot.company', self.company)
        self.env['ir.config_parameter'].set_param('odoo_hubspot.contact', self.contact)
        self.env['ir.config_parameter'].set_param('odoo_hubspot.deal', self.deal)
        return res

    @api.model
    def get_values(self):
        res = super(Integration, self).get_values()
        icpsudo = self.env['ir.config_parameter'].sudo()
        hubspot_keys = icpsudo.get_param('odoo_hubspot.hubspot_key')
        companies = icpsudo.get_param('odoo_hubspot.company')
        contacts = icpsudo.get_param('odoo_hubspot.contact')
        deals = icpsudo.get_param('odoo_hubspot.deal')
        res.update(
            hubspot_key=hubspot_keys,
            company=companies,
            contact=contacts,
            deal=deals,
        )
        return res

    def hubspot_api_key(self):
        try:
            if not self.hubspot_key:
                raise ValidationError('Please! Enter Credentials, something is missing...')
            else:
                response = requests.get(
                    'https://api.hubapi.com/contacts/v1/lists/all/contacts/all?hapikey=' + self.hubspot_key + '&count=5000',
                    headers={
                        'Accept': 'application/json',
                        'connection': 'keep-Alive'
                    })
                response = json.loads(response.content.decode('utf-8'))
                if 'status' in response and response['status'] == 'error':
                    raise ValidationError(
                        'Invalid Credentials . Please! Check your credential and regenerate the code and try again!')
                else:
                    message_id = self.env['message.wizard'].create({
                        'message': _("Hubspot API key successfully stored")
                    })
                    return {
                        'name': _('Successfull'),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'message.wizard',
                        'res_id': message_id.id,
                        'target': 'new'
                    }
        except Exception as e:
            _logger.error(e)
            raise ValidationError(_(str(e)))


class CustomAttachment(models.Model):
    _inherit = 'ir.attachment'

    hubspot_id = fields.Char()


class InheritPartner(models.Model):
    _inherit = 'res.partner'

    engagement_done = fields.Boolean("Engagements Fetched")


class InheritCRM(models.Model):
    _inherit = 'crm.lead'

    engagement_done = fields.Boolean("Engagements Fetched")


class InheritTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    engagement_done = fields.Boolean("Engagements Fetched")


class LogHandling(models.Model):
    _name = 'log.handling'

    record_id = fields.Char('Hubspot Id')
    odoo_record_name = fields.Char('Odoo Record Name')
    description = fields.Char('Description')
    skip = fields.Boolean('Record Skip?')
    model = fields.Char('Odoo Model')
