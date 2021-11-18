# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HospitalAppointment(models.Model):
    _name = "hospital.appointment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hospital Appointment"
    # _order = "doctor_id,name,age"
    # _order allow to use many field

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    age = fields.Integer(related='patient_id.age', string='Age', tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')])
    note = fields.Text(string='Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='Status', defaul='draft', tracking=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    date_appointment = fields.Date(string='Date', required=True)
    # date_check = fields.Datetime(string='Check Up Time')
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor', required=True)
    prescription = fields.Text(string="Prescription")
    prescription_line_id = fields.One2many('appointment.prescription.line', 'appointment_id',
                                           string='Prescription Line')

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.model
    def create(self, vals):
        if not vals.get('note'):
            vals['note'] = 'New Patient'
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.appointment') or _('New')
        res = super(HospitalAppointment, self).create(vals)
        print(res.id)
        return res

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        for rec in self:
            if rec.patient_id:
                if self.patient_id.gender:
                    rec.gender = self.patient_id.gender
                if self.patient_id.note:
                    rec.note = self.patient_id.note
            else:
                rec.gender = ''
                rec.note = ''

    def unlink(self):
        if self.state == 'done':
            raise ValidationError(_('You Cannot Delete "%s" as it is in Done State' % self.name))
        return super(HospitalAppointment, self).unlink()

    def action_url(self):
        return {
            'type': 'ir.actions.act_url',
            'url': 'https://github.com/mahacarviet',
            # 'url': 'https://github.com/mahacarviet/%s/' % self.prescription,
            'target': 'new'
        }


class AppointmentPrescriptionLine(models.Model):
    _name = "appointment.prescription.line"
    _description = "Appointment Prescription Line"

    name = fields.Char(string='Medicine')
    quantity = fields.Integer()
    note = fields.Char()
    appointment_id = fields.Many2one('hospital.appointment', string="Appointment")
