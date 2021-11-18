# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class EducationAcademic(models.Model):
    _name = 'education.academic.year'
    _description = 'Năm học'
    _order = 'sequence asc'
    _rec_name = 'name'

    @api.model
    def create(self, vals):
        """Over riding the create method and assigning the 
        sequence for the newly creating record"""
        vals['sequence'] = self.env['ir.sequence'].next_by_code(
            'education.academic.year')
        res = super(EducationAcademic, self).create(vals)
        return res

    def unlink(self):
        """return validation error on deleting the academic year"""
        for rec in self:
            raise ValidationError(
                _("Năm học không thể xóa, người dùng có thể ẩn năm học đó."))

    name = fields.Char(string='Tên năm học', required=True)
    # term_code = fields.Selection([('one', 'Học kỳ 1'), ('two', 'Học kỳ 2')], default='one', string='Mã năm học')
    ay_code = fields.Char(string='Mã năm học', required=True)
    sequence = fields.Integer(string='Số tuần tự năm học', required=True,
                              help='Mã đánh dấu chỉ số giúp kiểm soát sự tuần tự của các năm học')
    ay_start_date = fields.Date(string='Ngày bắt đầu', required=True,
                                help='Ngày bắt đầu năm học')
    ay_end_date = fields.Date(string='Ngày kết thúc', required=True,
                              help='Ngày kết thúc năm học')
    ay_description = fields.Text(string='Mô tả năm học')

    _sql_constraints = [
        ('ay_code', 'unique(ay_code)', "Mã năm học đã tồn tại!"), ]

    @api.constrains('ay_start_date', 'ay_end_date')
    def validate_date(self):
        """Checking the start and end dates of the syllabus,
        raise warning if start date is not anterior"""
        for rec in self:
            if rec.ay_start_date >= rec.ay_end_date:
                raise ValidationError(
                    _('Ngày kết thúc năm học phải diễn ra sau ngày bắt đầu năm học.'))
