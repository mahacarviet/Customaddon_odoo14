from odoo import fields, models, api, _
import requests
import json
from odoo.exceptions import UserError, ValidationError


#       Class Inherit Product Category
class ApiSendoProductCategoryInherit(models.Model):
    _inherit = "product.category"

    tiki_cate_id = fields.Integer(string='Category ID')
    tiki_status = fields.Char('Status')
    tiki_is_primary = fields.Boolean('Primary')
    tiki_has_called = fields.Boolean('Call from Tiki', default=False)
    tiki_parent_id = fields.Char('Tiki Parent ID')

    #       Add To Module Sale
    def get_categories_tiki(self):
        current_seller = self.env['tiki.seller'].sudo().search([])[0]
        url = "https://api-sellercenter.tiki.vn/integration/categories"
        payload = {
        }
        headers = {
            'tiki-api': current_seller.secret,
            'User-Agent': current_seller.user_agent,
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        categories = response.json()
        val = {}
        if categories:
            for cate in categories:
                try:
                    if ('id' and 'name' and 'status' and 'is_primary') in cate:
                        val['tiki_cate_id'] = cate['id']
                        val['name'] = cate['name']
                        val['tiki_status'] = cate['status']
                        val['tiki_is_primary'] = cate['is_primary']
                        val['tiki_has_called'] = False
                        val['tiki_parent_id'] = 2
                except Exception as e:
                    print(e)
                existed_category = self.env['product.category'].search([('tiki_cate_id', '=', cate['id'])], limit=1)
                if len(existed_category) < 1:
                    self.env['product.category'].create(val)
                else:
                    existed_category.write(val)
        else:
            raise ValidationError(_('Sync Category From Tiki Is Fail.'))

    def get_child_categories_tiki(self):
        current_seller = self.env['tiki.seller'].sudo().search([])[0]
        has_not_called_api = self.env['product.category'].sudo().search(
            [('tiki_has_called', '=', False), ('tiki_is_primary', '=', False)])
        for a in has_not_called_api:
            url = 'https://api-sellercenter.tiki.vn/integration/categories' + '?parent_id=' + str(a['tiki_cate_id'])
            payload = {
            }
            headers = {
                'tiki-api': current_seller.secret,
                'User-Agent': current_seller.user_agent,
            }
            response_raw = requests.request("GET", url, headers=headers, data=payload)
            response = response_raw.json()
            val = {}
            if response:
                for res in response:
                    try:
                        if ('id' and 'name' and 'status' and 'is_primary') in res:
                            val['tiki_cate_id'] = res['id']
                            val['name'] = res['name']
                            val['tiki_status'] = res['status']
                            val['tiki_is_primary'] = res['is_primary']
                            val['tiki_has_called'] = False
                            val['tiki_parent_id'] = a.tiki_cate_id
                            val['parent_id'] = a.id
                            self.env['product.category'].create(val)
                    except Exception as e:
                        print(e)
            a.tiki_has_called = True
