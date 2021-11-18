# -*- coding: utf-8 -*-
import logging
import re
from odoo.exceptions import ValidationError
from odoo import _, api, fields, models, modules, SUPERUSER_ID, tools
from datetime import datetime
import datetime
import requests
import json
import urllib
import html2text
import urllib.request
import os
import base64

_logger = logging.getLogger(__name__)
_image_dataurl = re.compile(r'(data:image/[a-z]+?);base64,([a-z0-9+/]{3,}=*)([\'"])', re.I)


class HubspotImportIntegration(models.Model):
    _name = 'hubspot.import.integration'

    field_name = fields.Char('Hubspot')
    start = fields.Datetime('Start from')
    end = fields.Datetime('Till')

    import_company = fields.Boolean('Import companies', store=True)
    import_contact = fields.Boolean('Import contacts', store=True)
    import_deal = fields.Boolean('Import deals', store=True)
    import_ticket = fields.Boolean('Import tickets', store=True)
    custom_date_range = fields.Boolean(string='Custom Date Range Sync')
    company_last_offfssset = fields.Char("Company offset")
    contact_last_offsetss = fields.Char("Contact Offset")
    ticket_last_offsetss = fields.Char("Ticket Offset")

    def read_file(self, file_name):
        try:
            lines = []
            if file_name == 'contacts':
                lines = ['aapt_ar_','business_unit','demo',
                        'did_they_go_to_a_new_school_district_company_','iacp','lead_type','napt',
                        'no_longer_at_school_district_company','planned_retirement_date','population',
                        'product_i_m_interested_in','purchased_list_july','purchasing_influence','remove','reports_to',
                        'request_a_demo','role','s247_secondary_company','state_or_province',
                        'state_or_region','surveillance_247_area_code','surveillance_247_district_name',
                        'surveillance_247_district_website_domain','territory','what_school_district_company_did_they_go_',
                        'what_type_of_support','why_not_at_school_district_company_','years_with_company',
                        'zoom_webinar_attendance_average_duration','zoom_webinar_attendance_count','zoom_webinar_joinlink',
                        'zoom_webinar_registration_count','aasbo_az_','address2','asta_al_','casbo_ca_',
                        'casto_ca_','full_name','accounting_contact_full_name','cgcs','accounting_email','cptc_cn_',
                        'crtc_wa_','purchasing_contact_full_name','cspta_co_','purchasing_email','ctaa',
                        'division_cf_contact','fpta_ctd','gapt_ga_','last_rma_email_date',
                        'gcapt_tx_','famtec_customer','iapt_il_','famtec_sales_rep','iapt_id_',
                        'bus_garage','ipta_ia_','kspta_ks_','mapt_mi_','mapt_mo_','mnapt_mn_','n247_dvr_total','as_of_date',
                        'msboa_mn_','cameras','napt_na_','external_camera','ncpta_nc_','ncst','special_instructions',
                        'area_code','nsba_na_','job_title_secondary','nsta_mid','nsta_summer','unique_identifier',
                        'nsta_national','solution_currently_installed','oapt_oh_','oapt_ok_','oasbo_on_','oasbo_osba',
                        'opta_or_','osbma_oh_','sbx','scapt_sc_','sesptc','stai_in_','stn','taa_az_','tapt_tn_','tapt_tx_',
                        'transfinder','tsd','uapt_ut_','vapt_va_','wapt_wa_','wpta_wy_','wsba_wi_','wvapt_wv_',
                        'chapter_meeting_1','sts_of_nj']
            elif file_name == 'companies':
                lines = [
                    'bid_potential','bid_status','business_vertical','business_vertical_other_','camera_system',
                    'camera_system_other_','cameras','competitor','contract_expires','contracted_services',
                    'dealer_sold_through','e360_cameras','external_camera','fleet_maintenance_system',
                    'fleet_maintenance_system_other_','fleet_size_s247','gps','gps_vendor','gps_vendor_other_','how_many_lots_',
                    'issr','n247_bus_saleman','n247s_lifecycle_stage','netsuite_refresh','company_type',
                    'number_of_sales_personnel','number_of_special_needs_students_transported',
                    'of_buses','of_cameras_per_bus','of_students_total','of_students_transported',
                    'parent_portal','parent_portal_other_','parent_portal_system','preferred_camera_vendor','preferred_camera_vendor_cloned_',
                    'previous_camera_system','products','prospect_status_s247','purchase_date','purchased_list_july','remove','rfp_date_posted',
                    'routing','routing_solution','routing_solution_other_','rsm','s247_contact_email',
                    's247_county','s247_first_name','s247_last_name','s247_lead_contact','s247_pre_post_salutation','s247_title',
                    'sales_rep','school_year_budget_begins','school_year_start','service_agreement',
                    'sic_code','stop_arm_camera_s_','student_count','student_information_system','student_information_system_other_',
                    'student_tracking','student_tracking_system','student_tracking_system_other_','surveillance_247_company_domain',
                    'surveillance_247_district','system','td_fleet_monitor','territory','touchdown',
                    'touchdown_cloud_services_amount','touchdown_cloud_services_renewal_date','touchdown_install_date','wireless_s247',
                    'internal_id','new_id','lot_1_address','status','fleet_size','lot_2_address','netsuite_customer','netsuite_status',
                    'bid_awarded_year','bus_garage','n247_dvr_total','special_instructions','area_code','vendor',
                    'dealer_sub_type','unique_identifier','opportunity_number','contractor','minitrack','erie_1_boces','bid_reference',
                ]
            elif file_name == 'deals':
                lines = [
                    'deal_entered_current_deal_stage', 'dealers_quoting_this_deal', 'end_user', 'isr',
                    'lost_reason_notes', 'n247s_lifecycle_stage', 'opportunity_link', 'product_s_considered',
                    'sales_order', 'state', 'opportunity_number'
                ]
            elif file_name == 'tickets':
                lines = ['assigned_company', 'cs_number', 'product', 'pw_resolution', 'rn_number', 's247_resolution',
                         's247_product', 'touchdown']

            property_url = ''
            for line in lines:
                property_url = property_url + '&properties=' + line
            return property_url
        except Exception as e:
            raise ValidationError(str(e))

    def add_properties(self, odoo_obj, hubspot_obj, name, model):
        try:
            m2m_list = []
            date_fields = ['contract_expires', 'school_year_budget_begins', 'school_year_start',
                           'touchdown_cloud_services_renewal_date', 'touchdown_install_date', 'date_of_birth',
                           'planned_retirement_date', 'last_rma_email_date', 'request_a_demo',
                           'closedate', 'first_conversion_date', 'recent_conversion_date',
                           'first_contact_createdate', 'first_deal_created_date', 'notes_last_updated',
                           'hs_last_booked_meeting_date', 'notes_last_contacted', 'hs_last_logged_call_date',
                           'hs_lastmodifieddate', 'hs_last_open_task_date', 'hs_last_sales_activity_timestamp',
                           'hubspot_owner_assigneddate', 'recent_deal_close_date',
                           'hs_analytics_first_timestamp', 'hs_analytics_last_timestamp',
                           'hs_analytics_first_visit_timestamp', 'hs_analytics_last_visit_timestamp',
                           ]
            if name == 'contacts':
                m2m_list = [
                    'asta_al_', 'aasbo_az_', 'aapt_ar_',
                    'wvapt_wv_', 'wsba_wi_', 'wpta_wy_', 'wapt_wa_', 'vapt_va_', 'uapt_ut_',
                    'tsd', 'transfinder', 'tapt_tx_', 'tapt_tn_', 'taa_az_', 'sts_of_nj', 'stn',
                    'stai_in_', 'sesptc', 'scapt_sc_', 'sbx', 'osbma_oh_', 'opta_or_', 'oasbo_osba',
                    'oasbo_on_', 'oapt_ok_', 'oapt_oh_', 'nsta_summer', 'nsta_national', 'nsta_mid',
                    'nsba_na_', 'ncst', 'ncpta_nc_', 'napt_na_', 'napt', 'msboa_mn_', 'mnapt_mn_',
                    'mapt_mo_', 'mapt_mi_', 'kspta_ks_', 'ipta_ia_', 'iapt_il_', 'iapt_id_', 'gcapt_tx_',
                    'gapt_ga_', 'fpta_ctd', 'ctaa', 'cspta_co_', 'crtc_wa_', 'cptc_cn_', 'chapter_meeting_1',
                    'cgcs', 'casto_ca_', 'casbo_ca_', 'business_unit', 'buying_role', 'what_type_of_support'
                ]
            elif name == 'companies':
                m2m_list = ['system', 'dealer_sold_through', 'camera_system', 'how_many_lots_', 'competitor',
                            'previous_camera_system']
            elif name == 'deals':
                m2m_list = ['dealers_quoting_this_deal', 'product_s_considered']
            elif name == 'tickets':
                m2m_list = ['s247_product']
            else:
                print("hello")

            lines = []
            if name == 'contacts':
                lines = ['aapt_ar_', 'business_unit', 'demo',
                         'did_they_go_to_a_new_school_district_company_', 'iacp', 'lead_type',
                         'napt',
                         'no_longer_at_school_district_company', 'planned_retirement_date', 'population',
                         'product_i_m_interested_in', 'purchased_list_july', 'purchasing_influence', 'remove', 'reports_to',
                         'request_a_demo', 'role', 's247_secondary_company',
                         'state_or_province',
                         'state_or_region', 'surveillance_247_area_code', 'surveillance_247_district_name',
                         'surveillance_247_district_website_domain', 'territory',
                         'what_school_district_company_did_they_go_',
                         'what_type_of_support', 'why_not_at_school_district_company_', 'years_with_company',
                         'zoom_webinar_attendance_average_duration', 'zoom_webinar_attendance_count',
                         'zoom_webinar_joinlink',
                         'zoom_webinar_registration_count', 'aasbo_az_', 'address2', 'asta_al_', 'casbo_ca_',
                         'casto_ca_', 'accounting_contact_full_name', 'cgcs', 'accounting_email', 'cptc_cn_',
                         'crtc_wa_', 'purchasing_contact_full_name', 'cspta_co_', 'purchasing_email', 'ctaa',
                         'division_cf_contact', 'fpta_ctd', 'gapt_ga_', 'last_rma_email_date',
                         'gcapt_tx_', 'famtec_customer', 'iapt_il_', 'famtec_sales_rep', 'iapt_id_',
                         'bus_garage', 'ipta_ia_', 'kspta_ks_', 'mapt_mi_', 'mapt_mo_', 'mnapt_mn_', 'n247_dvr_total',
                         'as_of_date',
                         'msboa_mn_', 'cameras', 'napt_na_', 'external_camera', 'ncpta_nc_', 'ncst', 'special_instructions',
                         'area_code', 'nsba_na_', 'job_title_secondary', 'nsta_mid', 'nsta_summer', 'unique_identifier',
                         'nsta_national', 'solution_currently_installed', 'oapt_oh_', 'oapt_ok_', 'oasbo_on_', 'oasbo_osba',
                         'opta_or_', 'osbma_oh_', 'sbx', 'scapt_sc_', 'sesptc', 'stai_in_', 'stn', 'taa_az_', 'tapt_tn_',
                         'tapt_tx_',
                         'transfinder', 'tsd', 'uapt_ut_', 'vapt_va_', 'wapt_wa_', 'wpta_wy_', 'wsba_wi_', 'wvapt_wv_',
                         'chapter_meeting_1', 'sts_of_nj']
            elif name == 'companies':
                lines = [
                    'bid_potential', 'bid_status', 'business_vertical', 'business_vertical_other_', 'camera_system',
                    'camera_system_other_', 'cameras', 'competitor', 'contract_expires',
                    'contracted_services',
                    'dealer_sold_through', 'e360_cameras', 'external_camera', 'fleet_maintenance_system',
                    'fleet_maintenance_system_other_', 'fleet_size_s247', 'gps', 'gps_vendor', 'gps_vendor_other_',
                    'how_many_lots_',
                    'issr', 'n247_bus_saleman', 'n247s_lifecycle_stage', 'netsuite_refresh', 'company_type',
                    'number_of_sales_personnel', 'number_of_special_needs_students_transported',
                    'of_buses', 'of_cameras_per_bus', 'of_students_total',
                    'of_students_transported',
                    'parent_portal', 'parent_portal_other_', 'parent_portal_system', 'preferred_camera_vendor',
                    'preferred_camera_vendor_cloned_',
                    'previous_camera_system', 'products', 'prospect_status_s247', 'purchase_date', 'purchased_list_july',
                    'remove', 'rfp_date_posted',
                    'routing', 'routing_solution', 'routing_solution_other_', 'rsm', 's247_contact_email',
                    's247_county', 's247_first_name', 's247_last_name', 's247_lead_contact', 's247_pre_post_salutation',
                    's247_title',
                    'sales_rep', 'school_year_budget_begins', 'school_year_start', 'service_agreement',
                    'sic_code', 'stop_arm_camera_s_', 'student_count', 'student_information_system',
                    'student_information_system_other_',
                    'student_tracking', 'student_tracking_system', 'student_tracking_system_other_',
                    'surveillance_247_company_domain',
                    'surveillance_247_district', 'system', 'td_fleet_monitor', 'territory',
                    'touchdown',
                    'touchdown_cloud_services_amount', 'touchdown_cloud_services_renewal_date', 'touchdown_install_date',
                    'wireless_s247',
                    'internal_id', 'new_id', 'lot_1_address', 'status', 'fleet_size', 'lot_2_address', 'netsuite_customer',
                    'netsuite_status',
                    'bid_awarded_year', 'bus_garage', 'n247_dvr_total', 'special_instructions', 'area_code',
                    'vendor',
                    'dealer_sub_type', 'unique_identifier', 'opportunity_number', 'contractor', 'minitrack', 'erie_1_boces',
                    'bid_reference', 'about_us', 'closedate', 'description', 'facebook_company_page',
                    'facebookfans', 'first_conversion_event_name', 'first_conversion_date',
                    'hs_analytics_first_touch_converting_campaign', 'hs_ideal_customer_profile', 'is_public', 'nadp',
                    'hs_num_contacts_with_buying_roles', 'hs_num_decision_makers', 'numberofemployees',
                    'num_conversion_events', 'hs_num_open_deals', 'hs_analytics_num_page_views', 'hs_analytics_num_visits',
                    'num_contacted_notes', 'recent_conversion_event_name', 'recent_conversion_date',
                    'engagements_last_meeting_booked_source', 'total_revenue', 'founded_year',
                    # 'hs_analytics_last_touch_converting_campaign', 'engagements_last_meeting_booked_medium',
                    'hs_num_child_companies', 'recent_deal_amount', 'total_money_raised', 'hs_total_deal_value'
                    'hs_total_deal_value', 'number_of_buses', 'hubspot_team_id'
                ]
                # 'wireless''customer_rating'
            elif name == 'deals':
                lines = [
                    'deal_entered_current_deal_stage', 'dealers_quoting_this_deal', 'end_user', 'isr',
                    'lost_reason_notes', 'n247s_lifecycle_stage', 'opportunity_link', 'product_s_considered',
                    'sales_order', 'state', 'opportunity_number'
                ]
            elif name == 'tickets':
                lines = ['assigned_company', 'cs_number', 'product', 'pw_resolution', 'rn_number', 's247_resolution',
                         's247_product', 'touchdown']
            else:
                print("Hellossss")
            for line in lines:
                if hubspot_obj.get(line):
                    if line in m2m_list:
                        odoo_obj.update({
                            line: [[6, 0, self.add_m2m_values(hubspot_obj[line]['value'], line, model)]]
                        })
                    else:
                        if line in date_fields:
                            date_convert = hubspot_obj[line]['value']
                            date_value = datetime.datetime.fromtimestamp(int(date_convert[:-3]))
                            odoo_obj.update({
                                line: date_value
                            })
                        else:
                            if hubspot_obj[line]['value'] != 'false':
                                state_fields = ['state_or_province', 'state_or_region']
                                if line in state_fields:
                                    odoo_state = self.env['res.country.state'].search([('name', '=', hubspot_obj[line]['value'])])
                                    odoo_obj.update({
                                        line: odoo_state.id if odoo_state else None
                                    })
                                else:
                                    odoo_obj.update({
                                        line: hubspot_obj[line]['value'] if hubspot_obj[line]['value'] else None
                                    })
        except Exception as e:
            raise ValidationError(str(e))

    def add_m2m_values(self, values, line, model):
        try:
            value_ids = []
            fields = [
                    'asta_al_', 'aasbo_az_', 'aapt_ar_',
                    'wvapt_wv_', 'wsba_wi_', 'wpta_wy_', 'wapt_wa_', 'vapt_va_', 'uapt_ut_',
                    'tsd', 'transfinder', 'tapt_tx_', 'tapt_tn_', 'taa_az_', 'sts_of_nj', 'stn',
                    'stai_in_', 'sesptc', 'scapt_sc_', 'sbx', 'osbma_oh_', 'opta_or_', 'oasbo_osba',
                    'oasbo_on_', 'oapt_ok_', 'oapt_oh_', 'nsta_summer', 'nsta_national', 'nsta_mid',
                    'nsba_na_', 'ncst', 'ncpta_nc_', 'napt_na_', 'napt', 'msboa_mn_', 'mnapt_mn_',
                    'mapt_mo_', 'mapt_mi_', 'kspta_ks_', 'ipta_ia_', 'iapt_il_', 'iapt_id_', 'gcapt_tx_',
                    'gapt_ga_', 'fpta_ctd', 'ctaa', 'cspta_co_', 'crtc_wa_', 'cptc_cn_', 'chapter_meeting_1',
                    'cgcs', 'casto_ca_', 'casbo_ca_']
            if model == 'res.partner' and line in fields:
                for value in values.split(';'):
                    odoo_value = self.env['res.partner_years'].search([('name', '=', value)])
                    if not odoo_value:
                        odoo_value = self.env['res.partner_years'].create({
                            'name': value,
                        })
                    self.env.cr.commit()
                    value_ids.append(odoo_value.id)

            else:
                for value in values.split(';'):
                    odoo_value = self.env[str(model) + '_' + str(line)].search([('name', '=', value)])
                    if not odoo_value:
                        odoo_value = self.env[str(model) + '_' + str(line)].create({
                            'name': value,
                        })
                    self.env.cr.commit()
                    value_ids.append(odoo_value.id)
            return value_ids
        except Exception as e:
            raise ValidationError(str(e))

    def import_contacts(self):
        icpsudo = self.env['ir.config_parameter'].sudo()
        hubspot_keys = icpsudo.get_param('odoo_hubspot.hubspot_key')
        hubspot_ids = []
        if not hubspot_keys:
            raise ValidationError('Please! Enter Hubspot key...')
        else:
            try:
                get_all_contacts_url = "https://api.hubapi.com/contacts/v1/lists/all/contacts/all?"
                if self.contact_last_offsetss:
                    parameter_dict = {'hapikey': hubspot_keys, 'limit': 250, 'vidOffset': int(self.contact_last_offsetss)}
                else:
                    parameter_dict = {'hapikey': hubspot_keys, 'limit': 250}
                headers = {
                    'Accept': 'application/json',
                    'connection': 'keep-Alive'
                }
                has_more = True
                properties = self.read_file('contacts')
                while has_more:
                    parameters = urllib.parse.urlencode(parameter_dict)
                    get_url = get_all_contacts_url + parameters + properties
                    r = requests.get(url=get_url, headers=headers)
                    response_dict = json.loads(r.text)
                    hubspot_ids.extend(self.create_contacts(response_dict['contacts'], hubspot_keys))
                    has_more = response_dict['has-more']
                    parameter_dict['vidOffset'] = response_dict['vid-offset']
                    self.contact_last_offsetss = response_dict['vid-offset']
                # return hubspot_ids
            except Exception as e:
                _logger.error(e)
                raise ValidationError(_(str(e)))

    def create_contacts(self, contacts, hubspot_keys):
        try:
            hubspot_ids = []
            get_single_contact_url = "https://api.hubapi.com/contacts/v1/contact/vid/"
            get_single_company_url = "https://api.hubapi.com/companies/v2/companies/"
            headers = {
                'Accept': 'application/json',
                'connection': 'keep-Alive'
            }
            for contact in contacts:
                odoo_company = None
                odoo_country = None
                state_id = None
                contact_url = get_single_contact_url + str(contact['vid']) + '/profile?hapikey=' + hubspot_keys
                r = requests.get(url=contact_url, headers=headers)
                profile = json.loads(r.text)['properties']

                if 'associatedcompanyid' in profile and not profile['associatedcompanyid']['value'] == '':
                    odoo_company = self.env['res.partner'].search([('hubspot_id', '=', str(profile['associatedcompanyid']['value']))])
                    if not odoo_company:
                        get_url = get_single_company_url + str(profile['associatedcompanyid']['value']) + '?hapikey=' + hubspot_keys
                        company_response = requests.get(url=get_url, headers=headers)
                        company_profile = json.loads(company_response.content.decode('utf-8'))['properties']
                        if 'country' in company_profile.keys():
                            odoo_country = self.env['res.country'].search([('name', '=', company_profile['country']['value'])]).id
                        if company_profile.get('state', None):
                            state = company_profile['state']
                            if state.get('value', None):
                                state_code = state['value']
                                odoo_state = self.env['res.country.state'].search(
                                    [('code', '=', state_code), ('country_id', '=', odoo_country)]
                                )
                                if len(odoo_state) == 1:
                                    state_id = odoo_state.id
                        company_values = {
                            'name': company_profile['name']['value'] if 'name' in company_profile.keys() else '',
                            'website': company_profile['website']['value'] if 'website' in company_profile.keys() else '',
                            'street': company_profile['address']['value'] if 'address' in company_profile.keys() else '',
                            'city': company_profile['city']['value'] if 'city' in company_profile.keys() else '',
                            'phone': company_profile['phone']['value'] if 'phone' in company_profile.keys() else '',
                            'zip': company_profile['zip']['value'] if 'zip' in company_profile.keys() else '',
                            'country_id': odoo_country if odoo_country else None,
                            'hubspot_id': str(profile['associatedcompanyid']['value']),
                            'is_company': True,
                        }
                        self.add_properties(company_values, company_profile, 'companies', 'res.partner')
                        odoo_company = self.env['res.partner'].create(company_values)
                first_name = profile['firstname']['value'] if 'firstname' in profile else ''
                last_name = profile['lastname']['value'] if 'lastname' in profile else ''
                name = first_name + ' ' + last_name
                odoo_partner = self.env['res.partner'].search([('hubspot_id', '=', str(contact['vid']))])

                contact_values = {
                    'name': name,
                    'email': profile['email']['value'] if 'email' in profile.keys() else '',
                    'website': profile['website']['value'] if 'website' in profile.keys() else '',
                    'city': profile['city']['value'] if 'city' in profile.keys() else '',
                    'zip': profile['zip']['value'] if 'zip' in profile.keys() else '',
                    'parent_id': odoo_company.id if odoo_company else None,
                    'hubspot_id': str(contact['vid']),
                    'phone': profile['phone']['value'] if 'phone' in profile.keys() else '',
                    'country_id': odoo_country if odoo_country else None,
                    'state_id': state_id,
                }
                self.add_properties(contact_values, profile, 'contacts', 'res.partner')
                if not odoo_partner:
                    new_contact = self.env['res.partner'].create(contact_values)
                else:
                    odoo_partner.write(contact_values)
                self.env.cr.commit()
                hubspot_ids.append(contact['vid'])
            return hubspot_ids
        except Exception as e:
            _logger.error(e)
            raise ValidationError(_(str(e)))

    def import_companies(self):
        icpsudo = self.env['ir.config_parameter'].sudo()
        hubspot_keys = icpsudo.get_param('odoo_hubspot.hubspot_key')
        hubspot_ids = []
        if not hubspot_keys:
            raise ValidationError('Please! Enter Hubspot key...')
        else:
            try:
                get_all_companies_url = "https://api.hubapi.com/companies/v2/companies/paged?"
                if self.company_last_offfssset:
                    parameter_dict = {'hapikey': hubspot_keys, 'limit': 250, 'offset': int(self.company_last_offfssset)}
                else:
                    parameter_dict = {'hapikey': hubspot_keys, 'limit': 250}
                headers = {
                    'Accept': 'application/json',
                    'connection': 'keep-Alive'
                }
                properties = self.read_file('companies')
                has_more = True
                while has_more:
                    parameters = urllib.parse.urlencode(parameter_dict)
                    get_url = get_all_companies_url + parameters + properties
                    r = requests.get(url=get_url, headers=headers)
                    response_dict = json.loads(r.text)
                    hubspot_ids.extend(self.create_companies(response_dict['companies'], hubspot_keys))
                    has_more = response_dict['has-more']
                    parameter_dict['offset'] = response_dict['offset']
                    self.company_last_offfssset = response_dict['offset']
            except Exception as e:
                raise ValidationError(_(str(e)))

    def create_companies(self, companies, hubspot_keys):
        try:
            hubspot_ids = []
            get_single_company_url = "https://api.hubapi.com/companies/v2/companies/"
            headers = {
                'Accept': 'application/json',
                'connection': 'keep-Alive'
            }
            for company in companies:
                odoo_country = None
                state_id = None
                get_url = get_single_company_url + str(company['companyId']) + '?hapikey=' + hubspot_keys
                company_response = requests.get(url=get_url, headers=headers)
                company_data = json.loads(company_response.content.decode('utf-8'))
                if 'properties' in company_data:
                    company_profile = company_data['properties']

                    odoo_company = self.env['res.partner'].search([('hubspot_id', '=', str(company['companyId']))])
                    if 'country' in company_profile.keys():
                        odoo_country = self.env['res.country'].search([('name', '=', company_profile['country']['value'])]).id
                    if company_profile.get('state', None):
                        state = company_profile['state']
                        if state.get('value', None):
                            state_code = state['value']
                            odoo_state = self.env['res.country.state'].search(
                                [('code', '=', state_code), ('country_id', '=', odoo_country)]
                            )
                            if len(odoo_state) == 1:
                                state_id = odoo_state.id
                    company_values = {
                        'name': company_profile['name']['value'] if 'name' in company_profile.keys() else '',
                        'website': company_profile['website']['value'] if 'website' in company_profile.keys() else '',
                        'street': company_profile['address']['value'] if 'address' in company_profile.keys() else '',
                        'city': company_profile['city']['value'] if 'city' in company_profile.keys() else '',
                        'phone': company_profile['phone']['value'] if 'phone' in company_profile.keys() else '',
                        'zip': company_profile['zip']['value'] if 'zip' in company_profile.keys() else '',
                        'country_id': odoo_country if odoo_country else None,
                        'state_id': state_id,
                        'hubspot_id': str(company['companyId']),
                        'is_company': True,
                    }
                    self.add_properties(company_values, company_profile, 'companies', 'res.partner')
                    if not odoo_company:
                        self.env['res.partner'].create(company_values)
                    else:
                        odoo_company.write(company_values)
                    self.env.cr.commit()
                    hubspot_ids.append(company['companyId'])
            return hubspot_ids
        except Exception as e:
            raise ValidationError((str(e)))

    def import_deals(self,):
        icpsudo = self.env['ir.config_parameter'].sudo()
        hubspot_keys = icpsudo.get_param('odoo_hubspot.hubspot_key')
        hubspot_ids = []
        if not hubspot_keys:
            raise ValidationError('Please! Enter Hubspot key...')
        else:
            try:
                get_all_deals_url = "https://api.hubapi.com/deals/v1/deal/paged?"
                deal_properties = "&includeAssociations=true&properties=dealstage&properties=dealname" \
                                  "&properties=hs_createdate&properties=hubspot_owner_id&properties=dealtype" \
                                  "&properties=closedate&properties=amount&properties=hs_lastmodifieddate"
                parameter_dict = {'hapikey': hubspot_keys, 'limit': 250}
                headers = {
                    'Accept': 'application/json',
                    'connection': 'keep-Alive'
                }
                has_more = True
                while has_more:
                    parameters = urllib.parse.urlencode(parameter_dict)
                    get_url = get_all_deals_url + parameters + deal_properties
                    r = requests.get(url=get_url, headers=headers)
                    response_dict = json.loads(r.text)
                    hubspot_ids.extend(self.create_deals(response_dict['deals'], hubspot_keys))
                    has_more = response_dict['hasMore']
                    parameter_dict['offset'] = response_dict['offset']
                # return hubspot_ids
            except Exception as e:
                _logger.error(e)
                raise ValidationError(_(str(e)))

    def create_deals(self, deals, hubspot_keys):
        try:
            hubspot_ids = []
            close_date = None
            deal_stage = None
            i = 0
            for deal in deals:
                contacts = []
                companies = []
                if len(deal['associations']['associatedVids']) > 0:
                    contacts = self.get_contacts(deal['associations']['associatedVids'], hubspot_keys)
                if len(deal['associations']['associatedCompanyIds']) > 0:
                    companies = self.get_companies(deal['associations']['associatedCompanyIds'], hubspot_keys)
                odoo_deal = self.env['crm.lead'].search([('hubspot_id', '=', str(deal['dealId']))])
                # if 'dealstage' in deal['properties'].keys():
                #     deal_stage = self.env['crm.stage'].search([('name', '=', deal['properties']['dealstage']['value'])])
                #     if not deal_stage:
                #         deal_stage = self.env['crm.stage'].create({
                #             'name': deal['properties']['dealstage']['value'],
                #             'display_name': deal['properties']['dealstage']['value'],
                #         })
                if 'closedate' in deal['properties'].keys():
                    if deal['properties']['closedate']['value'] != "":
                        close_date = datetime.datetime.fromtimestamp(int(deal['properties']['closedate']['value'][:-3]))

                deal_values = {
                    'hubspot_id': str(deal['dealId']),
                    'name': deal['properties']['dealname']['value'],
                    'expected_revenue': deal['properties']['amount']['value'] if 'amount' in deal[
                        'properties'].keys() else None,
                    # 'stage_id': deal_stage.id if deal_stage else self.env['crm.stage'].search(
                    #     [('name', '=', 'New')]).id,
                    'date_closed': close_date if close_date else None,
                    'hs_deal_contacts': [[6, 0, contacts]] if contacts else None,
                    'hs_deal_companies': companies[0] if companies else None,
                    'type': 'opportunity'
                }

                self.add_properties(deal_values, deal, 'deals', 'crm.lead')
                if not odoo_deal:
                    self.env['crm.lead'].create(deal_values)
                else:
                    odoo_deal.write(deal_values)
                self.env.cr.commit()

                hubspot_ids.append(deal['dealId'])
            return hubspot_ids
        except Exception as e:
            raise ValidationError(_(str(e)))

    def get_contacts(self, contactsIds, hubspot_keys):
        contact_list = []
        get_single_contact_url = "https://api.hubapi.com/contacts/v1/contact/vid/"
        headers = {
            'Accept': 'application/json',
            'connection': 'keep-Alive'
        }
        for contactId in contactsIds:
            contact_url = get_single_contact_url + str(contactId) + '/profile?hapikey=' + hubspot_keys
            r = requests.get(url=contact_url, headers=headers)
            profile = json.loads(r.text)['properties']
            first_name = profile['firstname']['value'] if 'firstname' in profile else ''
            last_name = profile['lastname']['value'] if 'lastname' in profile else ''
            name = first_name + ' ' + last_name
            odoo_partner = self.env['res.partner'].search([('hubspot_id', '=', str(contactId))])
            if not odoo_partner:
                odoo_partner = self.env['res.partner'].create({
                    'name': name,
                    'email': profile['email']['value'] if 'email' in profile.keys() else '',
                    'website': profile['website']['value'] if 'website' in profile.keys() else '',
                    'city': profile['city']['value'] if 'city' in profile.keys() else '',
                    'zip': profile['zip']['value'] if 'zip' in profile.keys() else '',
                    'hubspot_id': str(contactId),
                    'phone': profile['phone']['value'] if 'phone' in profile.keys() else '',
                })
            else:
                odoo_partner.write({
                    'name': name,
                    'email': profile['email']['value'] if 'email' in profile.keys() else '',
                    'website': profile['website']['value'] if 'website' in profile.keys() else '',
                    'city': profile['city']['value'] if 'city' in profile.keys() else '',
                    'zip': profile['zip']['value'] if 'zip' in profile.keys() else '',
                    'hubspot_id': str(contactId),
                    'phone': profile['phone']['value'] if 'phone' in profile.keys() else '',
                })
            contact_list.append(odoo_partner.id)
        return contact_list

    def get_companies(self, companiesIds, hubspot_keys):
        company_list = []
        get_single_company_url = "https://api.hubapi.com/companies/v2/companies/"
        headers = {
            'Accept': 'application/json',
            'connection': 'keep-Alive'
        }
        for companyId in companiesIds:
            odoo_country = None
            get_url = get_single_company_url + str(companyId) + '?hapikey=' + hubspot_keys
            company_response = requests.get(url=get_url, headers=headers)
            company_profile = json.loads(company_response.content.decode('utf-8'))['properties']
            odoo_company = self.env['res.partner'].search([('hubspot_id', '=', str(companyId))])
            if 'country' in company_profile.keys():
                odoo_country = self.env['res.country'].search([('name', '=', company_profile['country']['value'])]).id
            if not odoo_company:
                odoo_company = self.env['res.partner'].create({
                    'name': company_profile['name']['value'] if 'name' in company_profile.keys() else '',
                    'website': company_profile['website']['value'] if 'website' in company_profile.keys() else '',
                    'street': company_profile['address']['value'] if 'address' in company_profile.keys() else '',
                    'city': company_profile['city']['value'] if 'city' in company_profile.keys() else '',
                    'phone': company_profile['phone']['value'] if 'phone' in company_profile.keys() else '',
                    'zip': company_profile['zip']['value'] if 'zip' in company_profile.keys() else '',
                    'country_id': odoo_country if odoo_country else None,
                    'hubspot_id': str(companyId),
                    'is_company': True,
                })
            else:
                odoo_company.write({
                    'name': company_profile['name']['value'] if 'name' in company_profile.keys() else '',
                    'website': company_profile['website']['value'] if 'website' in company_profile.keys() else '',
                    'street': company_profile['address']['value'] if 'address' in company_profile.keys() else '',
                    'city': company_profile['city']['value'] if 'city' in company_profile.keys() else '',
                    'phone': company_profile['phone']['value'] if 'phone' in company_profile.keys() else '',
                    'zip': company_profile['zip']['value'] if 'zip' in company_profile.keys() else '',
                    'country_id': odoo_country if odoo_country else None,
                    'hubspot_id': str(companyId),
                    'is_company': True,
                })
            company_list.append(odoo_company.id)
        return company_list

    def import_tickets(self):
        icpsudo = self.env['ir.config_parameter'].sudo()
        hubspot_keys = icpsudo.get_param('odoo_hubspot.hubspot_key')
        hubspot_ids = []
        if not hubspot_keys:
            raise ValidationError('Please! Enter Hubspot key...')
        else:
            try:
                get_all_tickets_url = "https://api.hubapi.com/crm-objects/v1/objects/tickets/paged?"
                data = "&properties=subject&properties=content&properties=hs_pipeline" \
                       "&properties=hs_pipeline_stage&properties=hs_ticket_priority" \
                       "&properties=hs_ticket_category&properties=hubspot_owner_id" \
                       "&properties=source_type&properties=hs_createdate&properties=createdate" \
                       "&properties=hs_lastmodifieddate"
                if self.ticket_last_offsetss:
                    parameter_dict = {'hapikey': hubspot_keys, 'limit': 250, 'offset': int(self.ticket_last_offsetss)}
                else:
                    parameter_dict = {'hapikey': hubspot_keys, 'limit': 250}
                headers = {
                    'Accept': 'application/json',
                    'connection': 'keep-Alive'
                }
                properties = self.read_file('tickets')
                has_more = True
                while has_more:
                    parameters = urllib.parse.urlencode(parameter_dict)
                    get_url = get_all_tickets_url + parameters + data + properties
                    r = requests.get(url=get_url, headers=headers)
                    response_dict = json.loads(r.text)
                    hubspot_ids.extend(self.create_tickets(response_dict['objects'], hubspot_keys))
                    has_more = response_dict['hasMore']
                    parameter_dict['offset'] = response_dict['offset']
                    self.ticket_last_offsetss = response_dict['offset']
                # return hubspot_ids
            except Exception as e:
                _logger.error(e)
                raise ValidationError(_(str(e)))

    def create_tickets(self, tickets, hubspot_keys):
        try:
            hubspot_ids = []
            get_association_url = 'https://api.hubapi.com/crm-associations/v1/associations/'
            headers = {
                'Accept': 'application/json',
                'connection': 'keep-Alive'
            }
            for ticket in tickets:
                contacts = []
                companies = []
                tag_ids = []
                priority = None
                get_ticket_contact_url = get_association_url + str(ticket['objectId']) + '/HUBSPOT_DEFINED/16?hapikey=' + hubspot_keys
                contact_response = requests.get(url=get_ticket_contact_url, headers=headers)
                contact_info = json.loads(contact_response.content.decode('utf-8'))['results']
                contacts = self.get_contacts(contact_info, hubspot_keys)
                get_ticket_company_url = get_association_url + str(
                    ticket['objectId']) + '/HUBSPOT_DEFINED/26?hapikey=' + hubspot_keys
                company_response = requests.get(url=get_ticket_company_url, headers=headers)
                company_info = json.loads(company_response.content.decode('utf-8'))['results']
                companies = self.get_companies(company_info, hubspot_keys)
                if 'source_type' in ticket['properties']:
                    odoo_type = self.env['helpdesk.ticket.type'].search([('name', '=', ticket['properties']['source_type']['value'])])
                    if not odoo_type:
                        odoo_type = self.env['helpdesk.ticket.type'].create({
                            'name': ticket['properties']['source_type']['value'],
                        })
                odoo_stage = None
                # if 'hs_pipeline_stage' in ticket['properties']:
                #     odoo_stage = self.env['helpdesk.stage'].search([('name', '=', ticket['properties']['hs_pipeline_stage']['value'])])
                #     if not odoo_stage:
                #         odoo_stage = self.env['helpdesk.stage'].create({
                #             'name': ticket['properties']['hs_pipeline_stage']['value'],
                #         })
                if 'hs_ticket_category' in ticket['properties']:
                    tags = ticket['properties']['hs_ticket_category']['value'].split(';')
                    for tag in tags:
                        odoo_tag = self.env['helpdesk.tag'].search([('name', '=', tag)])
                        if not odoo_tag:
                            odoo_tag = self.env['helpdesk.tag'].create({
                                'name': tag,
                            })
                        tag_ids.append(odoo_tag.id)
                if 'hs_ticket_priority' in ticket['properties']:
                    if ticket['properties']['hs_ticket_priority']['value'] == 'LOW':
                        priority = '1'
                    elif ticket['properties']['hs_ticket_priority']['value'] == 'MEDIUM':
                        priority = '2'
                    elif ticket['properties']['hs_ticket_priority']['value'] == 'HIGH':
                        priority = '3'
                    else:
                        priority = '0'

                odoo_ticket = self.env['helpdesk.ticket'].search([('hubspot_id', '=', str(ticket['objectId']))])
                ticket_values = {
                    'hubspot_id': str(ticket['objectId']),
                    'name': ticket['properties']['subject']['value'] if 'subject' in ticket['properties'] else " ",
                    'priority': priority,
                    # 'stage_id': odoo_stage.id if odoo_stage else None,
                    'ticket_type_id': odoo_type.id,
                    'tag_ids': [[6, 0, tag_ids]],
                    'hs_ticket_contacts': [[6, 0, contacts]] if contacts else None,
                    'hs_ticket_company': companies[0] if companies else None,
                }
                self.add_properties(ticket_values, ticket['properties'], 'tickets', 'helpdesk.ticket')

                if not odoo_ticket:
                    self.env['helpdesk.ticket'].create(ticket_values)
                else:
                    odoo_ticket.write(ticket_values)
                self.env.cr.commit()
                hubspot_ids.append(ticket['objectId'])
            return hubspot_ids
        except Exception as e:
            raise ValidationError(_(str(e)))

    def get_company_engagements(self):
        try:
            icpsudo = self.env['ir.config_parameter'].sudo()
            hubspot_keys = icpsudo.get_param('odoo_hubspot.hubspot_key')
            companies = self.env['res.partner'].search([('hubspot_id', '!=', False),
                                                        ('is_company', '=', True),
                                                        ('engagement_done', '=', True)]
            )
            for odoo_company in companies:
                get_associated_engagement_url = "https://api.hubapi.com/engagements/v1/engagements/associated/" \
                                                "COMPANY/{0}/paged?".format(odoo_company.hubspot_id)
                parameter_dict = {'hapikey': hubspot_keys, 'limit': 100}
                headers = {
                    'Accept': 'application/json',
                    'connection': 'keep-Alive'
                }
                has_more = True
                while has_more:
                    parameters = urllib.parse.urlencode(parameter_dict)
                    get_url = get_associated_engagement_url + parameters
                    response = requests.get(url=get_url, headers=headers)
                    res_data = json.loads(response.content.decode("utf-8"))
                    engagements = res_data['results']
                    for engagement in engagements:
                        engagement_data = engagement['engagement']
                        odoo_message = self.env['mail.message'].search([('engagement_id', '=', engagement_data['id'])])
                        odoo_activity = self.env['mail.activity'].search([('engagement_id', '=', engagement_data['id'])])
                        if odoo_message or odoo_activity:
                            self.env['log.handling'].create({
                                'record_id': engagement_data['id'],
                                'odoo_record_name': odoo_company.name,
                                'description': 'Record already exists',
                                'skip': False,
                                'model': 'Company-res.partner',
                            })
                            self.env.cr.commit()
                            continue
                        association_data = engagement['associations']
                        meta_data = engagement['metadata']
                        if engagement_data['type'] in ['EMAIL', 'INCOMING_EMAIL']:
                            if not meta_data.get('from'):
                                self.env['log.handling'].create({
                                    'record_id': engagement_data['id'],
                                    'description': 'Coming engagement email type has no \'from\' that is why skipped',
                                    'skip': True,
                                    'model': 'res.partner',
                                })
                                self.env.cr.commit()
                                continue
                            try:
                                print('Creating Email Engagement against the company', odoo_company.name)
                                author = self.env['res.partner'].search([('email', '=', meta_data['from']['email'])])
                                if len(author) > 1:
                                    author = author[0]
                                odoo_comment = self.env['mail.message'].create({
                                    'engagement_id': engagement_data['id'],
                                    'message_type': 'email',
                                    'body': meta_data['text'],
                                    'create_date': datetime.datetime.fromtimestamp(
                                        int(str(engagement_data['createdAt'])[:-3])),
                                    'display_name': author.name if author.name else None,
                                    'email_from': meta_data['from'],
                                    # comment.author.email if comment.author.email else None,
                                    'author_id': author.id if author else None,
                                    'model': 'res.partner',
                                    'res_id': odoo_company.id
                                })
                                self.env.cr.commit()
                                self.env['log.handling'].create({
                                    'record_id': engagement_data['id'],
                                    'odoo_record_name': odoo_company.name,
                                    'description': 'Email: New Created',
                                    'skip': False,
                                    'model': 'Company-res.partner',
                                })
                                self.env.cr.commit()
                            except Exception as e:
                                self.env['log.handling'].create({
                                    'record_id': engagement_data['id'],
                                    'odoo_record_name': odoo_company.name,
                                    'description': 'EMAIL: Skipped because of error while creating(' + str(e) + ')',
                                    'skip': True,
                                    'model': 'Company-res.partner',
                                })
                                self.env.cr.commit()
                                pass
                        # elif engagement_data['type'] == 'NOTE':
                        #     try:
                        #         print('Creating Note Engagement against the company', odoo_company.name)
                        #         author_id = self.env['res.users'].search([('hubspot_id', '=', engagement_data['ownerId'])]).partner_id
                        #         odoo_comment = self.env['mail.message'].create({
                        #             'engagement_id': engagement_data['id'],
                        #             'message_type': 'notification',
                        #             'body': engagement_data['bodyPreview'] if engagement_data.get('bodyPreview') else None,
                        #             'create_date': datetime.datetime.fromtimestamp(
                        #                 int(str(engagement_data['createdAt'])[:-3])),
                        #             'display_name': author_id.name if author_id.name else None,
                        #             'author_id': author_id.id,
                        #             'model': 'res.partner',
                        #             'res_id': odoo_company.id
                        #         })
                        #         self.env.cr.commit()
                        #         self.env['log.handling'].create({
                        #             'record_id': engagement_data['id'],
                        #             'odoo_record_name': odoo_company.name,
                        #             'description': 'Note: New Created',
                        #             'skip': False,
                        #             'model': 'Company-res.partner',
                        #         })
                        #         self.env.cr.commit()
                        #     except Exception as e:
                        #         self.env['log.handling'].create({
                        #             'record_id': engagement_data['id'],
                        #             'odoo_record_name': odoo_company.name,
                        #             'description': 'NOTE: Skipped because of error while creating(' + str(e) + ')',
                        #             'skip': True,
                        #             'model': 'Company-res.partner',
                        #         })
                        #         self.env.cr.commit()
                        #         pass
                        # elif engagement_data['type'] == 'TASK':
                        #     try:
                        #         print('Creating TASK Engagement against the company', odoo_company.name)
                        #         if meta_data['status'] != 'COMPLETED':
                        #             print(odoo_company.name)
                        #             user_id = self.env['res.users'].search([('hubspot_id', '=', engagement_data['ownerId'])])
                        #             activity_type = self.env['mail.activity.type'].search([('name', '=', 'Todo')])
                        #             partner_model = self.env['ir.model'].search([('model', '=', 'res.partner')])
                        #             self.env['mail.activity'].create({
                        #                 'engagement_id': engagement_data['id'],
                        #                 'res_id': odoo_company.id,
                        #                 'activity_type_id': activity_type.id,
                        #                 'summary': meta_data['subject'],
                        #                 'hubspot_status': meta_data['status'],
                        #                 'note': meta_data['body'] if meta_data.get('body') else None,
                        #                 'forObjectType': meta_data['forObjectType'],
                        #                 'res_model_id': partner_model.id,
                        #                 'date_deadline': datetime.datetime.fromtimestamp(
                        #                     int(str(meta_data['completionDate'])[:-3])) if meta_data.get(
                        #                     'completionDate') else datetime.datetime.now(),
                        #                 'user_id': user_id.id if user_id else self.env.user.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_company.name,
                        #                 'description': 'Task: New Created',
                        #                 'skip': False,
                        #                 'model': 'Company-res.partner',
                        #             })
                        #             self.env.cr.commit()
                        #         else:
                        #             print('message created for task', odoo_company.name)
                        #             author_id = self.env['res.users'].search([('hubspot_id', '=', engagement_data['ownerId'])]).partner_id
                        #             odoo_comment = self.env['mail.message'].create({
                        #                 'engagement_id': engagement_data['id'],
                        #                 'message_type': 'comment',
                        #                 # 'from': odoo_contact.email,
                        #                 'body': meta_data['body'] if meta_data.get('body') else meta_data['subject'],
                        #                 'create_date': datetime.datetime.fromtimestamp(
                        #                     int(str(engagement_data['createdAt'])[:-3])),
                        #                 'display_name': author_id.name if author_id.name else None,
                        #                 'author_id': author_id.id,
                        #                 'model': 'res.partner',
                        #                 'res_id': odoo_company.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_company.name,
                        #                 'description': 'Task: New Created(Completed)',
                        #                 'skip': False,
                        #                 'model': 'Company-res.partner',
                        #             })
                        #             self.env.cr.commit()
                        #     except Exception as e:
                        #         self.env['log.handling'].create({
                        #             'record_id': engagement_data['id'],
                        #             'odoo_record_name': odoo_company.name,
                        #             'description': 'TASK: Skipped because of error while creating(' + str(e) + ')',
                        #             'skip': True,
                        #             'model': 'Company-res.partner',
                        #         })
                        #         self.env.cr.commit()
                        #         pass
                        # elif engagement_data['type'] == 'CALL':
                        #     try:
                        #         print('Creating Call Engagement against the company', odoo_company.name)
                        #         if meta_data['status'] != 'COMPLETED':
                        #             print(odoo_company.name)
                        #             user_id = self.env['res.users'].search(
                        #                 [('hubspot_id', '=', engagement_data['ownerId'])])
                        #             activity_type = self.env['mail.activity.type'].search([('name', '=', 'Call')])
                        #             partner_model = self.env['ir.model'].search([('model', '=', 'res.partner')])
                        #             self.env['mail.activity'].create({
                        #                 'engagement_id': engagement_data['id'],
                        #                 'res_id': odoo_company.id,
                        #                 'activity_type_id': activity_type.id,
                        #                 'summary': meta_data['subject'] if meta_data.get('subject') else meta_data[
                        #                     'body'] if meta_data.get('body') else None,
                        #                 'hubspot_status': meta_data['status'],
                        #                 'note': html2text.html2text(meta_data['body']) if meta_data.get('body') else None,
                        #                 'toNumber': meta_data['toNumber'] if meta_data.get('toNumber') else None,
                        #                 'fromNumber': meta_data['fromNumber'] if meta_data.get('fromNumber') else None,
                        #                 'durationMilliseconds': str(meta_data['durationMilliseconds']) if meta_data.get(
                        #                     'durationMilliseconds') else None,
                        #                 'recordingUrl': meta_data['recordingUrl'] if meta_data.get(
                        #                     'recordingUrl') else None,
                        #                 'disposition': meta_data['disposition'] if meta_data.get('disposition') else None,
                        #                 'res_model_id': partner_model.id,
                        #                 'date_deadline': datetime.datetime.fromtimestamp(
                        #                     int(str(meta_data['completionDate'])[:-3])) if meta_data.get(
                        #                     'completionDate') else datetime.datetime.now(),
                        #                 'user_id': user_id.id if user_id else self.env.user.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_company.name,
                        #                 'description': 'Call: New Created',
                        #                 'skip': False,
                        #                 'model': 'Company-res.partner',
                        #             })
                        #             self.env.cr.commit()
                        #         else:
                        #             print('message created for call', odoo_company.name)
                        #             author_id = self.env['res.users'].search([('hubspot_id', '=', engagement_data['ownerId'])]).partner_id
                        #             odoo_comment = self.env['mail.message'].create({
                        #                 'message_type': 'comment',
                        #                 'engagement_id': engagement_data['id'],
                        #                 'body': meta_data['body'] if meta_data.get('body') else meta_data[
                        #                     'subject'] if meta_data.get('subject') else None,
                        #                 'create_date': datetime.datetime.fromtimestamp(
                        #                     int(str(engagement_data['createdAt'])[:-3])),
                        #                 'display_name': author_id.name if author_id.name else None,
                        #                 'author_id': author_id.id,
                        #                 'model': 'res.partner',
                        #                 'res_id': odoo_company.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_company.name,
                        #                 'description': 'Call: New Created(Completed)',
                        #                 'skip': False,
                        #                 'model': 'Company-res.partner',
                        #             })
                        #             self.env.cr.commit()
                        #     except Exception as e:
                        #         self.env['log.handling'].create({
                        #             'record_id': engagement_data['id'],
                        #             'odoo_record_name': odoo_company.name,
                        #             'description': 'CALL: Skipped because of error while creating(' + str(e) + ')',
                        #             'skip': True,
                        #             'model': 'Company-res.partner',
                        #         })
                        #         self.env.cr.commit()
                        #         pass
                        #
                        # elif engagement_data['type'] == 'MEETING':
                        #     try:
                        #         print('Creating Meeting Engagement against the company', odoo_company.name)
                        #         end_time = datetime.datetime.fromtimestamp(int(str(meta_data['endTime'])[:-3]))
                        #         if end_time > datetime.datetime.now():
                        #             print(odoo_company.name)
                        #             user_id = self.env['res.users'].search(
                        #                 [('hubspot_id', '=', engagement_data['ownerId'])])
                        #             activity_type = self.env['mail.activity.type'].search([('name', '=', 'Meeting')])
                        #             partner_model = self.env['ir.model'].search([('model', '=', 'res.partner')])
                        #             self.env['mail.activity'].create({
                        #                 'engagement_id': engagement_data['id'],
                        #                 'res_id': odoo_company.id,
                        #                 'activity_type_id': activity_type.id,
                        #                 'summary': meta_data['title'] if meta_data.get('title') else meta_data[
                        #                     'body'] if meta_data.get('body') else None,
                        #                 'note': meta_data['body'] if meta_data.get('body') else None,
                        #                 'startTime': datetime.datetime.fromtimestamp(
                        #                     int(str(meta_data['startTime'])[:-3])) if meta_data.get(
                        #                     'startTime') else datetime.datetime.now(),
                        #                 'endTime': datetime.datetime.fromtimestamp(
                        #                     int(str(meta_data['endTime'])[:-3])) if meta_data.get(
                        #                     'endTime') else datetime.datetime.now(),
                        #                 'res_model_id': partner_model.id,
                        #                 'date_deadline': datetime.datetime.fromtimestamp(
                        #                     int(str(meta_data['endTime'])[:-3])) if meta_data.get(
                        #                     'endTime') else datetime.datetime.now(),
                        #                 'user_id': user_id.id if user_id else self.env.user.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_company.name,
                        #                 'description': 'Meeting: New Created',
                        #                 'skip': False,
                        #                 'model': 'Company-res.partner',
                        #             })
                        #             self.env.cr.commit()
                        #         else:
                        #             print('message created for call', odoo_company.name)
                        #             author_id = self.env['res.users'].search([('hubspot_id', '=', engagement_data['ownerId'])]).partner_id
                        #             odoo_comment = self.env['mail.message'].create({
                        #                 'engagement_id': engagement_data['id'],
                        #                 'message_type': 'comment',
                        #                 'body': meta_data['body'] if meta_data.get('body') else meta_data['title'],
                        #                 'create_date': datetime.datetime.fromtimestamp(
                        #                     int(str(engagement_data['createdAt'])[:-3])),
                        #                 'display_name': author_id.name if author_id.name else None,
                        #                 'author_id': author_id.id,
                        #                 'model': 'res.partner',
                        #                 'res_id': odoo_company.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_company.name,
                        #                 'description': 'Meeting: New Created(Completed)',
                        #                 'skip': False,
                        #                 'model': 'Company-res.partner',
                        #             })
                        #             self.env.cr.commit()
                        #     except Exception as e:
                        #         self.env['log.handling'].create({
                        #             'record_id': engagement_data['id'],
                        #             'odoo_record_name': odoo_company.name,
                        #             'description': 'MEETING: Skipped because of error while creating(' + str(e) + ')',
                        #             'skip': True,
                        #             'model': 'Company-res.partner',
                        #         })
                        #         self.env.cr.commit()
                        #         pass

                    has_more = res_data['hasMore']
                    parameter_dict['offset'] = res_data['offset']
                odoo_company.write({
                    'engagement_done': False,
                })
                self.env.cr.commit()
        except Exception as e:
            pass

    def get_lead_engagements(self):
        try:
            icpsudo = self.env['ir.config_parameter'].sudo()
            hubspot_keys = icpsudo.get_param('odoo_hubspot.hubspot_key')
            leads = self.env['crm.lead'].search([('hubspot_id', '!=', False),
                                                 ('type', '=', 'opportunity'),
                                                 ('engagement_done', '=', True)])
            for odoo_lead in leads:
                get_associated_engagement_url = "https://api.hubapi.com/engagements/v1/engagements/associated/" \
                                                "DEAL/{0}/paged?".format(odoo_lead.hubspot_id)
                parameter_dict = {'hapikey': hubspot_keys, 'limit': 100}
                headers = {
                    'Accept': 'application/json',
                    'connection': 'keep-Alive'
                }
                has_more = True
                while has_more:
                    parameters = urllib.parse.urlencode(parameter_dict)
                    get_url = get_associated_engagement_url + parameters
                    response = requests.get(url=get_url, headers=headers)
                    res_data = json.loads(response.content.decode("utf-8"))
                    engagements = res_data['results']
                    for engagement in engagements:
                        engagement_data = engagement['engagement']
                        odoo_message = self.env['mail.message'].search([('engagement_id', '=', engagement_data['id'])])
                        odoo_activity = self.env['mail.activity'].search([('engagement_id', '=', engagement_data['id'])])
                        if odoo_message or odoo_activity:
                            self.env['log.handling'].create({
                                'record_id': engagement_data['id'],
                                'odoo_record_name': odoo_lead.name,
                                'description': 'Record already exists',
                                'skip': False,
                                'model': 'Deal-crm.lead',
                            })
                            self.env.cr.commit()
                            continue
                        association_data = engagement['associations']
                        meta_data = engagement['metadata']
                        if engagement_data['type'] in ['EMAIL', 'INCOMING_EMAIL']:
                            if not meta_data.get('from'):
                                self.env['log.handling'].create({
                                    'record_id': engagement_data['id'],
                                    'odoo_record_name': odoo_lead.name,
                                    'description': 'Coming engagement email type has no \'from\' that is why skipped',
                                    'skip': True,
                                    'model': 'Deal-crm.lead',
                                })
                                self.env.cr.commit()
                                continue
                            try:
                                author = self.env['res.partner'].search([('email', '=', meta_data['from']['email'])])
                                if len(author) > 1:
                                    author = author[0]
                                odoo_comment = self.env['mail.message'].create({
                                    'engagement_id': engagement_data['id'],
                                    'message_type': 'email',
                                    'body': meta_data['text'] if meta_data.get('text') else '',
                                    'create_date': datetime.datetime.fromtimestamp(
                                        int(str(engagement_data['createdAt'])[:-3])),
                                    'display_name': author.name if author.name else None,
                                    'email_from': meta_data['from'],
                                    # comment.author.email if comment.author.email else None,
                                    'author_id': author.id if author else None,
                                    'model': 'crm.lead',
                                    'res_id': odoo_lead.id
                                })
                                self.env.cr.commit()
                                self.env['log.handling'].create({
                                    'record_id': engagement_data['id'],
                                    'odoo_record_name': odoo_lead.name,
                                    'description': 'Email: New Created',
                                    'skip': False,
                                    'model': 'Deal-crm.lead',
                                })
                                self.env.cr.commit()
                            except Exception as e:
                                self.env['log.handling'].create({
                                    'record_id': engagement_data['id'],
                                    'odoo_record_name': odoo_lead.name,
                                    'description': 'EMAIL: Skipped because of error while creating(' + str(e) + ')',
                                    'skip': True,
                                    'model': 'Deal-crm.lead',
                                })
                                self.env.cr.commit()
                                pass
                        # elif engagement_data['type'] == 'NOTE':
                        #     try:
                        #         print('Creating Note Engagement against the company', odoo_lead.name)
                        #         author_id = self.env['res.users'].search(
                        #             [('hubspot_id', '=', engagement_data['ownerId'])]).partner_id
                        #
                        #         odoo_comment = self.env['mail.message'].create({
                        #             'engagement_id': engagement_data['id'],
                        #             'message_type': 'notification',
                        #             'body': engagement_data['bodyPreview'] if engagement_data.get('bodyPreview') else None,
                        #             'create_date': datetime.datetime.fromtimestamp(
                        #                 int(str(engagement_data['createdAt'])[:-3])),
                        #             'display_name': author_id.name if author_id.name else None,
                        #             'author_id': author_id.id,
                        #             'model': 'crm.lead',
                        #             'res_id': odoo_lead.id
                        #         })
                        #         self.env.cr.commit()
                        #         self.env['log.handling'].create({
                        #             'record_id': engagement_data['id'],
                        #             'odoo_record_name': odoo_lead.name,
                        #             'description': 'Note: New Created',
                        #             'skip': False,
                        #             'model': 'Deal-crm.lead',
                        #         })
                        #         self.env.cr.commit()
                        #     except Exception as e:
                        #         self.env['log.handling'].create({
                        #             'record_id': engagement_data['id'],
                        #             'odoo_record_name': odoo_lead.name,
                        #             'description': 'NOTE: Skipped because of error while creating(' + str(e) + ')',
                        #             'skip': True,
                        #             'model': 'Deal-crm.lead',
                        #         })
                        #         self.env.cr.commit()
                        #         pass
                        # elif engagement_data['type'] == 'TASK':
                        #     try:
                        #         print('Creating TASK Engagement against the lead', odoo_lead.name)
                        #         if meta_data['status'] != 'COMPLETED':
                        #             print(odoo_lead.name)
                        #             user_id = self.env['res.users'].search([('hubspot_id', '=', engagement_data['ownerId'])])
                        #             activity_type = self.env['mail.activity.type'].search([('name', '=', 'Todo')])
                        #             partner_model = self.env['ir.model'].search([('model', '=', 'crm.lead')])
                        #             self.env['mail.activity'].create({
                        #                 'engagement_id': engagement_data['id'],
                        #                 'res_id': odoo_lead.id,
                        #                 'activity_type_id': activity_type.id,
                        #                 'summary': meta_data['subject'],
                        #                 'hubspot_status': meta_data['status'],
                        #                 'note': meta_data['body'] if meta_data.get('body') else None,
                        #                 'forObjectType': meta_data['forObjectType'],
                        #                 'res_model_id': partner_model.id,
                        #                 'date_deadline': datetime.datetime.fromtimestamp(
                        #                     int(str(meta_data['completionDate'])[:-3])) if meta_data.get(
                        #                     'completionDate') else datetime.datetime.now(),
                        #                 'create_date': datetime.datetime.fromtimestamp(
                        #                     int(str(engagement_data['createdAt'])[:-3])),
                        #                 'user_id': user_id.id if user_id else self.env.user.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_lead.name,
                        #                 'description': 'Task: New Created',
                        #                 'skip': False,
                        #                 'model': 'Deal-crm.lead',
                        #             })
                        #             self.env.cr.commit()
                        #         else:
                        #             print('message created for task', odoo_lead.name)
                        #             author_id = self.env['res.users'].search(
                        #                 [('hubspot_id', '=', engagement_data['ownerId'])]).partner_id
                        #
                        #             odoo_comment = self.env['mail.message'].create({
                        #                 'engagement_id': engagement_data['id'],
                        #                 'message_type': 'comment',
                        #                 # 'from': odoo_contact.email,
                        #                 'body': meta_data['body'] if meta_data.get('body') else meta_data['subject'],
                        #                 'create_date': datetime.datetime.fromtimestamp(
                        #                     int(str(engagement_data['createdAt'])[:-3])),
                        #                 'display_name': author_id.name if author_id.name else None,
                        #                 'author_id': author_id.id,
                        #                 'model': 'crm.lead',
                        #                 'res_id': odoo_lead.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_lead.name,
                        #                 'description': 'Task: New Created(Completed)',
                        #                 'skip': False,
                        #                 'model': 'Deal-crm.lead',
                        #             })
                        #             self.env.cr.commit()
                        #     except Exception as e:
                        #         self.env['log.handling'].create({
                        #             'record_id': engagement_data['id'],
                        #             'odoo_record_name': odoo_lead.name,
                        #             'description': 'TASK: Skipped because of error while creating(' + str(e) + ')',
                        #             'skip': True,
                        #             'model': 'Deal-crm.lead',
                        #         })
                        #         self.env.cr.commit()
                        #         pass
                        # elif engagement_data['type'] == 'CALL':
                        #     try:
                        #         print('Creating Call Engagement against the lead', odoo_lead.name)
                        #         if meta_data['status'] != 'COMPLETED':
                        #             print(odoo_lead.name)
                        #             user_id = self.env['res.users'].search(
                        #                 [('hubspot_id', '=', engagement_data['ownerId'])])
                        #             activity_type = self.env['mail.activity.type'].search([('name', '=', 'Call')])
                        #             partner_model = self.env['ir.model'].search([('model', '=', 'crm.lead')])
                        #             self.env['mail.activity'].create({
                        #                 'engagement_id': engagement_data['id'],
                        #                 'res_id': odoo_lead.id,
                        #                 'activity_type_id': activity_type.id,
                        #                 'summary': meta_data['subject'] if meta_data.get('subject') else meta_data[
                        #                     'body'] if meta_data.get('body') else None,
                        #                 'hubspot_status': meta_data['status'],
                        #                 'note': html2text.html2text(meta_data['body']) if meta_data.get('body') else None,
                        #                 'toNumber': meta_data['toNumber'] if meta_data.get('toNumber') else None,
                        #                 'fromNumber': meta_data['fromNumber'] if meta_data.get('fromNumber') else None,
                        #                 'durationMilliseconds': str(meta_data['durationMilliseconds']) if meta_data.get(
                        #                     'durationMilliseconds') else None,
                        #                 'recordingUrl': meta_data['recordingUrl'] if meta_data.get(
                        #                     'recordingUrl') else None,
                        #                 'disposition': meta_data['disposition'] if meta_data.get('disposition') else None,
                        #                 'res_model_id': partner_model.id,
                        #                 'date_deadline': datetime.datetime.fromtimestamp(
                        #                     int(str(meta_data['completionDate'])[:-3])) if meta_data.get(
                        #                     'completionDate') else datetime.datetime.now(),
                        #                 'create_date': datetime.datetime.fromtimestamp(
                        #                     int(str(engagement_data['createdAt'])[:-3])),
                        #                 'user_id': user_id.id if user_id else self.env.user.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_lead.name,
                        #                 'description': 'Call: New Created',
                        #                 'skip': False,
                        #                 'model': 'Deal-crm.lead',
                        #             })
                        #             self.env.cr.commit()
                        #         else:
                        #             print('message created for call', odoo_lead.name)
                        #             author_id = self.env['res.users'].search(
                        #                 [('hubspot_id', '=', engagement_data['ownerId'])]).partner_id
                        #
                        #             odoo_comment = self.env['mail.message'].create({
                        #                 'message_type': 'comment',
                        #                 'engagement_id': engagement_data['id'],
                        #                 'body': meta_data['body'] if meta_data.get('body') else meta_data[
                        #                     'subject'] if meta_data.get('subject') else None,
                        #                 'create_date': datetime.datetime.fromtimestamp(
                        #                     int(str(engagement_data['createdAt'])[:-3])),
                        #                 'display_name': author_id.name if author_id.name else None,
                        #                 'author_id': author_id.id,
                        #                 'model': 'crm.lead',
                        #                 'res_id': odoo_lead.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_lead.name,
                        #                 'description': 'Call: New Created(Completed)',
                        #                 'skip': False,
                        #                 'model': 'Deal-crm.lead',
                        #             })
                        #             self.env.cr.commit()
                        #     except Exception as e:
                        #         self.env['log.handling'].create({
                        #             'record_id': engagement_data['id'],
                        #             'odoo_record_name': odoo_lead.name,
                        #             'description': 'CALL: Skipped because of error while creating(' + str(e) + ')',
                        #             'skip': True,
                        #             'model': 'Deal-crm.lead',
                        #         })
                        #         self.env.cr.commit()
                        #         pass
                        #
                        # elif engagement_data['type'] == 'MEETING':
                        #     try:
                        #         print('Creating Meeting Engagement against the lead', odoo_lead.name)
                        #         end_time = datetime.datetime.fromtimestamp(int(str(meta_data['endTime'])[:-3]))
                        #         if end_time > datetime.datetime.now():
                        #             print(odoo_lead.name)
                        #             user_id = self.env['res.users'].search(
                        #                 [('hubspot_id', '=', engagement_data['ownerId'])])
                        #             activity_type = self.env['mail.activity.type'].search([('name', '=', 'Meeting')])
                        #             partner_model = self.env['ir.model'].search([('model', '=', 'crm.lead')])
                        #             self.env['mail.activity'].create({
                        #                 'engagement_id': engagement_data['id'],
                        #                 'res_id': odoo_lead.id,
                        #                 'activity_type_id': activity_type.id,
                        #                 'summary': meta_data['title'] if meta_data.get('title') else meta_data[
                        #                     'body'] if meta_data.get('body') else None,
                        #                 'note': meta_data['body'] if meta_data.get('body') else None,
                        #                 'startTime': datetime.datetime.fromtimestamp(
                        #                     int(str(meta_data['startTime'])[:-3])) if meta_data.get(
                        #                     'startTime') else datetime.datetime.now(),
                        #                 'endTime': datetime.datetime.fromtimestamp(
                        #                     int(str(meta_data['endTime'])[:-3])) if meta_data.get(
                        #                     'endTime') else datetime.datetime.now(),
                        #                 'res_model_id': partner_model.id,
                        #                 'date_deadline': datetime.datetime.fromtimestamp(
                        #                     int(str(meta_data['endTime'])[:-3])) if meta_data.get(
                        #                     'endTime') else datetime.datetime.now(),
                        #                 'create_date': datetime.datetime.fromtimestamp(
                        #                     int(str(engagement_data['createdAt'])[:-3])),
                        #                 'user_id': user_id.id if user_id else self.env.user.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_lead.name,
                        #                 'description': 'Meeting: New Created',
                        #                 'skip': False,
                        #                 'model': 'Deal-crm.lead',
                        #             })
                        #             self.env.cr.commit()
                        #         else:
                        #             print('message created for call', odoo_lead.name)
                        #             author_id = self.env['res.users'].search(
                        #                 [('hubspot_id', '=', engagement_data['ownerId'])]).partner_id
                        #
                        #             odoo_comment = self.env['mail.message'].create({
                        #                 'engagement_id': engagement_data['id'],
                        #                 'message_type': 'comment',
                        #                 'body': meta_data['body'] if meta_data.get('body') else meta_data['title'],
                        #                 'create_date': datetime.datetime.fromtimestamp(
                        #                     int(str(engagement_data['createdAt'])[:-3])),
                        #                 'display_name': author_id.name if author_id.name else None,
                        #                 'author_id': author_id.id,
                        #                 'model': 'crm.lead',
                        #                 'res_id': odoo_lead.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_lead.name,
                        #                 'description': 'Meeting: New Created(Completed)',
                        #                 'skip': False,
                        #                 'model': 'Deal-crm.lead',
                        #             })
                        #             self.env.cr.commit()
                        #     except Exception as e:
                        #         self.env['log.handling'].create({
                        #             'record_id': engagement_data['id'],
                        #             'odoo_record_name': odoo_lead.name,
                        #             'description': 'MEETING: Skipped because of error while creating(' + str(e) + ')',
                        #             'skip': True,
                        #             'model': 'Deal-crm.lead',
                        #         })
                        #         self.env.cr.commit()
                        #         pass

                    has_more = res_data['hasMore']
                    parameter_dict['offset'] = res_data['offset']

                odoo_lead.write({
                    'engagement_done': False,
                })
                self.env.cr.commit()
        except Exception as e:
            pass

    def get_ticket_engagements(self):
        try:
            icpsudo = self.env['ir.config_parameter'].sudo()
            hubspot_keys = icpsudo.get_param('odoo_hubspot.hubspot_key')
            tickets = self.env['helpdesk.ticket'].search([('hubspot_id', '!=', False),
                                                          ('engagement_done', '=', True)])
            for odoo_ticket in tickets:
                get_associated_engagement_url = "https://api.hubapi.com/engagements/v1/engagements/associated/" \
                                                "TICKET/{0}/paged?".format(odoo_ticket.hubspot_id)
                parameter_dict = {'hapikey': hubspot_keys, 'limit': 100}
                headers = {
                    'Accept': 'application/json',
                    'connection': 'keep-Alive'
                }
                has_more = True
                while has_more:
                    parameters = urllib.parse.urlencode(parameter_dict)
                    get_url = get_associated_engagement_url + parameters
                    response = requests.get(url=get_url, headers=headers)
                    res_data = json.loads(response.content.decode("utf-8"))
                    engagements = res_data['results']
                    for engagement in engagements:
                        engagement_data = engagement['engagement']
                        odoo_message = self.env['mail.message'].search([('engagement_id', '=', engagement_data['id'])])
                        odoo_activity = self.env['mail.activity'].search([('engagement_id', '=', engagement_data['id'])])
                        if odoo_message or odoo_activity:
                            self.env['log.handling'].create({
                                'record_id': engagement_data['id'],
                                'odoo_record_name': odoo_ticket.name,
                                'description': 'Record already exists',
                                'skip': False,
                                'model': 'Ticket-helpdesk.ticket',
                            })
                            self.env.cr.commit()
                            continue
                        association_data = engagement['associations']
                        meta_data = engagement['metadata']
                        if engagement_data['type'] in ['EMAIL', 'INCOMING_EMAIL']:
                            if not meta_data.get('from'):
                                self.env['log.handling'].create({
                                    'record_id': engagement_data['id'],
                                    'odoo_record_name': odoo_ticket.name,
                                    'description': 'Coming engagement email type has no \'from\' that is why skipped',
                                    'skip': True,
                                    'model': 'Ticket-helpdesk.ticket',
                                })
                                self.env.cr.commit()
                                continue
                            try:
                                author = self.env['res.partner'].search([('email', '=', meta_data['from']['email'])])
                                if len(author) > 1:
                                    author = author[0]
                                odoo_comment = self.env['mail.message'].create({
                                    'engagement_id': engagement_data['id'],
                                    'message_type': 'email',
                                    'body': meta_data['text'] if meta_data.get('text') else '',
                                    'create_date': datetime.datetime.fromtimestamp(
                                        int(str(engagement_data['createdAt'])[:-3])),
                                    'display_name': author.name if author.name else None,
                                    'email_from': meta_data['from'],
                                    # comment.author.email if comment.author.email else None,
                                    'author_id': author.id if author else None,
                                    'model': 'helpdesk.ticket',
                                    'res_id': odoo_ticket.id
                                })
                                self.env.cr.commit()
                                self.env['log.handling'].create({
                                    'record_id': engagement_data['id'],
                                    'odoo_record_name': odoo_ticket.name,
                                    'description': 'Email: New Created',
                                    'skip': False,
                                    'model': 'Ticket-helpdesk.ticket',
                                })
                                self.env.cr.commit()
                            except Exception as e:
                                self.env['log.handling'].create({
                                    'record_id': engagement_data['id'],
                                    'odoo_record_name': odoo_ticket.name,
                                    'description': 'EMAIL: Skipped because of error while creating(' + str(e) + ')',
                                    'skip': True,
                                    'model': 'Ticket-helpdesk.ticket',
                                })
                                self.env.cr.commit()
                                pass
                        # elif engagement_data['type'] == 'NOTE':
                        #     try:
                        #         print('Creating Note Engagement against the company', odoo_ticket.name)
                        #         author_id = self.env['res.users'].search(
                        #             [('hubspot_id', '=', engagement_data['ownerId'])]).partner_id
                        #
                        #         odoo_comment = self.env['mail.message'].create({
                        #             'engagement_id': engagement_data['id'],
                        #             'message_type': 'notification',
                        #             'body': engagement_data['bodyPreview'] if engagement_data.get('bodyPreview') else None,
                        #             'create_date': datetime.datetime.fromtimestamp(
                        #                 int(str(engagement_data['createdAt'])[:-3])),
                        #             'display_name': author_id.name if author_id.name else None,
                        #             'author_id': author_id.id,
                        #             'model': 'helpdesk.ticket',
                        #             'res_id': odoo_ticket.id
                        #         })
                        #         self.env.cr.commit()
                        #         self.env['log.handling'].create({
                        #             'record_id': engagement_data['id'],
                        #             'odoo_record_name': odoo_ticket.name,
                        #             'description': 'Note: New Created',
                        #             'skip': False,
                        #             'model': 'Ticket-helpdesk.ticket',
                        #         })
                        #         self.env.cr.commit()
                        #     except Exception as e:
                        #         self.env['log.handling'].create({
                        #             'record_id': engagement_data['id'],
                        #             'odoo_record_name': odoo_ticket.name,
                        #             'description': 'NOTE: Skipped because of error while creating(' + str(e) + ')',
                        #             'skip': True,
                        #             'model': 'Ticket-helpdesk.ticket',
                        #         })
                        #         self.env.cr.commit()
                        #         pass
                        # elif engagement_data['type'] == 'TASK':
                        #     try:
                        #         print('Creating TASK Engagement against the lead', odoo_ticket.name)
                        #         if meta_data['status'] != 'COMPLETED':
                        #             print(odoo_ticket.name)
                        #             user_id = self.env['res.users'].search(
                        #                 [('hubspot_id', '=', engagement_data['ownerId'])])
                        #             activity_type = self.env['mail.activity.type'].search([('name', '=', 'Todo')])
                        #             partner_model = self.env['ir.model'].search([('model', '=', 'helpdesk.ticket')])
                        #             self.env['mail.activity'].create({
                        #                 'engagement_id': engagement_data['id'],
                        #                 'res_id': odoo_ticket.id,
                        #                 'activity_type_id': activity_type.id,
                        #                 'summary': meta_data['subject'],
                        #                 'hubspot_status': meta_data['status'],
                        #                 'note': meta_data['body'] if meta_data.get('body') else None,
                        #                 'forObjectType': meta_data['forObjectType'],
                        #                 'res_model_id': partner_model.id,
                        #                 'date_deadline': datetime.datetime.fromtimestamp(
                        #                     int(str(meta_data['completionDate'])[:-3])) if meta_data.get(
                        #                     'completionDate') else datetime.datetime.now(),
                        #                 'create_date': datetime.datetime.fromtimestamp(
                        #                     int(str(engagement_data['createdAt'])[:-3])),
                        #                 'user_id': user_id.id if user_id else self.env.user.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_ticket.name,
                        #                 'description': 'Task: New Created',
                        #                 'skip': False,
                        #                 'model': 'Ticket-helpdesk.ticket',
                        #             })
                        #             self.env.cr.commit()
                        #         else:
                        #             print('message created for task', odoo_ticket.name)
                        #             author_id = self.env['res.users'].search(
                        #                 [('hubspot_id', '=', engagement_data['ownerId'])]).partner_id
                        #             odoo_comment = self.env['mail.message'].create({
                        #                 'engagement_id': engagement_data['id'],
                        #                 'message_type': 'comment',
                        #                 # 'from': odoo_contact.email,
                        #                 'body': meta_data['body'] if meta_data.get('body') else meta_data['subject'],
                        #                 'create_date': datetime.datetime.fromtimestamp(
                        #                     int(str(engagement_data['createdAt'])[:-3])),
                        #                 'display_name': author_id.name if author_id.name else None,
                        #                 'author_id': author_id.id,
                        #                 'model': 'helpdesk.ticket',
                        #                 'res_id': odoo_ticket.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_ticket.name,
                        #                 'description': 'Task: New Created(Completed)',
                        #                 'skip': False,
                        #                 'model': 'Ticket-helpdesk.ticket',
                        #             })
                        #             self.env.cr.commit()
                        #     except Exception as e:
                        #         self.env['log.handling'].create({
                        #             'record_id': engagement_data['id'],
                        #             'odoo_record_name': odoo_ticket.name,
                        #             'description': 'TASK: Skipped because of error while creating(' + str(e) + ')',
                        #             'skip': True,
                        #             'model': 'Ticket-helpdesk.ticket',
                        #         })
                        #         self.env.cr.commit()
                        #         pass
                        # elif engagement_data['type'] == 'CALL':
                        #     try:
                        #         print('Creating Call Engagement against the lead', odoo_ticket.name)
                        #         if meta_data['status'] != 'COMPLETED':
                        #             print(odoo_ticket.name)
                        #             user_id = self.env['res.users'].search(
                        #                 [('hubspot_id', '=', engagement_data['ownerId'])])
                        #             activity_type = self.env['mail.activity.type'].search([('name', '=', 'Call')])
                        #             partner_model = self.env['ir.model'].search([('model', '=', 'helpdesk.ticket')])
                        #             self.env['mail.activity'].create({
                        #                 'engagement_id': engagement_data['id'],
                        #                 'res_id': odoo_ticket.id,
                        #                 'activity_type_id': activity_type.id,
                        #                 'summary': meta_data['subject'] if meta_data.get('subject') else meta_data[
                        #                     'body'] if meta_data.get('body') else None,
                        #                 'hubspot_status': meta_data['status'],
                        #                 'note': html2text.html2text(meta_data['body']) if meta_data.get('body') else None,
                        #                 'toNumber': meta_data['toNumber'] if meta_data.get('toNumber') else None,
                        #                 'fromNumber': meta_data['fromNumber'] if meta_data.get('fromNumber') else None,
                        #                 'durationMilliseconds': str(meta_data['durationMilliseconds']) if meta_data.get(
                        #                     'durationMilliseconds') else None,
                        #                 'recordingUrl': meta_data['recordingUrl'] if meta_data.get(
                        #                     'recordingUrl') else None,
                        #                 'disposition': meta_data['disposition'] if meta_data.get('disposition') else None,
                        #                 'res_model_id': partner_model.id,
                        #                 'date_deadline': datetime.datetime.fromtimestamp(
                        #                     int(str(meta_data['completionDate'])[:-3])) if meta_data.get(
                        #                     'completionDate') else datetime.datetime.now(),
                        #                 'create_date': datetime.datetime.fromtimestamp(
                        #                     int(str(engagement_data['createdAt'])[:-3])),
                        #                 'user_id': user_id.id if user_id else self.env.user.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_ticket.name,
                        #                 'description': 'Call: New Created',
                        #                 'skip': False,
                        #                 'model': 'Ticket-helpdesk.ticket',
                        #             })
                        #             self.env.cr.commit()
                        #         else:
                        #             print('message created for call', odoo_ticket.name)
                        #             author_id = self.env['res.users'].search(
                        #                 [('hubspot_id', '=', engagement_data['ownerId'])]).partner_id
                        #             odoo_comment = self.env['mail.message'].create({
                        #                 'message_type': 'comment',
                        #                 'engagement_id': engagement_data['id'],
                        #                 'body': meta_data['body'] if meta_data.get('body') else meta_data[
                        #                     'subject'] if meta_data.get('subject') else None,
                        #                 'create_date': datetime.datetime.fromtimestamp(
                        #                     int(str(engagement_data['createdAt'])[:-3])),
                        #                 'display_name': author_id.name if author_id.name else None,
                        #                 'author_id': author_id.id,
                        #                 'model': 'helpdesk.ticket',
                        #                 'res_id': odoo_ticket.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_ticket.name,
                        #                 'description': 'Call: New Created(Completed)',
                        #                 'skip': False,
                        #                 'model': 'Ticket-helpdesk.ticket',
                        #             })
                        #             self.env.cr.commit()
                        #     except Exception as e:
                        #         self.env['log.handling'].create({
                        #             'record_id': engagement_data['id'],
                        #             'odoo_record_name': odoo_ticket.name,
                        #             'description': 'CALL: Skipped because of error while creating(' + str(e) + ')',
                        #             'skip': True,
                        #             'model': 'Ticket-helpdesk.ticket',
                        #         })
                        #         self.env.cr.commit()
                        #         pass
                        #
                        # elif engagement_data['type'] == 'MEETING':
                        #     try:
                        #         print('Creating Meeting Engagement against the lead', odoo_ticket.name)
                        #         end_time = datetime.datetime.fromtimestamp(int(str(meta_data['endTime'])[:-3]))
                        #         if end_time > datetime.datetime.now():
                        #             print(odoo_ticket.name)
                        #             user_id = self.env['res.users'].search(
                        #                 [('hubspot_id', '=', engagement_data['ownerId'])])
                        #             activity_type = self.env['mail.activity.type'].search([('name', '=', 'Meeting')])
                        #             partner_model = self.env['ir.model'].search([('model', '=', 'helpdesk.ticket')])
                        #             self.env['mail.activity'].create({
                        #                 'engagement_id': engagement_data['id'],
                        #                 'res_id': odoo_ticket.id,
                        #                 'activity_type_id': activity_type.id,
                        #                 'summary': meta_data['title'] if meta_data.get('title') else meta_data[
                        #                     'body'] if meta_data.get('body') else None,
                        #                 'note': meta_data['body'] if meta_data.get('body') else None,
                        #                 'startTime': datetime.datetime.fromtimestamp(
                        #                     int(str(meta_data['startTime'])[:-3])) if meta_data.get(
                        #                     'startTime') else datetime.datetime.now(),
                        #                 'endTime': datetime.datetime.fromtimestamp(
                        #                     int(str(meta_data['endTime'])[:-3])) if meta_data.get(
                        #                     'endTime') else datetime.datetime.now(),
                        #                 'res_model_id': partner_model.id,
                        #                 'date_deadline': datetime.datetime.fromtimestamp(
                        #                     int(str(meta_data['endTime'])[:-3])) if meta_data.get(
                        #                     'endTime') else datetime.datetime.now(),
                        #                 'create_date': datetime.datetime.fromtimestamp(
                        #                     int(str(engagement_data['createdAt'])[:-3])),
                        #                 'user_id': user_id.id if user_id else self.env.user.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_ticket.name,
                        #                 'description': 'Meeting: New Created',
                        #                 'skip': False,
                        #                 'model': 'Ticket-helpdesk.ticket',
                        #             })
                        #             self.env.cr.commit()
                        #         else:
                        #             print('message created for call', odoo_ticket.name)
                        #             author_id = self.env['res.users'].search(
                        #                 [('hubspot_id', '=', engagement_data['ownerId'])]).partner_id
                        #             odoo_comment = self.env['mail.message'].create({
                        #                 'engagement_id': engagement_data['id'],
                        #                 'message_type': 'comment',
                        #                 'body': meta_data['body'] if meta_data.get('body') else meta_data['title'],
                        #                 'create_date': datetime.datetime.fromtimestamp(
                        #                     int(str(engagement_data['createdAt'])[:-3])),
                        #                 'display_name': author_id.name if author_id.name else None,
                        #                 'author_id': author_id.id,
                        #                 'model': 'helpdesk.ticket',
                        #                 'res_id': odoo_ticket.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_ticket.name,
                        #                 'description': 'Meeting: New Created(Completed)',
                        #                 'skip': False,
                        #                 'model': 'Ticket-helpdesk.ticket',
                        #             })
                        #             self.env.cr.commit()
                        #     except Exception as e:
                        #         self.env['log.handling'].create({
                        #             'record_id': engagement_data['id'],
                        #             'odoo_record_name': odoo_ticket.name,
                        #             'description': 'MEETING: Skipped because of error while creating(' + str(e) + ')',
                        #             'skip': True,
                        #             'model': 'Ticket-helpdesk.ticket',
                        #         })
                        #         self.env.cr.commit()
                        #         pass

                    has_more = res_data['hasMore']
                    parameter_dict['offset'] = res_data['offset']

                odoo_ticket.write({
                    'engagement_done': False,
                })
                self.env.cr.commit()
        except Exception as e:
            pass

    def get_contact_engagements(self):
        try:
            icpsudo = self.env['ir.config_parameter'].sudo()
            hubspot_keys = icpsudo.get_param('odoo_hubspot.hubspot_key')
            contacts = self.env['res.partner'].search([('hubspot_id', '!=', False),
                                                       ('is_company', '=', False),
                                                       ('engagement_done', '=', True)])

            for odoo_contact in contacts:
                get_associated_engagement_url = "https://api.hubapi.com/engagements/v1/engagements/associated/" \
                                                "CONTACT/{0}/paged?".format(odoo_contact.hubspot_id)
                parameter_dict = {'hapikey': hubspot_keys, 'limit': 100}
                headers = {
                    'Accept': 'application/json',
                    'connection': 'keep-Alive'
                }
                has_more = True
                while has_more:
                    parameters = urllib.parse.urlencode(parameter_dict)
                    get_url = get_associated_engagement_url + parameters
                    response = requests.get(url=get_url, headers=headers)
                    res_data = json.loads(response.content.decode("utf-8"))
                    engagements = res_data['results']
                    for engagement in engagements:
                        engagement_data = engagement['engagement']
                        odoo_message = self.env['mail.message'].search([('engagement_id', '=', engagement_data['id'])])
                        odoo_activity = self.env['mail.activity'].search([('engagement_id', '=', engagement_data['id'])])
                        if odoo_message or odoo_activity:
                            self.env['log.handling'].create({
                                'record_id': engagement_data['id'],
                                'odoo_record_name': odoo_contact.name,
                                'description': 'Record already exists',
                                'skip': False,
                                'model': 'Contact-res.partner',
                            })
                            self.env.cr.commit()
                            continue
                        association_data = engagement['associations']
                        meta_data = engagement['metadata']
                        if engagement_data['type'] in ['EMAIL', 'INCOMING_EMAIL']:
                            if not meta_data.get('from'):
                                self.env['log.handling'].create({
                                    'record_id': engagement_data['id'],
                                    'odoo_record_name': odoo_contact.name,
                                    'description': 'Coming engagement email type has no \'from\' that is why skipped',
                                    'skip': True,
                                    'model': 'Contact-res.partner',
                                })
                                self.env.cr.commit()
                                continue
                            try:
                                author = self.env['res.partner'].search([('email', '=', meta_data['from']['email'])])
                                if len(author) > 1:
                                    author = author[0]

                                odoo_comment = self.env['mail.message'].create({
                                    'engagement_id': engagement_data['id'],
                                    'message_type': 'email',
                                    'body': meta_data['text'] if meta_data.get('text') else '',
                                    'create_date': datetime.datetime.fromtimestamp(
                                        int(str(engagement_data['createdAt'])[:-3])),
                                    'display_name': author.name if author.name else None,
                                    'email_from': meta_data['from'],
                                    # comment.author.email if comment.author.email else None,
                                    'author_id': author.id if author else None,
                                    'model': 'res.partner',
                                    'res_id': odoo_contact.id
                                })
                                self.env.cr.commit()
                                self.env['log.handling'].create({
                                    'record_id': engagement_data['id'],
                                    'odoo_record_name': odoo_contact.name,
                                    'description': 'Email: New Created',
                                    'skip': False,
                                    'model': 'Contact-res.partner',
                                })
                                self.env.cr.commit()
                            except Exception as e:
                                self.env['log.handling'].create({
                                    'record_id': engagement_data['id'],
                                    'odoo_record_name': odoo_contact.name,
                                    'description': 'EMAIL: Skipped because of error while creating(' + str(e) + ')',
                                    'skip': True,
                                    'model': 'Contact-res.partner',
                                })
                                self.env.cr.commit()
                                continue
                        # elif engagement_data['type'] == 'NOTE':
                        #     try:
                        #         print(odoo_contact.name)
                        #         author_id = self.env['res.users'].search([('hubspot_id', '=', engagement_data['ownerId'])]).partner_id
                        #         odoo_comment = self.env['mail.message'].create({
                        #             'engagement_id': engagement_data['id'],
                        #             'message_type': 'notification',
                        #             'body': engagement_data['bodyPreview'] if engagement_data.get('bodyPreview') else None,
                        #             'create_date': datetime.datetime.fromtimestamp(
                        #                 int(str(engagement_data['createdAt'])[:-3])),
                        #             'display_name': author_id.name if author_id.name else None,
                        #             'author_id': author_id.id,
                        #             'model': 'res.partner',
                        #             'res_id': odoo_contact.id
                        #         })
                        #         self.env.cr.commit()
                        #         self.env['log.handling'].create({
                        #             'record_id': engagement_data['id'],
                        #             'odoo_record_name': odoo_contact.name,
                        #             'description': 'Note: New Created',
                        #             'skip': False,
                        #             'model': 'Contact-res.partner',
                        #         })
                        #         self.env.cr.commit()
                        #     except Exception as e:
                        #         self.env['log.handling'].create({
                        #             'record_id': engagement_data['id'],
                        #             'odoo_record_name': odoo_contact.name,
                        #             'description': 'NOTE: Skipped because of error while creating(' + str(e) + ')',
                        #             'skip': True,
                        #             'model': 'Contact-res.partner',
                        #         })
                        #         self.env.cr.commit()
                        #         continue
                        # elif engagement_data['type'] == 'TASK':
                        #     try:
                        #         if meta_data['status'] != 'COMPLETED':
                        #             print(odoo_contact.name)
                        #             user_id = self.env['res.users'].search([('hubspot_id', '=', engagement_data['ownerId'])])
                        #             activity_type = self.env['mail.activity.type'].search([('name', '=', 'Todo')])
                        #             partner_model = self.env['ir.model'].search([('model', '=', 'res.partner')])
                        #             self.env['mail.activity'].create({
                        #                 'engagement_id': engagement_data['id'],
                        #                 'res_id': odoo_contact.id,
                        #                 'activity_type_id': activity_type.id,
                        #                 'summary': meta_data['subject'],
                        #                 'hubspot_status': meta_data['status'],
                        #                 'note': meta_data['body'] if meta_data.get('body') else None,
                        #                 'forObjectType': meta_data['forObjectType'],
                        #                 'res_model_id': partner_model.id,
                        #                 'date_deadline': datetime.datetime.fromtimestamp(
                        #                     int(str(meta_data['completionDate'])[:-3])) if meta_data.get(
                        #                     'completionDate') else datetime.datetime.now(),
                        #                 'user_id': user_id.id if user_id else self.env.user.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_contact.name,
                        #                 'description': 'Task: New Created',
                        #                 'skip': False,
                        #                 'model': 'Contact-res.partner',
                        #             })
                        #             self.env.cr.commit()
                        #         else:
                        #             print('message created for task', odoo_contact.name)
                        #             author_id = self.env['res.users'].search([('hubspot_id', '=', engagement_data['ownerId'])]).partner_id
                        #             odoo_comment = self.env['mail.message'].create({
                        #                 'engagement_id': engagement_data['id'],
                        #                 'message_type': 'comment',
                        #                 # 'from': odoo_contact.email,
                        #                 'body': meta_data['body'] if meta_data.get('body') else meta_data['subject'],
                        #                 'create_date': datetime.datetime.fromtimestamp(
                        #                     int(str(engagement_data['createdAt'])[:-3])),
                        #                 'display_name': author_id.name if author_id.name else None,
                        #                 'author_id': author_id.id,
                        #                 'model': 'res.partner',
                        #                 'res_id': odoo_contact.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_contact.name,
                        #                 'description': 'Task: New Created(Completed)',
                        #                 'skip': False,
                        #                 'model': 'Contact-res.partner',
                        #             })
                        #             self.env.cr.commit()
                        #     except Exception as e:
                        #         self.env['log.handling'].create({
                        #             'record_id': engagement_data['id'],
                        #             'odoo_record_name': odoo_contact.name,
                        #             'description': 'TASK: Skipped because of error while creating(' + str(e) + ')',
                        #             'skip': True,
                        #             'model': 'Contact-res.partner',
                        #         })
                        #         self.env.cr.commit()
                        #         continue
                        # elif engagement_data['type'] == 'CALL':
                        #     try:
                        #         if meta_data['status'] != 'COMPLETED':
                        #             print(odoo_contact.name)
                        #             user_id = self.env['res.users'].search(
                        #                 [('hubspot_id', '=', engagement_data['ownerId'])])
                        #             activity_type = self.env['mail.activity.type'].search([('name', '=', 'Call')])
                        #             partner_model = self.env['ir.model'].search([('model', '=', 'res.partner')])
                        #             self.env['mail.activity'].create({
                        #                 'engagement_id': engagement_data['id'],
                        #                 'res_id': odoo_contact.id,
                        #                 'activity_type_id': activity_type.id,
                        #                 'summary': meta_data['subject'] if meta_data.get('subject') else meta_data[
                        #                     'body'] if meta_data.get('body') else None,
                        #                 'hubspot_status': meta_data['status'],
                        #                 'note': html2text.html2text(meta_data['body']) if meta_data.get('body') else None,
                        #                 'toNumber': meta_data['toNumber'] if meta_data.get('toNumber') else None,
                        #                 'fromNumber': meta_data['fromNumber'] if meta_data.get('fromNumber') else None,
                        #                 'durationMilliseconds': str(meta_data['durationMilliseconds']) if meta_data.get(
                        #                     'durationMilliseconds') else None,
                        #                 'recordingUrl': meta_data['recordingUrl'] if meta_data.get(
                        #                     'recordingUrl') else None,
                        #                 'disposition': meta_data['disposition'] if meta_data.get('disposition') else None,
                        #                 'res_model_id': partner_model.id,
                        #                 'date_deadline': datetime.datetime.fromtimestamp(
                        #                     int(str(meta_data['completionDate'])[:-3])) if meta_data.get(
                        #                     'completionDate') else datetime.datetime.now(),
                        #                 'user_id': user_id.id if user_id else self.env.user.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_contact.name,
                        #                 'description': 'Call: New Created',
                        #                 'skip': False,
                        #                 'model': 'Contact-res.partner',
                        #             })
                        #             self.env.cr.commit()
                        #         else:
                        #             print('message created for call', odoo_contact.name)
                        #             author_id = self.env['res.users'].search([('hubspot_id', '=', engagement_data['ownerId'])]).partner_id
                        #             odoo_comment = self.env['mail.message'].create({
                        #                 'message_type': 'comment',
                        #                 'engagement_id': engagement_data['id'],
                        #                 'body': html2text.html2text(meta_data['body']) if meta_data.get('body') else
                        #                 meta_data['subject'],
                        #                 'create_date': datetime.datetime.fromtimestamp(
                        #                     int(str(engagement_data['createdAt'])[:-3])),
                        #                 'display_name': author_id.name if author_id.name else None,
                        #                 'author_id': author_id.id,
                        #                 'model': 'res.partner',
                        #                 'res_id': odoo_contact.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_contact.name,
                        #                 'description': 'Call: New Created(Completed)',
                        #                 'skip': False,
                        #                 'model': 'Contact-res.partner',
                        #             })
                        #             self.env.cr.commit()
                        #     except Exception as e:
                        #         self.env['log.handling'].create({
                        #             'record_id': engagement_data['id'],
                        #             'odoo_record_name': odoo_contact.name,
                        #             'description': 'CALL: Skipped because of error while creating(' + str(e) + ')',
                        #             'skip': True,
                        #             'model': 'Contact-res.partner',
                        #         })
                        #         self.env.cr.commit()
                        #         continue
                        # elif engagement_data['type'] == 'MEETING':
                        #     try:
                        #         end_time = datetime.datetime.fromtimestamp(int(str(meta_data['endTime'])[:-3]))
                        #         if end_time > datetime.datetime.now():
                        #             print(odoo_contact.name)
                        #             user_id = self.env['res.users'].search(
                        #                 [('hubspot_id', '=', engagement_data['ownerId'])])
                        #             activity_type = self.env['mail.activity.type'].search([('name', '=', 'Meeting')])
                        #             partner_model = self.env['ir.model'].search([('model', '=', 'res.partner')])
                        #             self.env['mail.activity'].create({
                        #                 'engagement_id': engagement_data['id'],
                        #                 'res_id': odoo_contact.id,
                        #                 'activity_type_id': activity_type.id,
                        #                 'summary': meta_data['title'] if meta_data.get('title') else meta_data[
                        #                     'body'] if meta_data.get('body') else None,
                        #                 'note': meta_data['body'] if meta_data.get('body') else None,
                        #                 'startTime': datetime.datetime.fromtimestamp(
                        #                     int(str(meta_data['startTime'])[:-3])) if meta_data.get(
                        #                     'startTime') else datetime.datetime.now(),
                        #                 'endTime': datetime.datetime.fromtimestamp(
                        #                     int(str(meta_data['endTime'])[:-3])) if meta_data.get(
                        #                     'endTime') else datetime.datetime.now(),
                        #                 'res_model_id': partner_model.id,
                        #                 'date_deadline': datetime.datetime.fromtimestamp(
                        #                     int(str(meta_data['endTime'])[:-3])) if meta_data.get(
                        #                     'endTime') else datetime.datetime.now(),
                        #                 'user_id': user_id.id if user_id else self.env.user.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_contact.name,
                        #                 'description': 'Meeting: New Created',
                        #                 'skip': False,
                        #                 'model': 'Contact-res.partner',
                        #             })
                        #             self.env.cr.commit()
                        #         else:
                        #             print('message created for call', odoo_contact.name)
                        #             author_id = self.env['res.users'].search([('hubspot_id', '=', engagement_data['ownerId'])]).partner_id
                        #             odoo_comment = self.env['mail.message'].create({
                        #                 'engagement_id': engagement_data['id'],
                        #                 'message_type': 'comment',
                        #                 'body': meta_data['body'] if meta_data.get('body') else meta_data['title'],
                        #                 'create_date': datetime.datetime.fromtimestamp(
                        #                     int(str(engagement_data['createdAt'])[:-3])),
                        #                 'display_name': author_id.name if author_id.name else None,
                        #                 'author_id': author_id.id,
                        #                 'model': 'res.partner',
                        #                 'res_id': odoo_contact.id
                        #             })
                        #             self.env.cr.commit()
                        #             self.env['log.handling'].create({
                        #                 'record_id': engagement_data['id'],
                        #                 'odoo_record_name': odoo_contact.name,
                        #                 'description': 'Meeting: New Created(Completed)',
                        #                 'skip': False,
                        #                 'model': 'Contact-res.partner',
                        #             })
                        #             self.env.cr.commit()
                        #     except Exception as e:
                        #         self.env['log.handling'].create({
                        #             'record_id': engagement_data['id'],
                        #             'odoo_record_name': odoo_contact.name,
                        #             'description': 'MEETING: Skipped because of error while creating(' + str(e) + ')',
                        #             'skip': True,
                        #             'model': 'Contact-res.partner',
                        #         })
                        #         self.env.cr.commit()
                        #         continue
                    has_more = res_data['hasMore']
                    parameter_dict['offset'] = res_data['offset']

                odoo_contact.write({
                    'engagement_done': False,
                })
                self.env.cr.commit()
        except:
            pass

    def create_owners(self):
        icpsudo = self.env['ir.config_parameter'].sudo()
        hubspot_keys = icpsudo.get_param('odoo_hubspot.hubspot_key')
        if not hubspot_keys:
            raise ValidationError('Please! Enter Hubspot key...')
        else:
            try:
                get_all_owners_url = "https://api.hubapi.com/owners/v2/owners?"
                parameter_dict = {'hapikey': hubspot_keys}
                headers = {
                    'Accept': 'application/json',
                    'connection': 'keep-Alive'
                }
                parameters = urllib.parse.urlencode(parameter_dict)
                get_url = get_all_owners_url + parameters
                r = requests.get(url=get_url, headers=headers)
                owners = json.loads(r.text)
                for owner in owners:
                    odoo_user = self.env['res.users'].search([('email', '=', owner['email'])])
                    if not odoo_user:
                        first_name = owner['firstName'] if owner['firstName'] else ''
                        last_name = owner['lastName'] if owner['lastName'] else ''
                        name = first_name + ' ' + last_name
                        self.env['res.users'].create({
                            'name': name,
                            'login': owner['email'] if owner['email'] else None,
                            'email': owner['email'] if owner['email'] else None,
                        })
                    else:
                        odoo_user.write({
                            'hubspot_id': owner['ownerId']
                        })
                    self.env.cr.commit()
            except Exception as e:
                _logger.error(e)
                raise ValidationError(_(str(e)))

    def get_lead_attachments(self):
        try:
            icpsudo = self.env['ir.config_parameter'].sudo()
            hubspot_keys = icpsudo.get_param('odoo_hubspot.hubspot_key')
            leads = self.env['crm.lead'].search(
                [('hubspot_id', '!=', False)]
            )
            for odoo_lead in leads:
                url = 'https://api.hubapi.com/engagements/v1/engagements/associated/DEAL/{0}/paged?hapikey={1}'.format(
                    odoo_lead.hubspot_id, hubspot_keys)
                response = requests.get(url)
                res_data = json.loads(response.content.decode("utf-8"))
                engagements = res_data['results']
                for engagement in engagements:
                    attachments = engagement['attachments']
                    if len(attachments):
                        for attachment in attachments:
                            try:
                                odoo_attachment = self.env['ir.attachment'].search(
                                    [('hubspot_id', '=', str(attachment['id']))]
                                )

                                attachment_url = 'https://api.hubapi.com/filemanager/api/v2/files/{0}/?hapikey={1}'.format(
                                    attachment['id'], hubspot_keys
                                )
                                response = requests.get(attachment_url)
                                res_data = json.loads(response.content.decode("utf-8"))
                                file_name = 'default'
                                if res_data.get('name'):
                                    file_name = res_data['name']
                                file_url = res_data.get('url', None)
                                if not os.path.isdir('engagement_files'):
                                    os.mkdir('engagement_files')
                                if file_url:
                                    try:
                                        file_res = urllib.request.urlretrieve(file_url,
                                                                              'engagement_files/' + file_name + '.' +
                                                                              res_data['extension'])
                                    except Exception as e:
                                        if e.code == 404:
                                            with open('lead.txt', 'a+') as file:
                                                file.write('\n')
                                                file.write('{} -> {} \n{}'.format(
                                                    odoo_lead.name, file_name, file_url)
                                                )
                                    if odoo_attachment:
                                        continue
                                    f = open('engagement_files/' + file_name + '.' + res_data['extension'], "rb")
                                    data = data = base64.b64encode(f.read())
                                    self.env['ir.attachment'].create({'name': file_name + '.' + res_data['extension'],
                                                                      'datas': data,
                                                                      'res_model': 'crm.lead',
                                                                      'res_id': odoo_lead.id, })
                                    f.close()
                                    os.remove('engagement_files/' + file_name + '.' + res_data['extension'])
                                    self.env.cr.commit()
                                    print(odoo_lead.name)
                            except Exception as e:
                                pass
        except Exception as e:
            pass

    def get_contact_attachments(self):
        try:
            icpsudo = self.env['ir.config_parameter'].sudo()
            hubspot_keys = icpsudo.get_param('odoo_hubspot.hubspot_key')
            contacts = self.env['res.partner'].search(
                [('hubspot_id', '!=', False), ('company_type', '=', 'person')]
            )
            for odoo_contact in contacts:
                url = 'https://api.hubapi.com/engagements/v1/engagements/associated/CONTACT/{0}/paged?hapikey={1}'.format(
                    odoo_contact.hubspot_id, hubspot_keys)
                response = requests.get(url)
                res_data = json.loads(response.content.decode("utf-8"))
                engagements = res_data['results']
                for engagement in engagements:
                    attachments = engagement['attachments']
                    if len(attachments):
                        for attachment in attachments:
                            try:
                                odoo_attachment = self.env['ir.attachment'].search(
                                    [('hubspot_id', '=', str(attachment['id']))]
                                )
                                attachment_url = 'https://api.hubapi.com/filemanager/api/v2/files/{0}/?hapikey={1}'.format(
                                    attachment['id'], hubspot_keys
                                )
                                response = requests.get(attachment_url)
                                res_data = json.loads(response.content.decode("utf-8"))
                                file_name = 'default'
                                if res_data.get('name'):
                                    file_name = res_data['name']
                                file_url = None
                                file_url = res_data.get('url', None)
                                if not os.path.isdir('engagement_files'):
                                    os.mkdir('engagement_files')
                                if file_url:
                                    try:
                                        urllib.request.urlretrieve(file_url, 'engagement_files/' + file_name + '.' + res_data['extension'])
                                    except Exception as e:
                                        if e.code == 404:
                                            with open('contact.txt', 'a+') as file:
                                                file.write('\n')
                                                file.write('{} -> {} \n{}'.format(
                                                    odoo_contact.name, file_name, file_url)
                                                )
                                    if odoo_attachment:
                                        continue
                                    a = 1
                                    f = open('engagement_files/' + file_name + '.' + res_data['extension'], "rb")
                                    data = data = base64.b64encode(f.read())
                                    self.env['ir.attachment'].create({'name': file_name + '.' + res_data['extension'],
                                                                      'datas': data,
                                                                      'res_model': 'res.partner',
                                                                      'res_id': odoo_contact.id, })
                                    f.close()
                                    os.remove('engagement_files/' + file_name + '.' + res_data['extension'])
                                    self.env.cr.commit()
                                    print(odoo_contact.name)
                                if odoo_attachment:
                                    continue
                            except Exception as e:
                                 pass
        except Exception as e:
            pass

    def get_company_attachments(self):
        try:
            icpsudo = self.env['ir.config_parameter'].sudo()
            hubspot_keys = icpsudo.get_param('odoo_hubspot.hubspot_key')
            companies = self.env['res.partner'].search(
                [('hubspot_id', '!=', False), ('company_type', '=', 'company')]
            )
            for odoo_company in companies:
                url = 'https://api.hubapi.com/engagements/v1/engagements/associated/COMPANY/{0}/paged?hapikey={1}'.format(
                    odoo_company.hubspot_id, hubspot_keys)
                # url = 'https://api.hubapi.com/engagements/v1/engagements/paged?hapikey={}'.format(API_KEY)
                response = requests.get(url)
                res_data = json.loads(response.content.decode("utf-8"))
                engagements = res_data['results']
                for engagement in engagements:
                    attachments = engagement['attachments']
                    if len(attachments):
                        for attachment in attachments:
                            try:
                                odoo_attachment = self.env['ir.attachment'].search(
                                    [('hubspot_id', '=', str(attachment['id']))]
                                )
                                attachment_url = 'https://api.hubapi.com/filemanager/api/v2/files/{0}/?hapikey={1}'.format(
                                    attachment['id'], hubspot_keys
                                )
                                response = requests.get(attachment_url)
                                res_data = json.loads(response.content.decode("utf-8"))
                                file_name = 'default'
                                if res_data.get('name'):
                                    file_name = res_data['name']
                                file_url = res_data.get('url', None)
                                if not os.path.isdir('engagement_files'):
                                    os.mkdir('engagement_files')
                                if file_url:
                                    try:
                                        urllib.request.urlretrieve(file_url,
                                                                   'engagement_files/' + file_name + '.' + res_data['extension'])
                                    except Exception as e:
                                        if e.code == 404:
                                            with open('company.txt', 'a+') as file:
                                                file.write('\n')
                                                file.write('{} -> {} \n{}'.format(
                                                    odoo_company.name, file_name, file_url)
                                                )
                                    if odoo_attachment:
                                        continue
                                    a = 1
                                    f = open('engagement_files/' + file_name + '.' + res_data['extension'], "rb")
                                    data = base64.b64encode(f.read())
                                    self.env['ir.attachment'].create({'name': file_name + '.' + res_data['extension'],
                                                                      'datas': data,
                                                                      'res_model': 'res.partner',
                                                                      'res_id': odoo_company.id, })
                                    f.close()
                                    os.remove('engagement_files/' + file_name + '.' + res_data['extension'])
                                    self.env.cr.commit()
                                    print(odoo_company.name)
                                if odoo_attachment:
                                    continue
                            except Exception as e:
                                pass
        except Exception as e:
            pass

    def get_ticket_attachments(self):
        try:
            icpsudo = self.env['ir.config_parameter'].sudo()
            hubspot_keys = icpsudo.get_param('odoo_hubspot.hubspot_key')
            tickets = self.env['helpdesk.ticket'].search([('hubspot_id', '!=', False)])
            for odoo_ticket in tickets:
                url = 'https://api.hubapi.com/engagements/v1/engagements/associated/TICKET/{0}/paged?hapikey={1}'.format(
                    odoo_ticket.hubspot_id, hubspot_keys)
                # url = 'https://api.hubapi.com/engagements/v1/engagements/paged?hapikey={}'.format(API_KEY)
                response = requests.get(url)
                res_data = json.loads(response.content.decode("utf-8"))
                engagements = res_data['results']
                for engagement in engagements:
                    attachments = engagement['attachments']
                    if len(attachments):
                        for attachment in attachments:
                            try:
                                odoo_attachment = self.env['ir.attachment'].search(
                                    [('hubspot_id', '=', str(attachment['id']))]
                                )
                                # if odoo_attachment:
                                #     continue
                                attachment_url = 'https://api.hubapi.com/filemanager/api/v2/files/{0}/?hapikey={1}'.format(
                                    attachment['id'], hubspot_keys
                                )
                                response = requests.get(attachment_url)
                                res_data = json.loads(response.content.decode("utf-8"))
                                file_name = 'default'
                                if res_data.get('name'):
                                    file_name = res_data['name']
                                file_url = res_data.get('url', None)
                                if not os.path.isdir('engagement_files'):
                                    os.mkdir('engagement_files')
                                if file_url:
                                    try:
                                        file_res = urllib.request.urlretrieve(file_url,
                                                               'engagement_files/' + file_name + '.' + res_data['extension'])
                                    except Exception as e:
                                        if e.code == 404:
                                            with open('ticket.txt', 'a+') as file:
                                                file.write('\n')
                                                file.write('{} -> {} \n{}'.format(
                                                    odoo_ticket.name, file_name, file_url)
                                                )
                                    if odoo_attachment:
                                        continue

                                    a = 1
                                    f = open('engagement_files/' + file_name + '.' + res_data['extension'], "rb")
                                    data = data = base64.b64encode(f.read())
                                    self.env['ir.attachment'].create({'name': file_name + '.' + res_data['extension'],
                                                                      'datas': data,
                                                                      'res_model': 'helpdesk.ticket',
                                                                      'res_id': odoo_ticket.id, })
                                    f.close()
                                    os.remove('engagement_files/' + file_name + '.' + res_data['extension'])
                                    self.env.cr.commit()
                                    print(odoo_ticket.name)
                                if odoo_attachment:
                                    continue
                            except Exception as e:
                                pass
        except Exception as e:
            pass
