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
    score_academic_year_id = fields.Many2one('education.academic.year', string='Năm học', required=True)
    score_student_one_ids = fields.One2many('education.score.overall.one', 'overall_student_one_id')
    score_student_two_ids = fields.One2many('education.score.overall.two', 'overall_student_two_id')
    state = fields.Boolean(default=False)
    status = fields.Selection([('up', 'Đủ điều kiện lên lớp'), ('down', 'Không đủ điều kiện lên lớp')], default='up')

    name = fields.Char()
    score_average_one = fields.Float(string='Điểm TB HK1', default=8)
    score_average_two = fields.Float(string='Điểm TB HK2', default=10)
    score_average_overall = fields.Float(string='Điểm TB cả năm')

    def calculate_score_average_overall(self):
        self.score_student_one_ids.get_score_student_one()
        self.score_student_two_ids.get_score_student_two()
        # Code calculate score student
        # self.score_average_one = self.score_student_one_ids.get_score_student_one()
        # self.score_average_two = self.score_student_two_ids.get_score_student_two()
        self.score_average_overall = (self.score_average_one + 2 * self.score_average_two) / 3
        self.state = True

    @api.model
    def create(self, vals):
        division_id = self.env['education.class.division'].browse(vals['score_division_id'])
        academic_year_id = self.env['education.academic.year'].browse(vals['score_academic_year_id'])
        score_student_id = self.env['education.student'].browse(vals['score_student_id'])
        name = 'Bảng điểm học sinh ' + str(score_student_id.name) + ' - Lớp ' + str(
            division_id.name) + ' (Năm học ' + str(academic_year_id.name) + ')'
        vals['name'] = name
        return super(EducationScoreStudent, self).create(vals)


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

    # academic_year_id_one = fields.Many2one('education.academic.year', string='Năm học')
    overall_student_one_id = fields.Many2one('education.score.student')

    def get_score_student_one(self):
        search_score_exam_one = self.env['exam.result.line'].sudo().search([
            ('student_class_ids', '=', self.overall_student_one_id.score_class_id.id),
            ('student_division_ids', '=', self.overall_student_one_id.score_division_id.id),
            ('academic_year_id', '=', self.overall_student_one_id.score_academic_year_id.id),
            ('term_code', '=', 'one')])
        if search_score_exam_one:
            average_score_one = 0
            count_subject = 0
            for exam in search_score_exam_one:
                if exam.exam_type:
                    if exam.exam_type == 'final_exam':
                        self.final_exam = exam.mark_scored
                    else:
                        raise ValidationError('Không tìm thấy kết quả bài thi học kỳ 1 của học sinh này.')
                    if exam.exam_type == 'fast_exam':
                        if self.fast_exam_1:
                            self.fast_exam_1 = exam.mark_scored
                        else:
                            self.fast_exam_2 = exam.mark_scored
                    else:
                        raise ValidationError('Không tìm thấy kết quả điểm miệng học kỳ 1 của học sinh này.')
                    if exam.exam_type == 'part_exam':
                        if self.part_exam_1:
                            self.part_exam_1 = exam.mark_scored
                        else:
                            self.part_exam_2 = exam.mark_scored
                    else:
                        raise ValidationError('Không tìm thấy kết quả bài kiểm tra 15p học kỳ 1 của học sinh này.')
                    if exam.exam_type == 'quarter_exam':
                        if self.quarter_exam_1:
                            self.quarter_exam_1 = exam.mark_scored
                        else:
                            self.quarter_exam_2 = exam.mark_scored
                    else:
                        raise ValidationError('Không tìm thấy kết quả bài kiểm tra 45p học kỳ 1 của học sinh này.')

                average_score_1 = self.fast_exam_1 + self.fast_exam_2 + self.part_exam_1 + self.part_exam_2
                average_score_2 = self.quarter_exam_1 * 2 + self.quarter_exam_2 * 2 + self.final_exam * 3
                self.average_score = (average_score_1 + average_score_2) / 11
                average_score_one = average_score_one + self.average_score
                count_subject = count_subject + 1
            result_one = average_score_one / count_subject
            return result_one
        else:
            raise ValidationError('Không tìm thấy kết quả bài thi học kỳ 1 của học sinh này.')


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

    def get_score_student_two(self):
        search_score_exam_two = self.env['exam.result.line'].sudo().search([
            ('student_class_ids', '=', self.overall_student_one_id.score_class_id.id),
            ('student_division_ids', '=', self.overall_student_one_id.score_division_id.id),
            ('academic_year_id', '=', self.overall_student_one_id.score_academic_year_id.id),
            ('term_code', '=', 'two')])
        if search_score_exam_two:
            average_score_two = 0
            count_subject = 0
            for exam in search_score_exam_two:
                if exam.exam_type:
                    if exam.exam_type == 'final_exam':
                        self.final_exam = exam.mark_scored
                    else:
                        raise ValidationError('Không tìm thấy kết quả bài thi học kỳ 2 của học sinh này.')
                    if exam.exam_type == 'fast_exam':
                        if self.fast_exam_1:
                            self.fast_exam_1 = exam.mark_scored
                        else:
                            self.fast_exam_2 = exam.mark_scored
                    else:
                        raise ValidationError('Không tìm thấy kết quả điểm miệng học kỳ 2 của học sinh này.')
                    if exam.exam_type == 'part_exam':
                        if self.part_exam_1:
                            self.part_exam_1 = exam.mark_scored
                        else:
                            self.part_exam_2 = exam.mark_scored
                    else:
                        raise ValidationError('Không tìm thấy kết quả bài kiểm tra 15p học kỳ 2 của học sinh này.')
                    if exam.exam_type == 'quarter_exam':
                        if self.quarter_exam_1:
                            self.quarter_exam_1 = exam.mark_scored
                        else:
                            self.quarter_exam_2 = exam.mark_scored
                    else:
                        raise ValidationError('Không tìm thấy kết quả bài kiểm tra 45p học kỳ 2 của học sinh này.')

                average_score_1 = self.fast_exam_1 + self.fast_exam_2 + self.part_exam_1 + self.part_exam_2
                average_score_2 = self.quarter_exam_1 * 2 + self.quarter_exam_2 * 2 + self.final_exam * 3
                self.average_score = (average_score_1 + average_score_2) / 11
                average_score_two = average_score_two + self.average_score
                count_subject = count_subject + 1
            result_two = average_score_two / count_subject
            return result_two
        else:
            raise ValidationError('Không tìm thấy kết quả bài thi học kỳ 2 của học sinh này.')
