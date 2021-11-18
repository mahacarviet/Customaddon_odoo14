# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_basic_price = fields.Float('Default Pet\'s Basic Price', default_model='my.pet')
    mypet_is_check_duplicated_pet_name = fields.Boolean('Check Duplicated Pet Name', config_parameter='mypet.is_check_duplicated_pet_name')
