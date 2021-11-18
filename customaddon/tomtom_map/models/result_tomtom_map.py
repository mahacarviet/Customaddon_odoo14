# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class CalculateRouteWizard(models.Model):
    _name = 'result.tomtom.map'
    _description = 'Result Tomtom Map'

    tomtom_starting_point = fields.Char(string='Starting Point')
    tomtom_destination = fields.Char(string='Destination')
    tomtom_distance = fields.Char(string='Distance  (m)')
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
        ('traffic', 'Traffic')], default='traffic', string='Section Type',
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

    result_tomtom_map_res_partner = fields.Many2one('res.partner', string='Result Calculate Route')