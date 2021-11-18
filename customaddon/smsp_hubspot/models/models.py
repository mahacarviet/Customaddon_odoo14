# -*- coding: utf-8 -*-

from odoo import models, fields, api

import json
import pika

RABBIT_MQ = 'localhost'
# RABBIT_MQ = '128.199.193.129'


class ContactConstraints(models.Model):
    _inherit = 'res.partner'

    # @api.model_create_multi
    # def create(self, vals_list):
    #     print('val list: ', vals_list)
    #     res = super(ContactConstraints, self).create(vals_list)
    #     # partner_search_mode = self.env.context.get('res_partner_search_mode')
    #     # print('context: ', self.env.context)
    #     # print('WWW: ', partner_search_mode)
    #     # print('res', res.id)
    #     name = vals_list[0].get('name')
    #     email = vals_list[0].get('email')
    #     data = {'name': name, 'email': email}

    #     # Send to message broker.
    #     connection = pika.BlockingConnection(
    #         pika.ConnectionParameters(host=RABBIT_MQ))
    #     channel = connection.channel()
    #     channel.queue_declare(queue='contact_odoo_queue', durable=True)
    #     message = json.dumps(data)
    #     channel.basic_publish(
    #         exchange='',
    #         routing_key='contact_odoo_queue',
    #         body=message,
    #         properties=pika.BasicProperties(
    #             delivery_mode=2,  # make message persistent
    #         ))
    #     connection.close()
    #     return res

    def write(self, values):
        res = super().write(values)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBIT_MQ))
        channel = connection.channel()
        channel.queue_declare(queue='contact_update_odoo_queue', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='contact_update_odoo_queue',
            body=str(self.id),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
        connection.close()
        return res


class LeadConstrains(models.Model):
    _inherit = 'crm.lead'

    def _handle_won_lost(self, vals):
        # res = super(LeadConstrains, self)._handle_won_lost(vals)
        stage_id = self.env['crm.stage'].browse(vals['stage_id'])
        if stage_id.is_won is True:
            data = str(self.id) + ':' + 'won'
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBIT_MQ))
            channel = connection.channel()
            channel.queue_declare(
                queue='deal_create_odoo_queue', durable=True)
            channel.basic_publish(
                exchange='',
                routing_key='deal_create_odoo_queue',
                body=str(data),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ))
            connection.close()
        # return res

    def action_set_lost(self, **additional_values):
        # res = super()._handle_won_lost(additional_values)
        # print('YAHHH LOSTTT ....')
        data = str(self.id) + ':' + 'lost'
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBIT_MQ))
        channel = connection.channel()
        channel.queue_declare(
            queue='deal_create_odoo_queue', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='deal_create_odoo_queue',
            body=str(data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
        connection.close()
        # return res

    def action_set_won(self):
        # res = super().action_set_won()
        # print('YAHHH WON ....')
        data = str(self.id) + ':' + 'won'
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBIT_MQ))
        channel = connection.channel()
        channel.queue_declare(
            queue='deal_create_odoo_queue', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='deal_create_odoo_queue',
            body=str(data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
        connection.close()
        # return res
