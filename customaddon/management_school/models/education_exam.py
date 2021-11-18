from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EducationExam(models.Model):
    _name = 'education.exam'
    _description = 'Bài kiểm tra'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Tên bài kiểm tra', default='Mới')
    class_id = fields.Many2one('education.class', string='Khối', required=True)
    division_id = fields.Many2one('education.class.division', string='Lớp', required=True,
                                  domain="[('class_id', '=', class_id)]")
    exam_type = fields.Selection(
        [('part_exam', 'Kiểm tra 15p'), ('quarter_exam', 'Kiểm tra 45p'),
         ('fast_exam', 'Kiểm tra miệng'), ('final_exam', 'Kiểm tra học kỳ')],
        string='Loại bài kiểm tra', required=True)
    start_date = fields.Date(string='Ngày bắt đầu')
    end_date = fields.Date(string='Ngày kết thúc')
    subject_id = fields.Many2one('education.subject', string='Môn học', required=True)
    state = fields.Selection(
        [('draft', 'Nháp'),
         ('ongoing', 'Đang diễn ra'),
         ('close', 'Đóng'),
         ('cancel', 'Hủy')],
        default='draft')
    term_code = fields.Selection([('one', 'Học kỳ 1'), ('two', 'Học kỳ 2')], default='one', string='Mã năm học')
    check_exam_result = fields.Boolean(default=False)

    academic_year = fields.Many2one('education.academic.year', string='Năm học', store=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())
    exam_attachment_id = fields.Many2many(
        'ir.attachment',
        string="Tài liệu",
        copy=False)

    @api.constrains('start_date', 'end_date')
    def check_dates(self):
        for rec in self:
            if rec.start_date > rec.end_date:
                raise ValidationError(
                    _("Ngày bắt đầu phải diễn ra trước ngày kết thúc."))

    @api.model
    def create(self, vals):
        res = super(EducationExam, self).create(vals)
        search_exam = self.env['education.exam'].search(
            [
                ('class_id', '=', res.class_id.id),
                ('division_id', '=', res.division_id.id),
                ('subject_id', '=', res.subject_id.id),
                ('state', '!=', 'close'),
                ('academic_year', '!=', res.academic_year.id),
            ])

        if res.exam_type == 'final_exam':
            if len(search_exam) > 1:
                raise UserError(
                    _('Bài kiểm tra học kỳ đã được tạo.'))
            return res
        else:
            if len(search_exam) > 1:
                raise UserError(
                    _('Bài kiểm tra miệng, 15p, 45p chỉ được tạo tối đa 2 bài kiểm tra.'))
            return res

    def close_exam(self):
        self.state = 'close'

    def cancel_exam(self):
        self.state = 'cancel'

    def confirm_exam(self):
        if not self.subject_id:
            raise UserError(_('Bài kiểm tra chưa được thêm môn học.'))
        value_exam_type = dict(self._fields['exam_type'].selection).get(self.exam_type)
        name = str(value_exam_type) + ' - ' + str(self.academic_year.name) + ' -'
        if self.term_code == 'one':
            name = name + ' HK1'
        else:
            name = name + ' HK2'
        if self.division_id:
            name = name + ' - ' + str(self.subject_id.name) + ' (' + str(self.division_id.name) + ')'
        self.name = name
        self.state = 'ongoing'
