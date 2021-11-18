from odoo import fields, models, api


class CreatePlanSaleWizard(models.TransientModel):
    _name = 'create.plan.sale.wizard'

    input_name = fields.Char(string="Name", require=True)
    input_information_plan = fields.Text(string="Information Plan Sale", require=True)

    # sale_order_ids_wizard = fields.Many2many("sale.order")
    id_quotation = fields.Many2one("sale.order")

    # res_partner_ids = fields.Many2many("res.partner", string="Approval")
    form_approval_wizard = fields.Many2many("plan.sale.order", string="Inspector")

    def action_create_plan_sale_1(self):
        for rec in self:
            # rec.sudo().id_quotation.message_post(body="Request create plan sale", message_type='notification',
            #                                      partner_ids=rec.form_approval_wizard.res_partner_form_approval.ids,
            #                                      subtype_xmlid='mail.mt_comment')
            rec.id_quotation.sender_name = rec.input_name
            rec.id_quotation.information_plan = rec.input_information_plan

    def check_approval_true (self):
        for rec in self:
            pass

    def check_approval_false(self):
        for rec in self:
            pass
