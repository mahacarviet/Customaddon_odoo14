# -*- coding: utf-8 -*-


from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class EducationClass(models.Model):
    _name = 'education.class'
    _description = "Lớp học"

    name = fields.Char(string='Khối', required=True)
    syllabus_ids = fields.One2many('education.syllabus', 'class_id')
    division_ids = fields.One2many('education.division', 'class_id')
    code_class = fields.Selection(
        [('six', 'Khối 6'), ('seven', 'Khối 7'), ('eight', 'Khối 8'), ('nine', 'Khối 9')])


class EducationDivision(models.Model):
    _name = 'education.division'
    _description = "Mã lớp"

    name = fields.Char(string='Mã lớp', required=True)
    strength = fields.Integer(string='Sĩ số lớp')
    faculty_id = fields.Many2one('education.faculty', string='Giáo viên chủ nhiệm')
    class_id = fields.Many2one('education.class', string='Lớp')


class EducationClassDivision(models.Model):
    _name = 'education.class.division'
    _description = "Lớp học"
    _inherit = ['mail.thread']

    @api.model
    def create(self, vals):
        """Return the name as a str of class + division"""
        class_id = self.env['education.class'].browse(vals['class_id'])
        division_id = self.env['education.division'].browse(vals['division_id'])
        name = str(class_id.name + ' - ' + division_id.name)
        vals['name'] = name
        vals['code_class'] = class_id.code_class
        return super(EducationClassDivision, self).create(vals)

    def write(self, values):
        """Return the name as a str of class + division"""
        if 'class_id' in values:
            class_id = self.env['education.class'].browse(values['class_id'])
        else:
            class_id = self.class_id
        if 'division_id' in values:
            division_id = self.env['education.division'].browse(values['division_id'])
        else:
            division_id = self.division_id
        name = str(class_id.name + ' - ' + division_id.name)
        values['name'] = name
        values['code_class'] = class_id.code_class
        res = super(EducationClassDivision, self).write(values)
        return res

    def view_students(self):
        """Return the list of current students in this class"""
        self.ensure_one()
        students = self.env['education.student'].search(
            [('class_id', '=', self.id)])
        students_list = students.mapped('id')
        return {
            'domain': [('id', 'in', students_list)],
            'name': _('Học sinh'),
            'view_mode': 'tree,form',
            'res_model': 'education.student',
            'view_id': False,
            'context': {'default_class_id': self.id},
            'type': 'ir.actions.act_window'
        }

    def _get_student_count(self):
        """Return the number of students in the class"""
        for rec in self:
            students = self.env['education.student'].search(
                [('class_id', '=', rec.id)])
            student_count = len(students) if students else 0
            rec.update({
                'student_count': student_count
            })

    def go_out_school(self):
        if self.code_class == 'nine':
            self.status_class = 'out_school'
            self.check_status = True

    def class_promotion(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Thiết lập lên lớp',
            'view_mode': 'form',
            'res_model': 'education.promotion.wizard',
            'target': 'new',
            'context': {
                # 'default_from_promotion_education_division': [(4, self.id)],
                'default_from_promotion_education_division': self.id,
            }
        }

    name = fields.Char(string='Name', readonly=True)
    actual_strength = fields.Integer(string='Sĩ số tối đa', default=40)
    faculty_id = fields.Many2one('education.faculty', string='Giáo viên chủ nhiệm')
    academic_year_id = fields.Many2one('education.academic.year',
                                       string='Năm học', required=True)
    class_id = fields.Many2one('education.class', string='Khối', required=True, store=True)
    division_id = fields.Many2one('education.division', string='Mã lớp', required=True, store=True)
    student_ids = fields.One2many('education.student', 'class_id', string='Học sinh')
    amenities_ids = fields.One2many('education.class.amenities', 'class_id', string='Thiết bị')
    student_count = fields.Integer(string='Học sinh', compute='_get_student_count')
    code_class = fields.Selection(
        [('six', 'Khối 6'), ('seven', 'Khối 7'), ('eight', 'Khối 8'), ('nine', 'Khối 9')], default='six')
    status_class = fields.Selection([('on_going', 'Đang học'), ('out_school', 'Ra trường')], default='on_going')
    check_status = fields.Boolean(default=False)

    @api.constrains('actual_strength')
    def validate_strength(self):
        """Return Validation error if
            the students strength is not a non-zero number"""
        for rec in self:
            if rec.actual_strength <= 0:
                raise ValidationError(_('Sĩ số lớp phải lớn hơn 0.'))


class EducationClassDivisionHistory(models.Model):
    _name = 'education.class.history'
    _description = "Lịch sử lớp học"
    _rec_name = 'class_id'

    academic_year_id = fields.Many2one('education.academic.year', string='Năm học')
    class_id = fields.Char(string='Lớp học')
    student_id = fields.Many2one('education.student', string='Học sinh')


class EducationClassAmenities(models.Model):
    _name = 'education.class.amenities'
    _description = "Thiết bị của lớp"

    name = fields.Many2one('education.amenities', string="Thiết bị")
    qty = fields.Float(string='Số lượng', default=1.0)
    class_id = fields.Many2one('education.class.division', string="Phòng học")

    @api.constrains('qty')
    def check_qty(self):
        """returns validation error if the qty is 0 or negative"""
        for rec in self:
            if rec.qty <= 0:
                raise ValidationError(_('Số lượng thiết bị phải lớn hơn 0.'))
