# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta, date
from ast import literal_eval


class PartnerTransit(models.Model):
    _inherit = 'res.partner'

    def open_partner_history_shipping(self):
        '''
        This function returns an action that display ristourne made for the given partners.
        '''
        action = self.env.ref('inov_transit.action_shipping_folder').read()[0]
        action['domain'] = literal_eval(action['domain'])
        action['domain'].append(('customer_id', 'child_of', self.id))
        return action