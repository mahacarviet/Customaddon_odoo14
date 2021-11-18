from odoo import fields, models, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class UpdateProductWarrantyWizard(models.TransientModel):
    _name = 'update.product.warranty.wizard'

    input_date_from = fields.Date(string='Warranty From')
    input_date_to = fields.Date(string='Warranty To')

    product_template_wizard = fields.Many2many('product.template', string='Product Template Wizard')


    def action_update_product_warranty(self):
        for rec in self:
            if rec.product_template_wizard:
                for product in rec.product_template_wizard:
                    product.date_from = rec.input_date_from
                    product.date_to = rec.input_date_to
