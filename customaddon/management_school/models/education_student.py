# -*- coding: utf-8 -*-


from odoo import fields, models, api, _


class EducationStudent(models.Model):
    _name = 'education.student'
    _description = 'Học sinh'
    _inherit = ['mail.thread']
    _inherits = {'res.partner': 'partner_id'}
    _rec_name = 'name'

    def student_documents(self):
        """Return the documents student submitted
        along with the admission application"""
        self.ensure_one()
        if self.application_id.id:
            documents = self.env['education.documents'].search(
                [('application_ref', '=', self.application_id.id)])
            documents_list = documents.mapped('id')
            return {
                'domain': [('id', 'in', documents_list)],
                'name': _('Tài liệu'),
                'view_mode': 'tree,form',
                'res_model': 'education.documents',
                'view_id': False,
                'context': {'default_application_ref': self.application_id.id},
                'type': 'ir.actions.act_window'
            }

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search(
                [('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search(
                    [('ad_no', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super(EducationStudent, self).name_search(
            name, args=args, operator=operator, limit=limit)

    @api.model
    def create(self, vals):
        """Over riding the create method to assign
        sequence for the newly creating the record"""
        vals['ad_no'] = self.env['ir.sequence'].next_by_code(
            'education.student')
        res = super(EducationStudent, self).create(vals)
        return res

    # partner_id = fields.Many2one(
    #     'res.partner', string='Partner', required=True, ondelete="cascade")
    application_no = fields.Char(string="Mã đơn đăng ký")
    date_of_birth = fields.Date(string="Ngày sinh", requird=True)
    guardian_name = fields.Char(string="Người bảo hộ")
    father_name = fields.Char(string="Họ tên bố")
    father_job = fields.Char(string="Nghề nghiệp")
    father_phone = fields.Char(string="Số điện thoại")
    mother_name = fields.Char(string="Họ tên mẹ")
    mother_job = fields.Char(string="Nghề nghiệp")
    mother_phone = fields.Char(string="Số điện thoại")
    class_id = fields.Many2one('education.class.division', string="Lớp")
    admission_class = fields.Many2one('education.class',
                                      string="Khối")
    ad_no = fields.Char(string="Mã học sinh", readonly=True)
    gender = fields.Selection([('male', 'Nam'), ('female', 'Nữ'), ('other', 'Giới tính khác')],
                              string='Giới tính', required=True, default='male',
                              track_visibility='onchange')
    blood_group = fields.Selection([('a+', 'A+'),
                                    ('a-', 'A-'),
                                    ('b+', 'B+'),
                                    ('o+', 'O+'),
                                    ('o-', 'O-'),
                                    ('ab-', 'AB-'),
                                    ('ab+', 'AB+')],
                                   string='Nhóm máu', required=True,
                                   default='a+', track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Công ty')

    street = fields.Char(string='Địa chỉ')
    street2 = fields.Char(string='Địa chỉ thay thế')
    zip = fields.Char(change_default=True, string='Mã ZIP', help="Người dùng nhập vào mã ZIP thành phố")
    city = fields.Char(string='Quận')
    state_id = fields.Many2one("res.country.state", string='Thành phố', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Quốc gia', ondelete='restrict')

    per_street = fields.Char()
    per_street2 = fields.Char()
    per_zip = fields.Char(change_default=True)
    per_city = fields.Char()
    per_state_id = fields.Many2one("res.country.state", string='Thành phố', ondelete='restrict')
    per_country_id = fields.Many2one('res.country', string='Quốc gia',
                                     ondelete='restrict')
    language_speaking = fields.Char(string="Ngôn ngữ gốc")
    sec_lang = fields.Char(string="Ngôn ngữ thứ hai")
    religion = fields.Char(string="Tôn giáo")
    is_same_address = fields.Boolean(string="Tương tự với địa chỉ liên hệ?")
    nationality = fields.Many2one('res.country', string='Quốc tịch', ondelete='restrict')
    application_id = fields.Many2one('education.application',
                                     string="Mã tài liệu")
    class_history_ids = fields.One2many('education.class.history', 'student_id',
                                        string="Lớp học cũ")

    _sql_constraints = [
        ('ad_no', 'unique(ad_no)',
         "Học sinh này đã được tạo từ đơn đăng ký học sinh!"),
    ]
