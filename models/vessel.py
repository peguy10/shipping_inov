# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class NavireTransit(models.Model):
    _inherit = 'vessel.transit'

    number_of_hold = fields.Integer(string='Nombre de Compartiment', default=5, required=True)
    type_carry = fields.Selection([('bulk', 'Bulk Carrier'), ('oil', 'Oil Tank')], string="Type of Carrier")
    flag_id = fields.Many2one(
        'res.country',
        string='Ship Flag',
    )
    weight_grt = fields.Float(string="GRT", required=True)
    weight_drt = fields.Float(string="NRT(mt)", required=True)
    vessel_loa = fields.Float(string="LOA(m)", required=True)
    vessel_beam = fields.Float(string="Beam(m)", required=True)
    vessel_draft = fields.Float(string="Vessel Summer Draft", required=True)
    hold_ids = fields.One2many('stock.location', 'vessel_id', string="Compartiment")
    bol_hold = fields.Boolean(default='False', )

    def create_hold_location(self):
        location_obj = self.env['stock.location']
        locations = []
        locations.append(
            location_obj.create({
                'name': _('%s/Hold/%s' % (self.name[:3].upper(), 1)),
                'active': True,
                'usage': 'internal',
                'vessel_id': self.id
            }).id
        )

        return locations


    def create(self, values):
        result = super(NavireTransit, self).create(values)
        holdlocations = result.create_hold_location()
        values['hold_ids'] = [(6, 0, holdlocations)]
        values['bol_hold'] = True
        return result

    def update_vessels(self):
        self.ensure_one()
        for rec in self:
            holds = rec.create_hold_location()
            rec.update({
                'hold_ids': [(6, 0, holds)],
                'bol_hold': True
            })
