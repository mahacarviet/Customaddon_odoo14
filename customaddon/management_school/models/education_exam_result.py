from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date


class EducationExamResult(models.Model):
    _name = 'education.exam.result'
    _description = "Kết quả bài kiểm tra"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Kết quả bài kiểm tra', default='Mới')
    mark = fields.Float(string='Điểm tối đa', required=True, default=10)
    state = fields.Selection([('draft', 'Mới'), ('completed', 'Hoàn tất'),
                              ('cancel', 'Hủy')], default='draft')
    mark_sheet_created = fields.Boolean(default=False)
    date = fields.Date(string='Ngày đánh giá', default=date.today())
    term_code = fields.Selection(related='exam_result_ids.term_code', string='Học kỳ', store=True)
    exam_type = fields.Selection(related='exam_result_ids.exam_type', string='Bài kiểm tra', store=True)

    student_id = fields.Many2one('education.student', string='Học sinh')
    class_id = fields.Many2one(string='Khối', related='exam_result_ids.class_id', required=True, store=True)
    division_id = fields.Many2one(string='Lớp', related='exam_result_ids.division_id', required=True, store=True)
    result_subject_id = fields.Many2one(related='exam_result_ids.subject_id', string='Môn học', store=True)
    academic_year_id = fields.Many2one(related='exam_result_ids.academic_year', string='Năm học', store=True)
    exam_result_ids = fields.Many2one('education.exam', string='Bài kiểm tra',
                                      domain=[('state', '=', 'close'), ('check_exam_result', '=', False)])
    valuation_line = fields.One2many('exam.result.line', 'education_exam_ids', string='Students')
    teachers_id = fields.Many2one('education.faculty', string='Giáo viên đánh giá')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())

    @api.model
    def create(self, vals):
        res = super(EducationExamResult, self).create(vals)
        search_valuation = self.env['education.exam.result'].search(
            [('id', '=', res.exam_result_ids.id),
             ('class_id', '=', res.class_id.id),
             ('division_id', '=', res.division_id.id),
             ('result_subject_id', '=', res.result_subject_id.id),
             ('state', '=', 'close')])
        if len(search_valuation) > 1:
            raise UserError(
                _('Bài đánh giá kết quả cho bài kiểm tra này đã được tạo hoặc bài kiểm tra vẫn đang diễn ra.'))
        return res

    def valuation_canceled(self):
        if self.valuation_line:
            self.valuation_line.sudo().unlink()
        self.mark_sheet_created = False
        self.state = 'cancel'

    def set_to_draft(self):
        if self.valuation_line:
            self.valuation_line.sudo().unlink()
        self.state = 'draft'

    def valuation_completed(self):
        self.name = 'Kết quả bài' + str(self.exam_result_ids.name)
        # Xu ly diem
        self.exam_result_ids.check_exam_result = True
        self.state = 'completed'

    def create_mark_sheet(self):
        valuation_line_obj = self.env['exam.result.line']
        students = self.division_id.student_ids
        if len(students) < 1:
            raise UserError(_('Không có học sinh nào trong lớp học này.'))
        for student in students:
            data = {
                'student_id': student.id,
                'student_name': student.name,
                'education_exam_ids': self.id,
                'student_division_ids': self.division_id.id,
                'student_class_ids': self.class_id.id,
            }
            valuation_line_obj.create(data)
        self.mark_sheet_created = True


class EducationExamResultLine(models.Model):
    _name = 'exam.result.line'
    _description = "Kết quả bài kiểm tra"

    education_exam_ids = fields.Many2one('education.exam.result')
    student_division_ids = fields.Many2one('education.class.division')
    student_class_ids = fields.Many2one('education.class')
    student_id = fields.Many2one('education.student', string='Học sinh')
    student_name = fields.Char(string='Họ và tên')
    mark_scored = fields.Float(string='Điểm số')
    term_code = fields.Selection(related='education_exam_ids.term_code', string='Học kỳ', store=True)
    exam_type = fields.Selection(related='education_exam_ids.exam_type', string='Bài kiểm tra', store=True)
    subject_id = fields.Many2one(related='education_exam_ids.result_subject_id', string='Môn học', store=True)
    academic_year_id = fields.Many2one(related='education_exam_ids.academic_year_id', string='Năm học', store=True)

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())

    @api.constrains('mark_scored')
    def check_scored(self):
        for rec in self:
            search_mark_scored = self.env['education.exam.result'].search(
                [('id', '=', rec.education_exam_ids.id)], limit=1)
            if rec.mark_scored < 0:
                raise ValidationError(
                    _("Điểm số học sinh phải lớn hơn 0."))
            if rec.mark_scored > search_mark_scored.mark:
                raise ValidationError(
                    _("Điểm số học sinh không được vượt quá điểm số tối đa."))
