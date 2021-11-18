# -*- coding: utf-8 -*-


from odoo import fields, models


class EducationAmenities(models.Model):
    _name = 'education.amenities'
    _description = 'Thiết bị của trường'
    _order = 'name asc'
    _rec_name = 'name'

    name = fields.Char(string='Tên thiết bị', required=True)
    code = fields.Char(string='Mã thiết bị')

    _sql_constraints = [
        ('code', 'unique(code)',
         "Mã thiết bị đã tồn tại!"),
    ]
