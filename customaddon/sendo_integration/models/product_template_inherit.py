from odoo import fields, models, api, _
import requests
import json
from odoo.exceptions import UserError, ValidationError
from datetime import *


class ProductTemplateInheritSendo(models.Model):
    _inherit = "product.template"

    sendo_product_id = fields.Integer(stored=True)
    sendo_category_id = fields.Integer()
    sendo_stock_availability = fields.Boolean(string='Stock Availability', default=True, store=True)
    sendo_height = fields.Float(string='Height', required=True, default=5)
    sendo_length = fields.Float(string='Length', required=True, default=20)
    sendo_width = fields.Float(string='Width', required=True, default=10)
    sendo_unit_id = fields.Selection([
        ('1', 'Cái'),
        ('2', 'Bộ'),
        ('3', 'Chiếc'),
        ('4', 'Đôi'),
        ('5', 'Hộp'),
        ('6', 'Cuốn'),
        ('7', 'Chai'),
        ('8', 'Thùng')], string='Unit Product', required=True, default='1')
    sendo_stock_quantity = fields.Integer(string='Stock Quantity', required=True, default=50)
    sendo_promotion_from_date = fields.Date(string='Promotion From Date', default=date.today(), store=True)
    sendo_promotion_to_date = fields.Date(string='Promotion To Date', required=True,
                                          default=date.today() + timedelta(days=9000), store=True)
    sendo_is_promotion = fields.Boolean(string='Promotion', default=True, store=True)
    sendo_special_price = fields.Float(string='Special Price', required=True, default=0.5)
    sendo_url_avatar_image = fields.Char(string='Image URL Product')
    check_product_sendo = fields.Boolean(store=True)

    @api.constrains('sendo_special_price', 'list_price')
    def check_sendo_special_price(self):
        for rec in self:
            if rec.sendo_special_price > rec.list_price:
                raise ValidationError(_("Sales Price need more than Special Price."))

    @api.constrains('sendo_height')
    def check_sendo_height(self):
        for rec in self:
            if rec.sendo_height <= 0:
                raise ValidationError(_("Height Product need more than 0."))

    @api.constrains('sendo_length')
    def check_sendo_length(self):
        for rec in self:
            if rec.sendo_length <= 0:
                raise ValidationError(_("Length Product need more than 0."))

    @api.constrains('sendo_width')
    def check_sendo_width(self):
        for rec in self:
            if rec.sendo_width <= 0:
                raise ValidationError(_("Width Product need more than 0."))

    @api.constrains('sendo_stock_quantity')
    def check_sendo_stock_quantity(self):
        for rec in self:
            if rec.sendo_stock_quantity < 0:
                raise ValidationError(_("Stock Quantity Product need more than 0."))

    def create_product_sendo(self):
        try:
            current_seller = self.env['sendo.seller'].sudo().search([])[0]

            search_cate_sendo = self.env['product.category'].sudo().search(
                [('id', '=', self.categ_id.id)], limit=1)

            url = "https://open.sendo.vn/api/partner/product"

            payload = {
                "id": 0,
                "name": self.name,
                "sku": self.default_code,
                "price": float(self.list_price),
                "weight": float(self.weight * 1000),
                "stock_availability": self.sendo_stock_availability,
                "description": self.description or 'string',
                "cat_4_id": search_cate_sendo.sendo_cate_id,
                "tags": None,
                "relateds": [
                    # {
                    #     "id": 0,
                    #     "name": None,
                    #     "sku": None,
                    #     "category_name": None,
                    #     "price": 0,
                    #     "status": 0,
                    #     "image": None
                    # }
                ],
                "seo_keyword": None,
                "seo_title": None,
                "seo_description": None,
                "product_image": self.sendo_url_avatar_image,
                "brand_id": 0,
                "video_links": None,
                "height": self.sendo_height,
                "length": self.sendo_length,
                "width": self.sendo_width,
                "unit_id": int(self.sendo_unit_id),
                "stock_quantity": self.sendo_stock_quantity,
                "avatar": {
                    "picture_url": self.sendo_url_avatar_image
                },
                "pictures": [
                    {
                        "picture_url": self.sendo_url_avatar_image
                    }
                ],
                "certificate_file": [
                    # {
                    #     "id": 0,
                    #     "table_name": None,
                    #     "table_id": 0,
                    #     "file_name": None,
                    #     "attachment_url": None,
                    #     "display_order": 0
                    # }
                ],
                "attributes": [
                    # {
                    #     "attribute_id": 0,
                    #     "attribute_name": None,
                    #     "attribute_code": None,
                    #     "attribute_is_custom": False,
                    #     "attribute_is_checkout": False,
                    #     "attribute_values": [
                    #         {
                    #             "id": 0,
                    #             "value": None,
                    #             "attribute_img": None,
                    #             "is_selected": False,
                    #             "is_custom": False
                    #         }
                    #     ]
                    # }
                ],
                "promotion_from_date": self.sendo_promotion_from_date.strftime("%Y-%m-%d"),
                "promotion_to_date": self.sendo_promotion_to_date.strftime("%Y-%m-%d"),
                "is_promotion": self.sendo_is_promotion,
                "extended_shipping_package":
                    {
                        "is_using_instant": False,
                        "is_using_in_day": False,
                        "is_self_shipping": False,
                        "is_using_standard": True,
                        "is_using_eco": False
                    },
                "variants": [
                    # {
                    #     "variant_attributes": [
                    #         {
                    #             "attribute_id": 0,
                    #             "attribute_code": None,
                    #             "option_id": 0
                    #         }
                    #     ],
                    #     "variant_sku": None,
                    #     "variant_price": 0,
                    #     "variant_promotion_start_date": None,
                    #     "variant_promotion_end_date": None,
                    #     "variant_special_price": 0,
                    #     "variant_quantity": 0
                    # }
                ],
                "is_config_variant": False,
                "special_price": self.sendo_special_price,
                "voucher": {
                    "product_type": 1,
                    "start_date": None,
                    "end_date": None,
                    "is_check_date": False
                }
            }

            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + current_seller.token_connection
            }

            response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
            if "exp" in response.json():
                raise ValidationError(_('My Token is expired, Please connect Sendo API.'))
            elif response.json()["success"]:
                print(response.json())
                existed_seller_product_sendo = self.env['product.template'].search(
                    [('default_code', '=', self.default_code)], limit=1)
                existed_seller_product_sendo.check_product_sendo = True
                existed_seller_product_sendo.sendo_product_id = int(response.json()["result"])
            else:
                raise ValidationError(_(response.json()["error"]["message"]))
        except Exception as e:
            raise ValidationError(str(e))

    def update_product_sendo(self):
        try:
            current_seller = self.env['sendo.seller'].sudo().search([])[0]

            search_cate_sendo = self.env['product.category'].sudo().search(
                [('id', '=', self.categ_id.id)], limit=1)

            url = "https://open.sendo.vn/api/partner/product"

            payload = {
                "id": self.sendo_product_id,
                "name": self.name,
                "sku": self.default_code,
                "price": float(self.list_price),
                "weight": float(self.weight * 1000),
                "stock_availability": self.sendo_stock_availability,
                "description": self.description or 'string',
                "cat_4_id": search_cate_sendo.sendo_cate_id,
                "tags": None,
                "relateds": [
                    # {
                    #     "id": 0,
                    #     "name": None,
                    #     "sku": None,
                    #     "category_name": None,
                    #     "price": 0,
                    #     "status": 0,
                    #     "image": None
                    # }
                ],
                "seo_keyword": None,
                "seo_title": None,
                "seo_description": None,
                "product_image": self.sendo_url_avatar_image,
                "brand_id": 0,
                "video_links": None,
                "height": self.sendo_height,
                "length": self.sendo_length,
                "width": self.sendo_width,
                "unit_id": int(self.sendo_unit_id),
                "stock_quantity": self.sendo_stock_quantity,
                "avatar": {
                    "picture_url": self.sendo_url_avatar_image
                },
                "pictures": [
                    {
                        "picture_url": self.sendo_url_avatar_image
                    }
                ],
                "certificate_file": [
                    # {
                    #     "id": 0,
                    #     "table_name": None,
                    #     "table_id": 0,
                    #     "file_name": None,
                    #     "attachment_url": None,
                    #     "display_order": 0
                    # }
                ],
                "attributes": [
                    # {
                    #     "attribute_id": 0,
                    #     "attribute_name": None,
                    #     "attribute_code": None,
                    #     "attribute_is_custom": False,
                    #     "attribute_is_checkout": False,
                    #     "attribute_values": [
                    #         {
                    #             "id": 0,
                    #             "value": None,
                    #             "attribute_img": None,
                    #             "is_selected": False,
                    #             "is_custom": False
                    #         }
                    #     ]
                    # }
                ],
                "promotion_from_date": self.sendo_promotion_from_date.strftime("%Y-%m-%d"),
                "promotion_to_date": self.sendo_promotion_to_date.strftime("%Y-%m-%d"),
                "is_promotion": self.sendo_is_promotion,
                "extended_shipping_package":
                    {
                        "is_using_instant": False,
                        "is_using_in_day": False,
                        "is_self_shipping": False,
                        "is_using_standard": True,
                        "is_using_eco": False
                    },
                "variants": [
                    # {
                    #     "variant_attributes": [
                    #         {
                    #             "attribute_id": 0,
                    #             "attribute_code": None,
                    #             "option_id": 0
                    #         }
                    #     ],
                    #     "variant_sku": None,
                    #     "variant_price": 0,
                    #     "variant_promotion_start_date": None,
                    #     "variant_promotion_end_date": None,
                    #     "variant_special_price": 0,
                    #     "variant_quantity": 0
                    # }
                ],
                "is_config_variant": False,
                "special_price": self.sendo_special_price,
                "voucher": {
                    "product_type": 1,
                    "start_date": None,
                    "end_date": None,
                    "is_check_date": False
                }
            }

            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + current_seller.token_connection
            }

            response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

            if "exp" in response.json():
                raise ValidationError(_('My Token is expired, Please connect Sendo API.'))
            elif response.json()["success"]:
                print(response.json())
            else:
                raise ValidationError(_(response.json()["error"]["message"]))
        except Exception as e:
            raise ValidationError(str(e))

    def update_price_stock_product_sendo(self):

        current_seller = self.env['sendo.seller'].sudo().search([])[0]
        try:
            url = "https://open.sendo.vn/api/partner/product/config/variant-price"

            payload = json.dumps([
                {
                    "product_id": int(self.sendo_product_id),
                    "price": float(self.list_price),
                    "stock_quantity": int(self.qty_available),
                    "is_config_variant": False,
                    "stock_availability": True,
                    "special_price": None,
                    "promotion_start_date": None,
                    "promotion_end_date": None,
                    "variants": []
                }
            ])
            headers = {
                'content-type': 'application/json',
                'Authorization': 'Bearer ' + current_seller.token_connection
            }

            response = requests.request("PUT", url, headers=headers, data=payload)

            if "exp" in response.json():
                raise ValidationError(_('My Token is expired, Please connect Sendo API.'))
            elif response.json()["success"]:
                self.sendo_is_promotion = False
                self.sendo_stock_quantity = self.qty_available
            else:
                raise ValidationError(_(response.json()['error']['message']))
        except Exception as e:
            raise ValidationError(str(e))

    def update_promotion_product_sendo(self):

        current_seller = self.env['sendo.seller'].sudo().search([])[0]
        try:
            url = "https://open.sendo.vn/api/partner/product/config/variant-price"

            payload = json.dumps([
                {
                    "product_id": int(self.sendo_product_id),
                    "price": float(self.list_price),
                    "stock_quantity": int(self.qty_available),
                    "is_config_variant": False,
                    "stock_availability": True,
                    "special_price": self.sendo_special_price,
                    "promotion_start_date": self.sendo_promotion_from_date.strftime("%Y-%m-%d"),
                    "promotion_end_date": self.sendo_promotion_to_date.strftime("%Y-%m-%d"),
                    "variants": []
                }
            ])
            headers = {
                'content-type': 'application/json',
                'Authorization': 'Bearer ' + current_seller.token_connection
            }

            response = requests.request("PUT", url, headers=headers, data=payload)

            if "exp" in response.json():
                raise ValidationError(_('My Token is expired, Please connect Sendo API.'))
            elif response.json()["success"]:
                if "error_list" in response.json()["result"]:
                    if response.json()["result"]["error_list"]:
                        raise ValidationError(_(response.json()['result']['error_list'][0]['message']))
                    else:
                        self.sendo_stock_quantity = self.qty_available
                else:
                    pass
        except Exception as e:
            raise ValidationError(str(e))
