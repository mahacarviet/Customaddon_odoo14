from ..controllers.auth import ShopifySession, XeroSession
import shopify
import json
import maya
import traceback
import logging
from datetime import datetime, timedelta, date
import calendar
_logger = logging.getLogger(__name__)

class AbstractModel:
    shopify_session = None
    xero_session = None
    xero_connector = None
    shopify_store = None
    filters = {}

    def __init__(self, *args, **kwargs):
        self.shopify_session = ShopifySession()
        self.xero_session = XeroSession()
        self.xero_connector = self.xero_session.get_xero_connector()
        self.shopify_store = self.shopify_session.get_shopify_store()
        super().__init__(*args, **kwargs)

    def add_filter(self, field, value=None):
        if type(field) == dict:
            for k,v in field.items():
                self.filters[k] = v
        else:
            self.filters[field] = value


class XeroContact(AbstractModel):

    def sync(self):
        xero_connector = self.xero_connector
        customers = shopify.Customer.find(limit=200, **self.filters)
        if customers:
            while True:
                vals_list = []
                for customer in customers:
                    vals = self.customer_vals(customer)
                    vals_list.append(vals)
                try:
                    xero_connector.contacts.save(vals_list)
                except Exception as e:
                    pass
                if customers.has_next_page():
                    customers = customers.next_page()
                else:
                    break
        return True

    def customer_vals(self,customer):
        vals = {
            "Name": '%s %s - Shopify (%s)' % (customer.first_name, customer.last_name, customer.id),
            "ContactNumber": customer.id,
            # "IsSupplier": False,
            # "IsCustomer": True,
            "FirstName": customer.first_name,
            "LastName": customer.last_name,
        }
        if customer.email:
            vals['EmailAddress'] = customer.email
        if customer.phone:
            vals['Phones'] = [
                {
                    "PhoneType": "DEFAULT",
                    "PhoneNumber": customer.phone,
                }
            ]
        if customer.default_address:
            vals['Addresses'] = []
            # address = customer.default_address
            address_data = customer.default_address
            vals['Addresses'].append({
                'AddressType': 'POBOX',
                'AddressLine1': address_data.address1,
                'City': address_data.city,
                'PostalCode': address_data.zip
            })
        return vals


class XeroProduct(AbstractModel):

    def sync(self):
        xero_connector = self.xero_connector
        products = shopify.Product.find(limit=200, **self.filters)
        if products:
            while True:
                vals_list = []
                for product in products:
                    for variant in product.variants:
                        if variant.fulfillment_service == 'gift_card':
                            shopify_store = self.shopify_store
                            if not shopify_store.plan.sync_giftcard:
                                continue
                        vals = self.product_vals(product.title, variant)
                        vals_list.append(vals)
                try:
                    xero_connector.items.save(vals_list)
                except Exception as e:
                    pass
                if products.has_next_page():
                    products = products.next_page()
                else:
                    break
        return True

    def product_vals(self, product_title, variant):
        varitant_title = variant.title
        if varitant_title == 'Default Title':
            varitant_title = ''
        vals = {
            "Code": variant.id,
            "Name": product_title + ' ' + varitant_title.upper(),
            "Description": product_title + ' ' + varitant_title.upper(),
            "SalesDetails": {
                "UnitPrice": int(variant.price),
            },
        }
        return vals


