# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class intern_test_1(models.Model):
#     _name = 'test.model.gitlab'
#     _description = 'intern_test_1.intern_test_1'
#
#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
