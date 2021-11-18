# -*- coding: utf-8 -*-


from odoo import fields, models, api


class EducationFaculty(models.Model):
    _name = 'education.faculty'
    _inherit = ['mail.thread']
    _description = 'Giáo viên'

    @api.model
    def create(self, vals):
        """Over riding the create method to assign
        the sequence for newly creating records"""
        vals['faculty_id'] = self.env['ir.sequence'].next_by_code(
            'education.faculty')
        res = super(EducationFaculty, self).create(vals)
        return res

    name = fields.Char(string='Họ và tên', required=True)
    faculty_id = fields.Char(string="ID", readonly=True)
    image = fields.Binary(string="Ảnh", attachment=True)
    email = fields.Char(string="Email", help="Email liên hệ với giáo viên")
    mobile = fields.Char(string="Số điện thoại")
    date_of_birth = fields.Date(string="Ngày sinh")
    home_towm = fields.Char(string='Quê quán')
    iden_id = fields.Char(string='Mã số CMT')
    iden_id_from = fields.Char(string='Nơi cấp')
    iden_id_date = fields.Date(string='Ngày cấp')
    date_come_from = fields.Date(string='Ngày vào trường')
    religion = fields.Char(string='Tôn giáo')

    street = fields.Char(string='Địa chỉ')
    city = fields.Char(string='Quận')
    state_id = fields.Many2one("res.country.state", string='Thành phố', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Quốc gia', ondelete='restrict')

    degree = fields.Char(string="Học vị", Help="Nhập bằng cao nhất của giáo viên.")
    gender = fields.Selection(
        [('male', 'Nam'), ('female', 'Nữ'), ('other', 'Giới tính khác')],
        string='Giới tính', required=True, default='male',
        track_visibility='onchange')
    blood_group = fields.Selection(
        [('a+', 'A+'), ('a-', 'A-'), ('b+', 'B+'), ('o+', 'O+'), ('o-', 'O-'),
         ('ab-', 'AB-'), ('ab+', 'AB+')],
        string='Nhóm máu', required=True, default='a+',
        track_visibility='onchange')
    subject_lines = fields.Many2many('education.subject', string='Subject Lines')
