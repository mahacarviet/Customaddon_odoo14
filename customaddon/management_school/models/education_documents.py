# -*- coding: utf-8 -*-

import datetime
from datetime import date
from odoo import fields, models, api, _


class EducationDocuments(models.Model):
    _name = 'education.documents'
    _description = "Tài liệu học sinh"

    @api.model
    def create(self, vals):
        """Over riding the create method to assign
        the sequence for newly creating records"""
        if vals.get('name', _('Mới')) == _('Mới'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'education.documents') or _('Mới')
        res = super(EducationDocuments, self).create(vals)
        return res

    name = fields.Char(string='Mã tài liệu', copy=False,
                       default=lambda self: _('Mới'))
    document_name = fields.Many2one('document.document', string="Loại tài liệu",
                                    required=True, help="Choose the type of the Document")
    description = fields.Text(string='Mô tả chi tiết tài liệu', copy=False)
    reference = fields.Char(string='Tên tài liệu', required=True, copy=False)

    application_ref = fields.Many2one('education.application', invisible=1,
                                      copy=False)
    doc_attachment_id = fields.Many2many(
        'ir.attachment', 'doc_attach_rel',
        'doc_id', 'attach_id3',
        string="Tài liệu",
        copy=False)


class HrEmployeeAttachment(models.Model):
    _inherit = 'ir.attachment'

    doc_attach_rel = fields.Many2many('education.documents',
                                      'doc_attachment_id', 'attach_id3',
                                      'doc_id',
                                      string="Thêm tài liệu", invisible=1)


class DocumentDocument(models.Model):
    _name = 'document.document'
    _description = "Loại tài liệu"

    name = fields.Char(string='Tên loại tài liệu', required=True)
    description = fields.Char(string='Mô tả chi tiết')
