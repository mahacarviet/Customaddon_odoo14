# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class BatchUpdateWizard(models.TransientModel):
    _name = "my.pet.batchupdate.wizard"
    _description = "Batch update for my.pet model"

    dob = fields.Date('DOB', required=False, default=False)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender', default=False)
    owner_id = fields.Many2one('res.partner', string='Owner', default=False)
    basic_price = fields.Float('Basic Price', default=0)

    def multi_update(self):
        ids = self.env.context.get('active_ids', []) # modify these lines!!
        # _logger.warning(ids)
        # if ids:
        #     my_pets = self.env["my.pet"].browse(ids) # get selected records
        # else:
        #     my_pets = self.env["my.pet"].search([]) # get all records
        my_pets = self.env["my.pet"].browse(ids)
        new_data = {}
        
        if self.dob:
            new_data["dob"] = self.dob
        if self.gender:
            new_data["gender"] = self.gender
        if self.owner_id:
            new_data["owner_id"] = self.owner_id
        if self.basic_price > 0:
            new_data["basic_price"] = self.basic_price
        
        my_pets.write(new_data)
        