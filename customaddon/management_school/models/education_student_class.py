# -*- coding: utf-8 -*-


from odoo import fields, models, _
from odoo.exceptions import ValidationError


class EducationStudentClass(models.Model):
    _name = 'education.student.class'
    _description = 'Đăng ký học sinh'
    _inherit = ['mail.thread']
    _rec_name = 'class_id'

    name = fields.Char(string="Đăng ký lớp cho học sinh")
    class_id = fields.Many2one('education.class', string='Khối')
    student_list = fields.One2many('education.student.list', 'connect_id', string="Học sinh")
    admitted_class = fields.Many2one('education.class.division', string="Lớp nhận")
    assigned_by = fields.Many2one('res.users', string='Được đăng ký bởi', default=lambda self: self.env.uid)
    state = fields.Selection([('draft', 'Mới'), ('done', 'Hoàn thành')],
                             string='Trạng thái', required=True, default='draft',
                             track_visibility='onchange')

    def get_student_list(self):
        """returns the list of students applied to join the selected class"""
        for rec in self:
            for line in rec.student_list:
                line.sudo().unlink()
            students = self.env['education.student'].search([
                ('admission_class', '=', rec.class_id.id),
                ('class_id', '=', False)])
            if not students:
                raise ValidationError(_('Không có học sinh nào có sẵn!'))
            values = []
            for stud in students:
                stud_line = {
                    'class_id': rec.class_id.id,
                    'student_id': stud.id,
                    'connect_id': rec.id
                }
                values.append(stud_line)
            for line in values:
                rec.student_list = [(0, 0, line)]


class EducationStudentList(models.Model):
    _name = 'education.student.list'

    connect_id = fields.Many2one('education.student.class', string='#Liên kết =')
    student_id = fields.Many2one('education.student', string='Học sinh')
    class_id = fields.Many2one('education.class', string='Khối')
