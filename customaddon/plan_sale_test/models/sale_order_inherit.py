from odoo import fields, models, api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    plan_sale_sale_order_1 = fields.One2many("plan.sale.order", "sale_order_plan_sale_1")

    status = fields.Selection(related="plan_sale_sale_order_1.status")
    sender_name = fields.Char(string="Name")
    information_plan = fields.Text(string="Information Business Plan")

    # create_plan_sale_order = fields.One2many("create.plan.sale.wizard")

    def action_create_plan_sale(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'My Company',
            'view_mode': 'form',
            'res_model': 'create.plan.sale.wizard',
            'target': 'new',
            'context': {
                'default_id_quotation': self.id,
                'default_res_partner_ids': self.ids,

            }
        }
