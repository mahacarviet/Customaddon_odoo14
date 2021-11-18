from odoo import _, models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import date


class CreateContractWizard(models.TransientModel):
    _name = "create.contract.wizard"

    contract_id = fields.Char(related="id_quotation.name")
    customer_name = fields.Char(related="id_quotation.partner_id.name")
    signing_date = fields.Date(default=date.today())
    amount_total = fields.Float()
    # contract_id = fields.Char()
    # customer_name = fields.Char()
    # signing_date = fields.Date(default=date.today())
    # amount_total = fields.Monetary()

    id_quotation = fields.Many2many("sale.order")

    # def create_contract(self):
    #     quotation_id = self.env.context.get('active_ids', [])
    #     quotation = self.env['sale.order'].browse(quotation_id[0])
    #     vals = {
    #         'contract_id': self.id_quotation.name,
    #         'customer_name': self.id_quotation.partner_id.name,
    #         'amount_total': self.id_quotation.amount_total,
    #         'signing_date': date.today(),
    #         'state': 'new'
    #     }
    #     self.env['contract.customer'].create(vals)
    #     plan_id = self.env['contract.customer'].search([('contract_sale_order', '=', quotation_id[0])], limit=1).id
    #     # quotation.write({'business_plan': plan_id})




