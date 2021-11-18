from odoo import fields, models, api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    discount_code = fields.Char(related="partner_id.customer_discount_code", string="Discount Code")
    check_discount_code = fields.Boolean(related="partner_id.check_discount_code", string="Check Discount Code")

    discount_total = fields.Monetary(compute="_compute_discount_total")

    # amount_total = fields.Monetary(compute="_compute_amount_total")

    def _compute_discount_total(self):
        for rec in self:
            if rec.check_discount_code == False:
                rec.discount_total = rec.amount_untaxed + rec.amount_tax
            else:
                rec.discount_total = (1 - float(str(rec.discount_code)[4:]) / 100) * (rec.amount_untaxed + rec.amount_tax)


    # @api.depends('amount_total')
    # def _compute_discount_total(self):
    #     for rec in self:
    #         rec.amount_total = rec.amount_untaxed + rec.amount_tax - int(str(rec.discount_code)[4:]) / 100 * (
    #                     rec.amount_untaxed + rec.amount_tax)
