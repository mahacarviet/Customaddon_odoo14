# -*- coding: utf-8 -*-


from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class EducationSubject(models.Model):
    _name = 'education.subject'

    name = fields.Char(string='Tên môn học', required=True)
    is_language = fields.Boolean(string="Môn học ngôn ngữ",
                                 help="Lựa chọn nếu môn học này là ngôn ngữ")
    is_lab = fields.Boolean(string="Có sử dụng phòng thí nghiệm", help="Lựa chọn nếu môn học sử dụng phòng thí nghiệm")
    code = fields.Char(string="Mã môn học")
    type = fields.Selection(
        [('compulsory', 'Bắt buộc'), ('elective', 'Tùy chọn')],
        string='Loại môn học', default="compulsory")

    description = fields.Text(string='Mô tả chi tiết môn học')

    _sql_constraints = [
        ('code', 'unique(code)',
         "Mã môn học đã tồn tại!"),
    ]


class EducationSyllabus(models.Model):
    _name = 'education.syllabus'

    name = fields.Char('Mã giáo án', required=True)
    class_id = fields.Many2one('education.class', string='Khối')
    subject_id = fields.Many2one('education.subject', string='Môn học')
    total_hours = fields.Float(string='Tổng số giờ')
    description = fields.Text(string='Mô tả chi tiết')

    @api.constrains('total_hours')
    def validate_time(self):
        """returns validation error if the hours is not a possitive value"""
        for rec in self:
            if rec.total_hours <= 0:
                raise ValidationError(_('Số giờ phải lớn hơn 0.'))
