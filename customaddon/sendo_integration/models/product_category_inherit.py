from odoo import fields, models, api, _
import requests
import json
from odoo.exceptions import UserError, ValidationError


#       Class Inherit Product Category
class ApiSendoProductCategoryInherit(models.Model):
    _inherit = "product.category"

    sendo_cate_id = fields.Integer(string='Category ID')
    sendo_level = fields.Integer(string='Level')
    sendo_parent_id = fields.Char(string='Sendo Parent ID')
    sendo_has_called = fields.Boolean(default=False)

    #       Add To Module Sale
    def get_categories_sendo_to_product_template(self):
        try:
            current_seller = self.env['sendo.seller'].sudo().search([])[0]

            url = "https://open.sendo.vn/api/partner/category/0"

            payload = {}
            headers = {
                'Authorization': 'Bearer ' + current_seller.token_connection
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if "exp" in response.json():
                raise ValidationError(_('My Token is expired, Please connect Sendo API.'))
            elif response.json()["success"]:
                result_category = response.json()
                categories = result_category["result"]
                val = {}
                if categories:
                    for cate in categories:
                        try:
                            if ('id' and 'name' and 'level') in cate:
                                val['sendo_cate_id'] = cate['id']
                                val['name'] = cate['name']
                                val['sendo_parent_id'] = cate['parent_id']
                                val['sendo_level'] = cate['level']
                                val['sendo_has_called'] = False
                                val['parent_id'] = None
                        except Exception as e:
                            print(e)
                        existed_category = self.env['product.category'].search([('sendo_cate_id', '=', cate['id'])],
                                                                               limit=1)
                        if len(existed_category) < 1:
                            self.env['product.category'].create(val)
                        else:
                            existed_category.write(val)
            else:
                raise ValidationError(_('Sync Category From Sendo Is Fail.'))

        except Exception as e:
            raise ValidationError(str(e))

    #       Add To Module Sale
    def get_child_categories_sendo_to_product_template(self):
        try:
            current_seller = self.env['sendo.seller'].sudo().search([])[0]
            has_not_called_api = self.env['product.category'].sudo().search(
                [('sendo_has_called', '=', False), ('sendo_level', '!=', 4)])
            for a in has_not_called_api:
                url = 'https://open.sendo.vn/api/partner/category/' + str(a['sendo_cate_id'])

                payload = {}
                headers = {
                    'Authorization': 'Bearer ' + current_seller.token_connection
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                if "exp" in response.json():
                    raise ValidationError(_('My Token is expired, Please connect Sendo API.'))
                elif response.json()["success"]:
                    result_child_cate = response.json()
                    response = result_child_cate["result"]
                    val = {}
                    if response:
                        for res in response:
                            try:
                                if ('id' and 'name' and 'level') in res:
                                    val['sendo_cate_id'] = res['id']
                                    val['name'] = res['name']
                                    val['sendo_level'] = res['level']
                                    val['sendo_parent_id'] = a.sendo_cate_id
                                    val['parent_id'] = a.id
                                    val['sendo_has_called'] = False
                                    self.env['product.category'].create(val)
                            except Exception as e:
                                print(e)
                    a.sendo_has_called = True
                else:
                    raise ValidationError(_('Sync Category From Sendo Is Fail.'))
        except Exception as e:
            raise ValidationError(str(e))
