from odoo import _, models, fields


class CreatePlan(models.TransientModel):
    _name = "create.plan.wizard"

    name = fields.Text(string='Name Plan', required=True)
    detail = fields.Text(string='Detail Information About Plan', required=True)

    list_partner = fields.Many2one('res.partner')

    def create_plan(self):
        quotation_id = self.env.context.get('active_ids', [])
        print(self.list_partner)
        quotation = self.env['sale.order'].browse(quotation_id[0])
        vals = {
            'name': self.name,
            'quotation': quotation_id[0],
            'detail': self.detail,
            'state': 'new'
        }
        self.env['plan.sale.order'].create(vals)
        plan_id = self.env['plan.sale.order'].search([('quotation', '=', quotation_id[0])], limit=1).id
        quotation.write({'business_plan': plan_id})
        for partner in self.list_partner:
            self.env['form.approver'].create({
                'plan_id': plan_id,
                'partner': partner.id
            })

        message = _(
            'Plan for quotation "%(quotation)s" created successfully.',
            quotation=quotation.name
        )
        quotation.message_post(body=message, message_type='notification', subtype_xmlid='mail.mt_comment')
