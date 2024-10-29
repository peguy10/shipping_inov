# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class LocationTransit(models.Model):
    _inherit = 'stock.location'

    vessel_id = fields.Many2one(
        'vessel.transit',
        string='Navire',
    )