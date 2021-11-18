from odoo import api, models, fields, _


class SearchAppointmentWizard(models.TransientModel):
    _name = 'search.appointment.wizard'
    _description = 'Search Appointment Wizard'

    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)

    def action_view_appointment_method1(self):
        action = self.env.ref('om_hospital.action_hospital_appointment').read()[0]
        action['domain'] = [('patient_id', '=', self.patient_id.id)]
        return action

    def action_view_appointment_method2(self):
        action = self.env['ir.actions.actions']._for_xml_id("om_hospital.action_hospital_appointment")
        action['domain'] = [('patient_id', '=', self.patient_id.id)]
        return action

    def action_view_appointment_method3(self):
        return {
            'name': 'Appointments',
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.appointment',
            'view_mode': 'form,tree',
            'view_type': 'form',
            'domain': [('patient_id', '=', self.patient_id.id)],
            'target': 'current'
        }
        # return action
