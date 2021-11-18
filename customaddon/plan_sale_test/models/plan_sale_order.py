from odoo import fields, models, api


class PlanSaleOrder(models.Model):
    _name = 'plan.sale.order'

    sale_order_plan_sale_1 = fields.Many2one("sale.order", "plan_sale_sale_order_1")

    sender_name = fields.Char(string="Name")
    id_quotation = fields.Char(related="sale_order_plan_sale_1.name", readonly=True)
    information_plan = fields.Text(string="Information Business Plan")

    status = fields.Selection([('approved', "Approved"),
                               ('waiting_approved', "Waiting Approved"),
                               ('denied', "Denied")], default="waiting_approved")

    res_partner_form_approval = fields.Many2one("res.partner", string="Approval")


