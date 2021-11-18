# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

from odoo.http import request
import logging
_logger = logging.getLogger(__name__)

class MyPet(models.Model):
    _name = "my.pet"
    _description = "My pet model"

    name = fields.Char('Pet Name', required=True)
    nickname = fields.Char('Nickname')
    description = fields.Text('Pet Description')
    age = fields.Integer('Pet Age', default=1)
    weight = fields.Float('Weight (kg)')
    dob = fields.Date('DOB', required=False)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender', default='male')
    pet_image = fields.Binary("Pet Image", attachment=True, help="Pet Image")    
    owner_id = fields.Many2one('res.partner', string='Owner')
    product_ids = fields.Many2many(comodel_name='product.product', 
                                string="Related Products", 
                                relation='pet_product_rel',
                                column1='col_pet_id',
                                column2='col_product_id')
    basic_price = fields.Float('Basic Price', default=0)
    
    def custom_method(self, name, price, txt_file):
        return {
            "name": name,
            "price": price,
            "txt_file": txt_file,
        }
    
    @api.model
    def create(self, vals):
        is_check_duplicated_pet_name = self.env['ir.config_parameter'].sudo().get_param('mypet.is_check_duplicated_pet_name', default=False)
        if is_check_duplicated_pet_name:
            vals = [vals,] if not isinstance(vals, (tuple, list)) else vals
            for val in vals:
                pet_name = val["name"]
                pet_records = self.search([('name', '=', pet_name)])
                if pet_records:
                    raise ValidationError(_("Duplicated pet name @ %s" % pet_name))
        return super(MyPet, self).create(vals)
    
    @api.model
    def btn_multi_update(self):
        # we can do something on records... it's up to you!
        # res = { 'type': 'ir.actions.client', 'tag': 'reload' } # reload the current page/url
        active_ids = [pet.id for pet in self.env["my.pet"].search([])]
        res = {            
            "name": _("Multi Update"),
            "type": "ir.actions.act_window",
            "res_model": "my.pet.batchupdate.wizard",
            "binding_model_id": self.env['ir.model']._get("my.pet").id,
            "view_mode": "form",
            "target": "new",
            "views": [[False, 'form']],
            "context": {
                "active_ids": active_ids,
                "default_dob": fields.Date.context_today(self),
                "default_owner_id": self.env.user.partner_id.id,
            },
        }
        return res

    def custom_remove(self):
        for pet in self:
            pet.unlink()
        #_logger.warning(self.id) # 5
        #_logger.warning(self.ids) # [5]
        pass
