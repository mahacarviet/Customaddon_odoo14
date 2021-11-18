# -*- coding: utf-8 -*-
from datetime import datetime, date
import pytz
import werkzeug
from dateutil.tz import tz

from odoo import http, exceptions, _
from odoo.exceptions import ValidationError, UserError
from odoo.http import request


class AdvancedPortalUser(http.Controller):
    @http.route('/my/home', website=True, auth='user', type="http", methods=['POST', 'GET'],
                csrf=False)
    def portal_user_features_dashboard(self, **kw):
        user_id = request.env.user.id
        employee_id = request.env.user.employee_related.id
        employee_name = request.env.user.employee_related.name
        attendance_count = request.env['hr.attendance'].sudo().search_count([('employee_id', '=', employee_id),
                                                                             ('user_id', '=', user_id)])
        leave_count = request.env['hr.leave'].sudo().search_count([('employee_id', '=', employee_id)])
        # ('user_id', '=', user_id)
        over_time_count = request.env['hr.over.time'].sudo().search_count([('employee_id', '=', employee_id),
                                                                           ('user_id', '=', user_id)])
        payslip_count = request.env['hr.payslip'].sudo().search_count([('employee_id', '=', employee_id)])
        return request.render("advanced_portal_user.portal_features_dashboard",
                              {'attendance_count': attendance_count,
                               'leave_count': leave_count,
                               'over_time_count': over_time_count,
                               'payslip_count': payslip_count,
                               'employee_name': employee_name
                               })

    @http.route('/portal_user/my_list_attendance', website=True, auth='user', type="http", methods=['POST', 'GET'],
                csrf=False)
    def portal_user_list_attendances(self, **kw):
        user_id = request.env.user.id
        employee_id = request.env.user.employee_related.id
        list_att = request.env['hr.attendance'].sudo().search([('employee_id', '=', employee_id),
                                                               ('user_id', '=', user_id)])
        return request.render("advanced_portal_user.portal_my_list_attendances",
                              {'list_att': list_att})

    @http.route('/portal_user/create_attendances', website=True, auth='user', type="http", methods=['POST', 'GET'],
                csrf=False)
    def portal_user_create_attendances(self, **kw):
        user_id = request.env.user.id
        employee_id = request.env.user.employee_related.id
        employee_name = request.env.user.employee_related.name
        current_att = request.env['hr.attendance'].sudo().search([('employee_id', '=', employee_id),
                                                                  ('user_id', '=', user_id),
                                                                  ('check_in', '!=', None),
                                                                  ('check_out', '=', None)])
        check_in_str = 0
        check_in_obj = []
        if current_att:
            check_in_obj = current_att['check_in'].replace(tzinfo=tz.gettz('UTC')).astimezone(tz.gettz('Asia/Saigon'))
            check_in_str = str(check_in_obj)[:16]
        else:
            pass
        return request.render("advanced_portal_user.portal_user_create_attendances",
                              {'check_in_str': check_in_str,
                               'check_in_obj': check_in_obj,
                               'employee_name': employee_name
                               })

    @http.route('/portal_user/save_attendances', website=True, auth='user', type="http", methods=['POST', 'GET'],
                csrf=False)
    def portal_user_save_attendances(self, **kw):
        user_id = request.env.user.id
        employee_id = request.env.user.employee_related.id
        today = date.today().strftime("%Y-%m-%d")
        today_str = str(today)
        param_time_in = request.env['ir.config_parameter'].sudo().get_param('advanced_portal_user.time_in')
        param_time_out = request.env['ir.config_parameter'].sudo().get_param('advanced_portal_user.time_out')
        if param_time_in:
            start_time = str(int(param_time_in[:2]) - 7) + param_time_in[2:]
        else:
            start_time = '00:00:00'
        if param_time_out:
            end_time = str(int(param_time_out[:2]) - 7) + param_time_in[2:]
        else:
            end_time = '23:00:00'
        start_date_time = datetime.strptime(today + ' ' + start_time + '.000000', '%Y-%m-%d %H:%M:%S.%f')
        end_date_time = datetime.strptime(today + ' ' + end_time + '.000000', '%Y-%m-%d %H:%M:%S.%f')
        current_time_obj_utc = datetime.now()
        approver = request.env['hr.employee'].sudo().search([('id', '=', employee_id)]).leave_manager_id.id
        current_att = request.env['hr.attendance'].sudo().search([('employee_id', '=', employee_id),
                                                                  ('user_id', '=', user_id),
                                                                  ('check_in', '!=', None),
                                                                  ('check_out', '=', None)])
        current_att_check_in = current_att['check_in']
        current_att_check_in_str = str(current_att_check_in)[:10]
        if start_date_time < current_time_obj_utc < end_date_time:
            if current_att:
                if current_att_check_in_str != today_str:
                    current_att.sudo().write({'check_out': current_att_check_in,
                                              'state': 'draft',
                                              'approver': approver})
                    request.env['hr.attendance'].sudo().create({
                        'employee_id': employee_id,
                        'user_id': user_id,
                        'check_in': current_time_obj_utc,
                    })
                else:
                    current_att.sudo().write({'check_out': current_time_obj_utc})
            else:
                request.env['hr.attendance'].sudo().create({
                    'employee_id': employee_id,
                    'user_id': user_id,
                    'check_in': current_time_obj_utc,
                })
        else:
            raise ValidationError(_('Cannot create new attendance record out of time regulations'))
        return werkzeug.utils.redirect('/portal_user/create_attendances')

    @http.route(['/portal_user/explanation_attendance/<int:element_att_id>'], website=True, auth='user', type="http", methods=['POST', 'GET'], csrf=False)
    def portal_user_explanation_attendance(self, element_att_id=None, **kw):
        attendance = request.env['hr.attendance'].sudo().search([('id', '=', element_att_id)])
        date_explanation = str(attendance['check_in'])[:10]
        return request.render("advanced_portal_user.portal_user_explanation_attendance",
                              {'attendance': attendance, 'date_explanation': date_explanation})

    @http.route('/portal_user/save_explanation_attendance', website=True, auth='user', type="http",
                methods=['POST', 'GET'], csrf=False)
    def portal_user_save_explanation_attendance(self, **kw):
        employee_id = request.env.user.employee_related.id
        explanation_attendance_id = kw['attendance_id']
        explanation = kw['explanation']
        approver = request.env['hr.employee'].sudo().search([('id', '=', employee_id)]).leave_manager_id.id
        explanation_val = {'explanation': explanation, 'state': 'draft', 'approver':approver}
        current_attendance = request.env['hr.attendance'].sudo().search([('id', '=', explanation_attendance_id)])
        if explanation:
            current_attendance.sudo().write(explanation_val)
        return werkzeug.utils.redirect('/portal_user/my_list_attendance')

    @http.route('/portal_user/my_list_leave', website=True, auth='user', type="http", methods=['POST', 'GET'],
                csrf=False)
    def portal_user_list_leaves(self, **kw):
        # user_id = request.env.user.id
        employee_id = request.env.user.employee_related.id
        list_leave = request.env['hr.leave'].sudo().search([('employee_id', '=', employee_id)])
        # ('user_id', '=', user_id)
        return request.render("advanced_portal_user.portal_my_list_leaves",
                              {'list_leave': list_leave})

    @http.route('/portal_user/create_leaves', website=True, auth='user', type="http", methods=['POST', 'GET'],
                csrf=False)
    def generate_template_create_leaves(self, **kw):
        user_id = request.env.user.id
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user_id)]).id
        leave_type = request.env['hr.leave.type'].sudo().search([])
        all_leave = request.env['hr.leave'].sudo().search([('employee_id', '=', employee_id)])
        total_hours = 0
        for leave in all_leave:
            total_hours += leave['number_of_days']
        return request.render("advanced_portal_user.portal_user_create_leaves", {'leave_type': leave_type})

    @http.route('/portal_user/save_leaves', auth='user', website=True, type="http", methods=['POST', 'GET'], csrf=False)
    def portal_user_create_leaves(self, **kw):
        user_id = request.env.user.id
        employee_id = request.env.user.employee_related.id
        date_from_str = kw['date_from']
        #convert string time to object timezone like database
        full_time_from_str = date_from_str[:11] + str(datetime.strptime(date_from_str[11:], '%I:%M %p'))[11:] + '.' + '000000'
        full_time_from_obj_utc = datetime.strptime(full_time_from_str, '%m/%d/%Y %H:%M:%S.%f').replace(tzinfo=tz.gettz('Asia/Saigon')).astimezone(tz.gettz('UTC'))
        full_time_from_str_utc = str(full_time_from_obj_utc)[:19] + '.' + '000000'
        full_time_from_obj = datetime.strptime(full_time_from_str_utc, '%Y-%m-%d %H:%M:%S.%f')
        request_date_from = full_time_from_obj.date()
        date_to_str = kw['date_to']
        full_time_to_str = date_to_str[:11] + str(datetime.strptime(date_to_str[11:], '%I:%M %p'))[11:] + '.' + '000000'
        full_time_to_obj_utc = datetime.strptime(full_time_to_str, '%m/%d/%Y %H:%M:%S.%f').replace(tzinfo=tz.gettz('Asia/Saigon')).astimezone(tz.gettz('UTC'))
        full_time_to_str_utc = str(full_time_to_obj_utc)[:19] + '.' + '000000'
        full_time_to_obj = datetime.strptime(full_time_to_str_utc, '%Y-%m-%d %H:%M:%S.%f')
        request_date_to = full_time_to_obj.date()
        leave_type_kw = int(kw['leave_type'])
        leave_type = request.env['hr.leave.type'].sudo().search([('id', '=', leave_type_kw)]).id
        leave_val = {
            'private_name': str(kw.get('private_name')),
            'state': 'confirm',
            'user_id': user_id,
            'employee_id': employee_id,
            'holiday_status_id': leave_type,
            'date_from': full_time_from_obj,
            'date_to': full_time_to_obj,
            'request_date_from': request_date_from,
            'request_date_to': request_date_to,
            'holiday_type': 'employee',
        }
        ####
        # compute number_of_day in model not working by anyway
        ###
        # missing field user_id
        ###
        request.env['hr.leave'].sudo().create(leave_val)

        return request.render("advanced_portal_user.success_to_create_leave_request", {})

    @http.route('/portal_user/my_list_over_time', website=True, auth='user', type="http", methods=['POST', 'GET'],
                csrf=False)
    def portal_user_list_over_time(self, **kw):
        user_id = request.env.user.id
        employee_id = request.env.user.employee_related.id
        list_over_time = request.env['hr.over.time'].sudo().search([('employee_id', '=', employee_id),
                                                                    ('user_id', '=', user_id)])
        return request.render("advanced_portal_user.portal_my_list_over_time",
                              {'list_over_time': list_over_time})

    @http.route('/portal_user/create_over_time', website=True, auth='user', type="http", methods=['POST', 'GET'],
                csrf=False)
    def portal_user_create_over_time(self, **kw):
        employee_id = request.env.user.employee_related.id
        return request.render("advanced_portal_user.portal_user_create_over_time", {'employee_id': employee_id})

    @http.route('/portal_user/save_over_time', website=True, auth='user', type="http", methods=['POST', 'GET'],
                csrf=False)
    def portal_user_save_over_time(self, **kw):
        user_id = http.request.env.user.id
        employee_id = request.env.user.employee_related.id
        time_from_str = kw['time_from']
        full_time_from_str = time_from_str[:11] + str(datetime.strptime(time_from_str[11:], '%I:%M %p'))[11:] + '.' + '000000'
        full_time_from_obj_utc = datetime.strptime(full_time_from_str, '%m/%d/%Y %H:%M:%S.%f').replace(tzinfo=tz.gettz('Asia/Saigon')).astimezone(tz.gettz('UTC'))
        full_time_from_str_utc = str(full_time_from_obj_utc)[:19] + '.' + '000000'
        full_time_from_obj = datetime.strptime(full_time_from_str_utc, '%Y-%m-%d %H:%M:%S.%f')
        time_to_str = kw['time_to']
        full_time_to_str = time_to_str[:11] + str(datetime.strptime(time_to_str[11:], '%I:%M %p'))[11:] + '.' + '000000'
        full_time_to_obj_utc = datetime.strptime(full_time_to_str, '%m/%d/%Y %H:%M:%S.%f').replace(tzinfo=tz.gettz('Asia/Saigon')).astimezone(tz.gettz('UTC'))
        full_time_to_str_utc = str(full_time_to_obj_utc)[:19] + '.' + '000000'
        full_time_to_obj = datetime.strptime(full_time_to_str_utc, '%Y-%m-%d %H:%M:%S.%f')
        description = kw['description']
        approver = request.env['hr.employee'].sudo().search([('id', '=', employee_id)]).leave_manager_id.id
        if not approver:
            approver = 1
        over_time_val = {
            'user_id': user_id,
            'employee_id': employee_id,
            'description': description,
            'time_from': full_time_from_obj,
            'time_to': full_time_to_obj,
            'approver': approver,
        }
        request.env['hr.over.time'].sudo().create(over_time_val)
        return request.render("advanced_portal_user.success_to_create_over_time_request", {})

    @http.route('/portal_user/my_list_payrolls', website=True, auth='user', type="http", methods=['POST', 'GET'],
                csrf=False)
    def portal_user_list_payrolls(self, **kw):
        employee_id = request.env.user.employee_related.id
        list_payrolls = request.env['hr.payslip'].sudo().search([('employee_id', '=', employee_id)])
        return request.render("advanced_portal_user.portal_my_list_payrolls",
                              {'list_payrolls': list_payrolls})

    @http.route(['/portal_user/payroll_detail/<int:payroll_id>'], website=True, auth='user', type="http", methods=['POST', 'GET'],
                csrf=False)
    def portal_user_view_payroll(self, payroll_id=None, **kw):
        payslip_line = request.env['hr.payslip.line'].sudo().search([('slip_id', '=', payroll_id)])
        payslip_line_total = 0
        for payslip_line_element in payslip_line:
            payslip_line_total += payslip_line_element['total']
        return request.render("advanced_portal_user.portal_user_detail_payroll", {'payslip_line': payslip_line, 'payslip_line_total':payslip_line_total})

    @http.route('/portal_user/create_order', website=True, auth='user', type="http", methods=['POST', 'GET'],
                csrf=False)
    def portal_user_create_order(self, **kw):
        user_id = request.env.user.id
        payment_terms = request.env['account.payment.term'].sudo().search([])
        product_attr = request.env['product.attribute'].sudo().search([])
        product_attr_val = request.env['product.attribute.value'].sudo().search([])
        return request.render("advanced_portal_user.portal_user_create_order", {'payment_terms': payment_terms, 'product_attr': product_attr, 'product_attr_val': product_attr_val})