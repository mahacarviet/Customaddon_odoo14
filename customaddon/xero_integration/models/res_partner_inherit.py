import requests
import json
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from urllib.request import urlopen
import base64
import re


#   Class Inherit Res Partner
class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    xero_ContactID = fields.Char()
    xero_check_customer = fields.Boolean(default=False, string='Xero Customer')


#   Class Inherit Account Move
class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    xero_InvoiceID = fields.Char()
    xero_Type = fields.Char()
    xero_InvoiceNumber = fields.Char()
    xero_Reference = fields.Char()
    xero_check_invoice = fields.Boolean(default=False, string='Xero Order')

    def create_invoices_xero(self):
        try:

            url = "https://api.xero.com/api.xro/2.0/Invoices"

            payload = json.dumps({
                "Type": "ACCREC",
                "Reference": "Monthly support",
                "Payments": [],
                "CreditNotes": [],
                "Prepayments": [],
                "Overpayments": [],
                "AmountDue": 550.00,
                "AmountPaid": 0.00,
                "AmountCredited": 0.00,
                "CurrencyRate": 1.0000000000,
                "IsDiscounted": False,
                "HasAttachments": False,
                "HasErrors": False,
                "Contact": {
                    "ContactID": self.partner_id.xero_ContactID,
                    "Name": self.partner_id.name,
                    "Addresses": [],
                    "Phones": [],
                    "ContactGroups": [],
                    "ContactPersons": [],
                    "HasValidationErrors": False
                },
                "DateString": "2021-10-31T00:00:00",
                "Date": "/Date(1635638400000+0000)/",
                "DueDateString": "2021-11-15T00:00:00",
                "DueDate": "/Date(1636934400000+0000)/",
                "BrandingThemeID": "d613f7f9-8fcb-477f-97f0-31eb85b7e5cf",
                "Status": "SUBMITTED" if self.state == 'posted' else 'DRAFT',
                "LineAmountTypes": "Inclusive",
                "LineItems": [],
                "SubTotal": self.amount_untaxed,
                "TotalTax": self.amount_by_group,
                "Total": self.amount_total,
                "UpdatedDateUTC": "/Date(1466789028673+0000)/",
                "CurrencyCode": self.company_currency_id.name
            })
            headers = {
                'xero-tenant-id': 'f3288060-cd58-4370-96c0-704754e3fc8f',
                'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjFDQUY4RTY2NzcyRDZEQzAyOEQ2NzI2RkQwMjYxNTgxNTcwRUZDMTkiLCJ0eXAiOiJKV1QiLCJ4NXQiOiJISy1PWm5jdGJjQW8xbkp2MENZVmdWY09fQmsifQ.eyJuYmYiOjE2MzY0MjExNzksImV4cCI6MTYzNjQyMjk3OSwiaXNzIjoiaHR0cHM6Ly9pZGVudGl0eS54ZXJvLmNvbSIsImF1ZCI6Imh0dHBzOi8vaWRlbnRpdHkueGVyby5jb20vcmVzb3VyY2VzIiwiY2xpZW50X2lkIjoiODY3NkM5NzY1RjFCNDM0QzgzMEFDNDNDRUFCMUU5M0UiLCJzdWIiOiI2MjFiZjFhMTdiZWE1ODdiYWRlZTVlYzAzYmQzOGIzMiIsImF1dGhfdGltZSI6MTYzNjM2NTU4NiwieGVyb191c2VyaWQiOiJiZjMzYWQzNS1iNTc3LTQ5ZWItYWFmZi01NzVmYTY5ZGVmNDUiLCJnbG9iYWxfc2Vzc2lvbl9pZCI6ImViNGMwM2YyM2RiZDRlNjE5ZDU1YmNhNDNjNDU5MjY5IiwianRpIjoiMTBkZGExNjcyYzIyMmQ0MmQwZmVjMWNiZDBlYTNlMGQiLCJhdXRoZW50aWNhdGlvbl9ldmVudF9pZCI6ImJjNjJmZmRkLWQ3MDUtNGM1My05MTFmLTdiYzdkMDU5NWEwZCIsInNjb3BlIjpbImVtYWlsIiwicHJvZmlsZSIsIm9wZW5pZCIsImFjY291bnRpbmcuc2V0dGluZ3MiLCJhY2NvdW50aW5nLnRyYW5zYWN0aW9ucyIsImFjY291bnRpbmcuY29udGFjdHMiLCJvZmZsaW5lX2FjY2VzcyJdfQ.Zjxi9CVJgqvCT0HT_WkRWfl7HfZq4dSf9KBROIOOsDSGYLUbWhxEU4e64xBmBi-MBXcwNNmBq9u4h1qhO4aGmbFJaJYGF2zu5xpDxCWMTs2HONtSFdJUCQ0q3ScR4DW5MNONm9g15Ahn60PTFVrarteEp-OqsjHjeEgzyF7ptGqW6N2YJA_p7lpto53LG7EPa4F5HX9rujB_LvmP3ZDurZZaK0MVVXuH90vC2daeWXLFgvPlscGKWf2p1v3jmnMJtU7J1trnwN-tgIBXU7Bcnj12RBD6oNQ2WRn-5FM6ZZbi0bgOuGXMECMf7Uqlz3V22IPP1WdhlmTICn6aQbWKJg',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }

            response = requests.request("PUT", url, headers=headers, data=payload)
            result = response.json()

        except Exception as e:
            raise ValidationError(str(e))
