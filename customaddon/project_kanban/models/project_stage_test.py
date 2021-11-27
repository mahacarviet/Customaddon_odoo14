# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectStageTest(models.Model):
    _name = 'project.stage.test'
    _rec_name = 'name'

    name = fields.Char(string='Stage', defaut='New', store=True)
    stage_note = fields.Char(string='Description')

