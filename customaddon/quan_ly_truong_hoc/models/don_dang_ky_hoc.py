# -*- coding: utf-8 -*-


from odoo import fields, models, _, api
from odoo.exceptions import ValidationError


class StudentApplication(models.Model):
    _name = 'education.application'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Đơn đăng ký học'

    @api.model
    def create(self, vals):
        """Overriding the create method and assigning
        the the sequence for the record"""
        if vals.get('application_no', _('New')) == _('New'):
            vals['application_no'] = self.env['ir.sequence'].next_by_code(
                'education.application') or _('New')
        res = super(StudentApplication, self).create(vals)
        return res

    def unlink(self):
        """Return warning if the application is not in the reject state"""
        for rec in self:
            if rec.state != 'reject':
                raise ValidationError(
                    _("Đơn đăng ký chỉ có thể xóa sau khi bị từ chối."))

    def send_to_verify(self):
        """Button action for sending the application for the verification"""
        for rec in self:
            document_ids = self.env['education.documents'].search(
                [('application_ref', '=', rec.id)])
            if not document_ids:
                raise ValidationError(_('Không có tài liệu nào được cung cấp.'))
            rec.write({
                'state': 'verification'
            })

    def create_student(self):
        """Create student from the application
            and data and return the student"""
        for rec in self:
            values = {
                'name': rec.name,
                'application_id': rec.id,
                'father_name': rec.father_name,
                'mother_name': rec.mother_name,
                'guardian_name': rec.guardian_name,
                'street': rec.street,
                'street2': rec.street2,
                'city': rec.city,
                'state_id': rec.state_id.id,
                'country_id': rec.country_id.id,
                'zip': rec.zip,
                'is_same_address': rec.is_same_address,
                'per_street': rec.per_street,
                'per_street2': rec.per_street2,
                'per_city': rec.per_city,
                'per_state_id': rec.per_state_id.id,
                'per_country_id': rec.per_country_id.id,
                'per_zip': rec.per_zip,
                'gender': rec.gender,
                'date_of_birth': rec.date_of_birth,
                'blood_group': rec.blood_group,
                'nationality': rec.nationality.id,
                'email': rec.email,
                'mobile': rec.mobile,
                'image_1920': rec.image,
                'language_speaking': rec.language_speaking,
                'religion_id': rec.religion_id,
                'sec_lang': rec.sec_lang,
                'admission_class': rec.admission_class.id,
                'company_id': rec.company_id.id
            }
            if not rec.is_same_address:
                pass
            else:
                values.update({
                    'per_street': rec.street,
                    'per_street2': rec.street2,
                    'per_city': rec.city,
                    'per_state_id': rec.state_id.id,
                    'per_country_id': rec.country_id.id,
                    'per_zip': rec.zip,
                })

            student = self.env['education.student'].create(values)
            rec.write({
                'state': 'done'
            })
            return {
                'name': _('Student'),
                'view_mode': 'form',
                'res_model': 'education.student',
                'type': 'ir.actions.act_window',
                'res_id': student.id,
                'context': self.env.context
            }

    def reject_application(self):
        """Rejecting the student application for admission"""
        for rec in self:
            rec.write({
                'state': 'reject'
            })

    def application_verify(self):
        """Verifying the student application. Return warning if no Documents
         provided or if the provided documents are not in done state"""
        for rec in self:
            document_ids = self.env['education.documents'].search(
                [('application_ref', '=', rec.id)])
            if document_ids:
                doc_status = document_ids.mapped('state')
                if all(state in ('done', 'returned') for state in doc_status):
                    rec.write({
                        'verified_by': self.env.uid,
                        'state': 'approve'
                    })
                else:
                    raise ValidationError(
                        _('Tất cả các tài liệu chưa được xác minh.'))

            else:
                raise ValidationError(_('No Documents provided'))

    def _document_count(self):
        """Return the count of the documents provided"""
        for rec in self:
            document_ids = self.env['education.documents'].search(
                [('application_ref', '=', rec.id)])
            rec.document_count = len(document_ids)

    def document_view(self):
        """Return the list of documents provided along with this application"""
        self.ensure_one()
        domain = [
            ('application_ref', '=', self.id)]
        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'education.documents',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'help': _('''<p class="oe_view_nocontent_create">
                               Chọn tạo để tạo một bản ghi mới.
                            </p>'''),
            'limit': 80,
            'context': {'default_application_ref': self.id}
        }

    def re_request(self):
        """Reapply rejected student application"""
        for rec in self:
            rec.write({
                'state': 'draft'
            })

    name = fields.Char(string='Họ và tên', required=True)
    prev_school = fields.Char(string='Trường cũ')
    image = fields.Binary(string='Ảnh', attachment=True)
    academic_year_id = fields.Many2one(
        'education.academic.year', string='Năm học',
        help="Người dùng chọn năm học đăng ký học cho sinh viên")
    language_speaking = fields.Char(string="Ngôn ngữ gốc", required=True)
    sec_lang = fields.Char(string="Ngôn ngữ thứ hai", required=True)
    admission_class = fields.Many2one(
        'education.class', string="Khối",
        required=True,
        help="Người dùng nhập khối cho học sinh.")
    admission_date = fields.Datetime('Ngày đăng ký',
                                     default=fields.Datetime.now, required=True)
    application_no = fields.Char(string='Mã đơn đăng ký', required=True,
                                 copy=False, readonly=True,
                                 index=True, default=lambda self: _('New'))
    company_id = fields.Many2one('res.company', string='Công ty',
                                 default=lambda self: self.env.user.company_id)
    email = fields.Char(string="Email")
    mobile = fields.Char(string="Số điện thoại", required=True)
    nationality = fields.Many2one('res.country', string='Quốc tịch', ondelete='restrict')

    street = fields.Char(string='Địa chỉ')
    street2 = fields.Char(string='Địa chỉ thay thế')
    zip = fields.Char(change_default=True, string='Mã ZIP', help="Người dùng nhập vào mã ZIP thành phố")
    city = fields.Char(string='Thành phố')
    state_id = fields.Many2one("res.country.state", string='Thành phố', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Đất nước', ondelete='restrict')
    is_same_address = fields.Boolean(string="Hộ khẩu thường trú", default=True,
                                     help="Người dùng tích nếu hộ khẩu thường trú trùng với với địa chỉ liên hệ")
    per_street = fields.Char(string='Địa chỉ')
    per_street2 = fields.Char(string='Địa chỉ thay thế')
    per_zip = fields.Char(change_default=True, string='Mã ZIP')
    per_city = fields.Char(string='Thành phố')
    per_state_id = fields.Many2one("res.country.state", string='Thành phố', ondelete='restrict')
    per_country_id = fields.Many2one('res.country', string='Đất nước',
                                     ondelete='restrict')
    date_of_birth = fields.Date(string="Ngày sinh", required=True)
    guardian_name = fields.Char(string="Người bảo hộ", required=True)
    description = fields.Text(string="Mô tả chi tiết")
    father_name = fields.Char(string="Họ tên bố")
    mother_name = fields.Char(string="Họ tên mẹ")
    religion_id = fields.Char(string="Tôn giáo")
    class_id = fields.Many2one('education.class.division', string="Class")
    document_count = fields.Integer(compute='_document_count',
                                    string='Tài liệu')
    verified_by = fields.Many2one('res.users', string='Verified by',
                                  help="The Document is verified by")
    reject_reason = fields.Many2one('application.reject.reason',
                                    string='Lý do từ chối')
    gender = fields.Selection(
        [('male', 'Nam'), ('female', 'Nữ'), ('other', 'Giới tính khác')],
        string='Giới tính', required=True, default='male', track_visibility='onchange')
    blood_group = fields.Selection(
        [('a+', 'A+'), ('a-', 'A-'), ('b+', 'B+'), ('o+', 'O+'), ('o-', 'O-'),
         ('ab-', 'AB-'), ('ab+', 'AB+')],
        string='Nhóm máu', required=True, default='a+', track_visibility='onchange')
    state = fields.Selection([('draft', 'Nháp'), ('verification', 'Chờ xác minh'),
                              ('approve', 'Chờ xét duyệt'), ('reject', 'Từ chối'),
                              ('done', 'Hoàn thành')],
                             string='Trạng thái', required=True, default='draft',
                             track_visibility='onchange')
