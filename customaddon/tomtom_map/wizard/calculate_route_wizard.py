# -*- coding: utf-8 -*-

import requests
import json
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class CalculateRouteWizard(models.TransientModel):
    _name = 'calculate.route.wizard'
    _description = 'Calculate Route Tomtom'

    tomtom_starting_point = fields.Char(string='Starting Point')
    tomtom_destination = fields.Char(string='Destination')
    tomtom_distance = fields.Char(string='Distance (m)')
    tomtom_instructions_type = fields.Text(string='Instructions Type')
    tomtom_section_type = fields.Selection([
        ('carTrain', 'Car Train'),
        ('ferry', 'Ferry'),
        ('tunnel', 'Tunnel'),
        ('motorway', 'Motorway'),
        ('pedestrian', 'Pedestrian'),
        ('tollRoad', 'Toll Road'),
        ('tollVignette', 'Toll Vignette'),
        ('country', 'Country'),
        ('travelMode', 'Travel Mode'),
        ('traffic', 'Traffic')], default='travelMode', string='Section Type',
        # help='Specifies which section types are explicitly reported in the route response')
        help='Chỉ định xem loại phương tiện nào được báo cáo rõ ràng trong phản hồi của tuyến đường')
    tomtom_avoid = fields.Selection([
        ('ferries', 'Ferries'),
        ('motorway', 'Motorway'),
        ('tollRoad', 'Toll Road'),
        ('unpavedRoads', 'Unpaved Roads'),
        ('carpools', 'Carpools'),
        ('alreadyUsedRoads', 'Already Used Roads')], default='unpavedRoads', string='Avoid',
        # help='Specifies whether the routing engine should try to avoid specific types of road segment when calculating the route.')
        help='Chỉ định xem công cụ định tuyến có nên cố gắng tránh các loại đoạn đường cụ thể khi tính toán tuyến đường hay không.')
    tomtom_route_type = fields.Selection([
        ('fastest', 'Fastest'),
        ('shortest', 'Shortest'),
        ('eco', 'Eco'),
        ('thrilling', 'Thrilling')], default='fastest', string='Route Type',
        # help='The type of route requested.')
        help='Loại tuyến đường được yêu cầu.')
    tomtom_travel_mode = fields.Selection([
        ('car', 'Car'),
        ('truck', 'Truck'),
        ('taxi', 'Taxi'),
        ('bus', 'Bus'),
        ('van', 'Van'),
        ('motorcycle', 'Motorcycle'),
        ('bicycle', 'Bicycle'),
        ('pedestrian', 'Pedestrian')], default='car', string='Travel Mode',
        # help='The mode of travel for the requested route.')
        help='Phương thức di chuyển cho tuyến đường yêu cầu.')
    tomtom_vehicle_commercial = fields.Boolean(default=False, string='Vehicle Commercial',
                                               # help='Indicates that the vehicle is used for commercial purposes. This means it may not be allowed on certain roads.')
                                               help='Cho biết chiếc xe được sử dụng cho mục đích thương mại hay không. Điều này có nghĩa là nó có thể không được phép trên một số con đường nhất định.')

    calculate_route_res_partner_id = fields.Many2one('res.partner', string='Quotation ID')

    def call_api_tomtom_search_address(self, result):
        try:
            url = "https://api.tomtom.com/search/2/search/" + result + ".json?key=QZJyGL0bUtJGXwdfEeGpRnpCsL7jS7Zk"

            payload = {}
            headers = {}

            response = requests.request("GET", url, headers=headers, data=payload)
            result_search = response.json()

            if result_search['summary']['numResults'] == 0:
                raise ValidationError(_('Can not search Starting Point or Destination'))
            else:
                lat = str(result_search['results'][0]['position']['lat'])
                lon = str(result_search['results'][0]['position']['lon'])
                return lat, lon

        except Exception as e:
            print(e)

    def call_api_tomtom_calculate_route(self):
        try:
            tomtom_key = "QZJyGL0bUtJGXwdfEeGpRnpCsL7jS7Zk"
            a, b = self.call_api_tomtom_search_address(self.tomtom_starting_point)
            c, d = self.call_api_tomtom_search_address(self.tomtom_destination)
            variant_url_0 = "https://api.tomtom.com/routing/1/calculateRoute/"
            latitude_longitude = str(a + "%2C" + b + "%3A" + c + "%2C" + d)
            variant_url_1 = "/json?instructionsType=text&computeBestOrder=true&report=effectiveSettings&routeType=" + self.tomtom_route_type
            variant_url_2 = "&traffic=true&avoid=" + self.tomtom_avoid + "&travelMode=" + self.tomtom_travel_mode + "&key=" + tomtom_key
            if self.tomtom_vehicle_commercial:
                variant_url_3 = "&vehicleCommercial=true"
            else:
                variant_url_3 = "&vehicleCommercial=false"
            url = variant_url_0 + latitude_longitude + variant_url_1 + variant_url_2 + variant_url_3

            payload = {}
            headers = {
                'Cache-Control': 'no-cache, no-transform',
                'Content-Type': 'application/json',
                'Accept-Charset': 'utf-8'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            result_calculate_route = response.json()

            self.tomtom_instructions_type = ""
            if "detailedError" in result_calculate_route:
                raise ValidationError(_(result_calculate_route['detailedError']['message']))
            else:
                self.tomtom_distance = result_calculate_route['routes'][0]['summary']['lengthInMeters']
                if result_calculate_route['routes'][0]['guidance']:
                    guide_route_variant = result_calculate_route['routes'][0]['guidance']
                    if "instructions" in guide_route_variant:
                        for guide_road in guide_route_variant['instructions']:
                            if int(guide_road['routeOffsetInMeters']) > 0:
                                self.tomtom_instructions_type = self.tomtom_instructions_type + "Go " + str(guide_road['routeOffsetInMeters']) + " m " + str(guide_road['message']) + ", "
                            else:
                                self.tomtom_instructions_type = self.tomtom_instructions_type + str(guide_road['message']) + ", "
                val = {
                    'tomtom_starting_point': self.tomtom_starting_point,
                    'tomtom_destination': self.tomtom_destination,
                    'tomtom_distance': self.tomtom_distance,
                    'tomtom_instructions_type': self.tomtom_instructions_type,
                    'tomtom_avoid': self.tomtom_avoid,
                    'tomtom_route_type': self.tomtom_route_type,
                    'tomtom_travel_mode': self.tomtom_travel_mode,
                    'tomtom_vehicle_commercial': self.tomtom_vehicle_commercial,
                }
                if self.calculate_route_res_partner_id:
                    exist_record = self.calculate_route_res_partner_id.calculate_route_ids.filtered(lambda e: e.tomtom_destination == self.tomtom_destination and e.tomtom_travel_mode == self.tomtom_travel_mode and e.tomtom_route_type == self.tomtom_route_type)
                    if not exist_record:
                        self.calculate_route_res_partner_id.calculate_route_ids = [(0, 0, val)]
                    else:
                        if exist_record[0].tomtom_distance != self.tomtom_distance:
                            exist_record[0].tomtom_distance = self.tomtom_distance
                        if exist_record[0].tomtom_route_type != self.tomtom_route_type:
                            exist_record[0].tomtom_route_type = self.tomtom_route_type

        except Exception as e:
            raise ValidationError(str(e))