class XeroOrder(AbstractModel):
    filters = {
        'status': 'any'
    }

    def sync(self):
        xero_connector = self.xero_connector
        shopify_store = self.shopify_store
        if not shopify_store.orders_synced >= shopify_store.plan.order_number or shopify_store.plan.is_unlimited:
            orders = shopify.Order.find(limit=200, **self.filters)
            if orders:
                while True:
                    vals_list = []
                    list_payment_vals = []
                    list_refund_vals = []
                    list_allocate_refund_vals = []
                    for order in orders:
                        order_vals = self.order_vals(order)
                        vals_list.append(order_vals)
                        # create payment or refund vals
                        invoice_number = self.get_invoice_number(order)
                        if order.financial_status in ['paid', 'refunded', 'partially_refunded']:
                            transactions = shopify.Transaction.find(order_id=order.id)
                            if transactions:
                                payment_vals = self.get_payment_vals(invoice_number=invoice_number,
                                                                     transactions=transactions)
                                if payment_vals:
                                    list_payment_vals.append(payment_vals)
                        if shopify_store.plan.sync_refund:
                            if order.financial_status in ['refunded', 'partially_refunded']:  # 'partially_refunded'
                                refund_vals = self.get_refund_vals(order=order, invoice_number=invoice_number)
                                if refund_vals:
                                    list_refund_vals.append(refund_vals)
                                payment_refund_vals = self.get_payment_refund_vals(order=order)
                                if payment_refund_vals:
                                    list_allocate_refund_vals.append(payment_refund_vals)
                    if vals_list:
                        successful_records = 0
                        try:
                            result = xero_connector.invoices.save(vals_list)
                            successful_records = len(result)
                        except Exception as e:
                            _logger.error(_logger.error(traceback.format_exc()))
                            try:
                                if hasattr(e, 'response') and hasattr(e.response, 'text'):
                                    response = json.loads(e.response.text)
                                    if 'Elements' in response:
                                        failed_records = len(response['Elements'])
                                        requested_records = len(vals_list)
                                        successful_records = requested_records - failed_records
                            except Exception as e:
                                _logger.error(_logger.error(traceback.format_exc()))
                        if successful_records > 0:
                            shopify_store.env['order.request.log'].sudo().create({
                                'shopify_store': shopify_store.id,
                                'order_count': successful_records
                            })
                            self.update_order_synced_number()
                    # pass payment or refund AFTER create Invoice, need InvoiceNumber
                    if list_payment_vals:
                        try:
                            xero_connector.payments.save(list_payment_vals)
                        except Exception as e:
                            pass
                    if list_refund_vals:
                        try:
                            xero_connector.creditnotes.save(list_refund_vals)
                        except Exception as e:
                            pass
                    if list_allocate_refund_vals:
                        try:
                            xero_connector.payments.save(list_allocate_refund_vals)
                        except Exception as e:
                            pass

                    if orders.has_next_page():
                        orders = orders.next_page()
                    else:
                        break
            return True

    def order_vals(self, order):
        vals = {
            "Type": "ACCREC",
            'Date': maya.parse(order.created_at).datetime(),
            'DueDate': maya.parse(order.updated_at).datetime(),
            "InvoiceNumber": self.get_invoice_number(order),
            "Reference": order.name,
            "LineAmountTypes": "Inclusive" if order.taxes_included else "Exclusive",
            "SubTotal": order.subtotal_price,
            "TotalTax": order.total_tax,
            "Total": order.total_price,
            "Contact": self.add_contact_vals(order),
            # "LineItems": self.get_line_items(order),
            "Status": self.switch_status(order.financial_status)
        }
        line_items_vals = []
        # order line vals
        for line_item in order.line_items:
            line_vals = self.order_line_vals(line_item)
            if line_vals:
                line_items_vals.append(line_vals)
        # ALl discount: free ship, fixed, perentage
        if order.discount_applications:
            discount_items_vals = self.get_all_order_discount(order=order)
            if discount_items_vals:
                line_items_vals.append(discount_items_vals)
        # Add shipping fee
        if order.shipping_lines:
            shipping_item_vals = self.add_shiping_item(order=order)
            if shipping_item_vals:
                line_items_vals.append(shipping_item_vals)
        # Add Tip item
        if order.total_tip_received:
            total_tip = int(float(order.total_tip_received))
            if total_tip > 0:
                tip_vals = self.add_tip(total_tip)
                if tip_vals:
                    line_items_vals.append(tip_vals)
        vals["LineItems"] = line_items_vals
        return vals

    def add_contact_vals(self, order):
        contact_vals = {}
        if 'customer' in order.attributes:
            contact_vals = {
                "ContactNumber": order.customer.id,
            }
        else:
            contact_vals = {
                "ContactNumber": order.user_id,
                "Name": 'Shopify User: '+ str(order.user_id),
            }
        return contact_vals

    def order_line_vals(self, line_item):
        sale_account = self.shopify_store.sale_account
        discount_amount = 0
        if line_item.total_discount:
            discount_amount = int(line_item.total_discount)
        tax_line_amount = 0
        if line_item.tax_lines:
            for tax_line in line_item.tax_lines:
                tax_line_amount += int(tax_line.price)
        line_vals = {}
        if line_item.variant_id:
            line_vals = {
                "Description": line_item.name,
                "UnitAmount": int(line_item.price),
                "ItemCode": line_item.variant_id,
                "Quantity": line_item.quantity,
                "AccountCode": sale_account,
                "TaxAmount": tax_line_amount,
            }
        if discount_amount > 0:
            line_vals.update({
                "DiscountAmount": discount_amount,
            })
        # if tax_line_amount > 0:
        #     line_vals.update({
        #         "TaxAmount": tax_line_amount,
        #     })
        return line_vals

    def switch_status(self, status):
        switcher = {
            'pending': 'SUBMITTED',
            'authorized': 'AUTHORISED',
            'partially_paid': 'AUTHORISED',
            'paid': 'AUTHORISED',
            'partially_refunded': 'AUTHORISED',
            'refunded': 'AUTHORISED',
        }
        return switcher.get(status,"DELETED")

    def get_all_order_discount(self, order):
        # line_items_vals = []
        for discount_application in order.discount_applications:
            if order.discount_codes:
                for discount_code in order.discount_codes:
                    if discount_application.target_selection == 'all' or discount_application.target_selection == 'entitled':
                        if discount_code.type == 'shipping':
                            free_ship_item_vals = self.add_free_ship_item(order)
                            # line_items_vals.append(free_ship_item_vals)
                            return free_ship_item_vals
                        elif discount_code.type == 'fixed_amount':
                            fixed_amount_vals = self.add_discount_amount(order)
                            # line_items_vals.append(fixed_amount_vals)
                            return fixed_amount_vals
                        elif discount_code.type == 'percentage':
                            percentage_amount_vals = self.add_discount_percentage(order)
                            # line_items_vals.append(percentage_amount_vals)
                            return percentage_amount_vals
            else:
                if discount_application.type == 'automatic':
                    if discount_application.target_selection == 'all' or discount_application.target_selection == 'entitled':
                        if discount_application.allocation_method == 'across':  # differ with buy 1 get 1
                            if discount_application.value_type == 'fixed_amount':
                                auto_discount_fixed_vals = self.auto_discount_fixed(order)
                                # line_items_vals.append(auto_discount_fixed_vals)
                                return auto_discount_fixed_vals
                            elif discount_application.value_type == 'percentage':
                                auto_discount_percentage_vals = self.auto_discount_percentage(order)
                                # line_items_vals.append(auto_discount_percentage_vals)
                                return auto_discount_percentage_vals
        return line_items_vals

    def add_shiping_item(self, order):
        shipping_item_vals = {
            "Description": 'Shipping: ' + order.shipping_lines[0].title,
            "UnitAmount": order.shipping_lines[0].price,
            "Quantity": 1,
            "AccountCode": self.shopify_store.shipping_account,
        }
        tax_type = ''
        tax_amount = ''
        for shipping_line in order.shipping_lines:
            if not shipping_line.tax_lines:
                tax_type = 'NONE'
            else:
                for tax_line in shipping_line.tax_lines:
                    tax_amount += tax_line.price
        if tax_type:
            shipping_item_vals.update({
                "TaxType": tax_type,
            })
        else:
            if tax_amount:
                shipping_item_vals.update({
                    "TaxAmount": tax_amount,
                })
        return shipping_item_vals

    def add_free_ship_item(self, order):
        free_ship_item_vals = {
            "Description": "Free Ship",
            "UnitAmount": str(-int(order.discount_codes[0].amount)),
            "Quantity": 1,
            "TaxType": "NONE",
            "AccountCode": self.shopify_store.sale_account,
        }
        return free_ship_item_vals

    def add_discount_amount(self, order):
        fixed_amount_vals = {
            "Description": "Discount Code: Fixed Amount",
            "UnitAmount": str(-int(order.discount_codes[0].amount)),
            "Quantity": 1,
            "TaxType": "NONE",
            "AccountCode": self.shopify_store.sale_account,
        }
        return fixed_amount_vals

    def add_discount_percentage(self, order):
        percentage_amount_vals = {
            "Description": "Discount Code: Percentage",
            "UnitAmount": str(-int(order.discount_codes[0].amount)),
            "Quantity": 1,
            "TaxType": "NONE",
            "AccountCode": self.shopify_store.sale_account,
        }
        return percentage_amount_vals

    def auto_discount_fixed(self, order):
        auto_discount_vals = {
            "Description": "Auto Discount Amount",
            "UnitAmount": str(-int(order.total_discounts)),
            "Quantity": 1,
            "TaxType": "NONE",
            "AccountCode": self.shopify_store.sale_account,
        }
        return auto_discount_vals

    def auto_discount_percentage(self, order):
        auto_discount_vals = {
            "Description": "Auto Discount Pecentage",
            "UnitAmount": str(-int(order.total_discounts)),
            "Quantity": 1,
            "TaxType": "NONE",
            "AccountCode": self.shopify_store.sale_account,
        }
        return auto_discount_vals

    def add_tip(self, total_tip):
        tip_vals = {
            "Description": 'Tip',
            "UnitAmount": total_tip,
            "Quantity": 1,
            "AccountCode": self.shopify_store.sale_account,
            "TaxType": "NONE",
        }
        return tip_vals

    def update_order_synced_number(self):
        first_day, last_day = self.get_month_range()
        order_request_logs = self.shopify_store.env['order.request.log'].sudo().search([('shopify_store','=', self.shopify_store.id),
                                                                                ('sync_date', '>=' , first_day),
                                                                                ('sync_date', '<=' , last_day),])
        order_synced_number = 0
        if order_request_logs:
            for order_request_log in order_request_logs:
                order_synced_number += order_request_log.order_count
        if order_synced_number:
            self.shopify_store.orders_synced = order_synced_number

    def get_month_range(self):
        today = date.today()
        first_day = today.replace(day=1)
        last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        return first_day, last_day

    def get_invoice_number(self, order):
        return "Shopify: " + str(order.id)

    def get_payment_vals(self, invoice_number, transactions):
        transaction_amount = 0
        transaction_date = ''
        if transactions:
            for transaction in transactions:
                if transaction.kind in ['sale', 'capture'] and transaction.status == 'success':
                    transaction_amount += int(transaction.amount)
                    transaction_date = maya.parse(transaction.processed_at).datetime()
        payment_vals = {
            "Type": "ACCREC",
            "Invoice": {"InvoiceNumber": invoice_number, },
            "Account": {"Code": self.shopify_store.payment_account},
            "Date": transaction_date,
        }
        if transaction_amount:
            payment_vals["Amount"] = str(transaction_amount)
        if payment_vals:
            return payment_vals

    def get_refund_vals(self, order, invoice_number):
        payment_account = self.shopify_store.payment_account
        created_at = ''
        total_amount = 0
        message = ''
        line_items_vals = []
        if order.refunds:
            for refund in order.refunds:
                created_at = maya.parse(refund.created_at).datetime()
                for transaction in refund.transactions:
                    total_amount += int(transaction.amount)
                    message = transaction.message
        line_vals = {
            'Description': '%s: %s' % (invoice_number,message),
            'Quantity': 1.0000,
            'UnitAmount': total_amount,
            'AccountCode': payment_account,
            'TaxType': 'NONE',
            'TaxAmount': 0
        }
        line_items_vals.append(line_vals)
        refund_vals = {
            'Type': 'ACCPAYCREDIT',
            'Status': 'AUTHORISED',
            'CreditNoteNumber': 'SC-%s'%(order.number),
            'Contact': {'ContactNumber': order.customer.id if 'customer' in order.attributes else order.user_id},
            'Date': created_at,
            'LineAmountTypes': 'Exclusive',
            'LineItems': line_items_vals,
        }
        return refund_vals

    def get_payment_refund_vals(self, order):
        created_at = ''
        total_amount = 0
        if order.refunds:
            for refund in order.refunds:
                created_at = maya.parse(refund.created_at).datetime()
                for transaction in refund.transactions:
                    total_amount += int(transaction.amount)
        payment_refund_vals = {
            'Type': 'ARCREDITPAYMENT',
            'CreditNote': {
                'CreditNoteNumber': 'SC-%s'%(order.number),
            },
            'Account': {
                'Code': self.shopify_store.payment_account,
            },
            'Date': created_at,
            'Amount': total_amount,
            "CurrencyRate": 1,
        }
        return payment_refund_vals