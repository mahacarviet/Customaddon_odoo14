from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EducationScoreStudent(models.Model):
    _name = 'education.score.student'
    _description = "Thẻ điểm"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    score_student_id = fields.Many2one('education.student', string='Học sinh',
                                       domain="[('class_id', '=', score_division_id)]")
    score_class_id = fields.Many2one('education.class', string='Khối', required=True)
    score_division_id = fields.Many2one('education.class.division', string='Lớp', required=True,
                                        domain="[('class_id', '=', score_class_id)]")
    score_academic_year_id = fields.Many2one(string='Năm học', required=True)
    score_student_one_ids = fields.One2many('education.score.overall.one', 'overall_student_one_id')
    score_student_two_ids = fields.One2many('education.score.overall.two', 'overall_student_two_id')

    name = fields.Char()
    score_average_one = fields.Float(string='Điểm TB HK1')
    score_average_two = fields.Float(string='Điểm TB HK2')
    score_average_overall = fields.Float(string='Điểm TB cả năm')

    def calculate_score_average_overall(self):
        pass


class EducationScoreOverallOne(models.Model):
    _name = 'education.score.overall.one'
    _description = 'Chi tiết điểm học sinh HK1'

    score_subject_id = fields.Many2one('education.subject', string='Môn học')
    fast_exam_1 = fields.Float(string='Điểm miệng (1)')
    fast_exam_2 = fields.Float(string='Điểm miệng (2)')
    part_exam_1 = fields.Float(string='Điểm 15p (1)')
    part_exam_2 = fields.Float(string='Điểm 15p (2)')
    quarter_exam_1 = fields.Float(string='Điểm 45p (1)')
    quarter_exam_2 = fields.Float(string='Điểm 45p (2)')
    final_exam = fields.Float(string='Điểm học kỳ')
    average_score = fields.Float(string='Điểm TB')

    overall_student_one_id = fields.Many2one('education.score.student')


class EducationScoreOverallTwo(models.Model):
    _name = 'education.score.overall.two'
    _description = 'Chi tiết điểm học sinh HK2'

    score_subject_id = fields.Many2one('education.subject', string='Môn học')
    fast_exam_1 = fields.Float(string='Điểm miệng (1)')
    fast_exam_2 = fields.Float(string='Điểm miệng (2)')
    part_exam_1 = fields.Float(string='Điểm 15p (1)')
    part_exam_2 = fields.Float(string='Điểm 15p (2)')
    quarter_exam_1 = fields.Float(string='Điểm 45p (1)')
    quarter_exam_2 = fields.Float(string='Điểm 45p (2)')
    final_exam = fields.Float(string='Điểm học kỳ')
    average_score = fields.Float(string='Điểm TB')

    overall_student_two_id = fields.Many2one('education.score.student')

