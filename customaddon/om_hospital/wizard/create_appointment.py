from odoo import api, models, fields, _
from datetime import *


class CreateAppointmentWizard(models.TransientModel):
    _name = 'create.appointment.wizard'
    _description = 'Create Appointment Wizard'

    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    date_appointment = fields.Date(string='Date', required=True)
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor')

    @api.model
    def default_get(self, fields):
        res = super(CreateAppointmentWizard, self).default_get(fields)
        if self._context.get('active_id'):
            res['patient_id'] = self._context.get('active_id')
        return res

    def action_create_appointment(self):
        vals = {
            'doctor_id': self.doctor_id.id,
            'patient_id': self.patient_id.id,
            'date_appointment': self.date_appointment,
            'state': 'draft'
        }
        appointment_rec = self.env['hospital.appointment'].create(vals)
        print("appointment", appointment_rec.id)
        return {
            'name': _('Appointment'),
            'view_mode': 'form',
            'res_model': 'hospital.appointment',
            'res_id': appointment_rec.id,
            'type': 'ir.actions.act_window',
        }

    # def action_view_appointment(self):
    #     # Method 1
    #     # action = self.env.ref('om_hospital.action_hospital_appointment').read()[0]
    #     # action['domain'] = [('patient_id', '=', self.patient_id.id)]
    #     # return action
    #
    #     # Method 2
    #     # action = self.env['ir.actions.actions']._for_xml_id("om_hospital.action_hospital_appointment")
    #     # action['domain'] = [('patient_id', '=', self.patient_id.id)]
    #     # return action
    #
    #     # Method 3
    #     # return {
    #     #     'name': 'Appointments',
    #     #     'type': 'ir.actions.act_window',
    #     #     'res_model': 'hospital.appointment',
    #     #     'view_mode': 'form,tree',
    #     #     'view_type': 'form',
    #     #     'domain': [('patient_id', '=', self.patient_id.id)],
    #     #     'target': 'current'
    #     # }
