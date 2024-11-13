# -*- coding: utf-8 -*-
from ast import literal_eval
from odoo import models, fields, api, _


class FretTransit(models.Model):
    _name = "fret.transit"

    name = fields.Char("Name")

class SaleOrderTemplate(models.Model):
    _inherit = 'sale.order.template'
    transit_id = fields.Many2one('folder.transit', string='Dossier')
class FolderTransit(models.Model):
    _inherit = 'folder.transit'

    number_of_hold = fields.Integer(related="vessel.number_of_hold", string='Nombre de Compartiment', store=True, )
    nce = fields.Char("C/E N")
    sign = fields.Char("CALL SIGN")
    type_carry = fields.Selection(related="vessel.type_carry", string="Type of Carrier")
    flag_id = fields.Many2one(
        related="vessel.flag_id",
        string='PAVILLON (FLAG)',
        store=True
    )
    weight_grt = fields.Float(related="vessel.weight_grt", strong="GRT", store=True)
    weight_drt = fields.Float(related="vessel.weight_drt", strong="NRT(mt)", store=True)
    vessel_loa = fields.Float(related="vessel.vessel_loa", strong="LOA", store=True)
    vessel_beam = fields.Float(related="vessel.vessel_beam", strong="Beam(m)", store=True)
    vessel_draft = fields.Float(related="vessel.vessel_draft", strong="Vessel Summer Draft", store=True)
    total_crew = fields.Integer(string="Equipage Vessel")
    captain_name = fields.Char(string="Nom du Capitaine")
    nbr_escale = fields.Integer(
        string="Nombre de Jour d'escale",
    )
    volum_vessel = fields.Float("Volume:cbm", compute='_get_data_vessel', store=True)

    # Ajout du champ Many2One pour le modèle de devis
    order_template_id = fields.Many2one(
        comodel_name='sale.order.template',
        string='Modèle de Devis'
    )

    # fret_id = fields.Many2one(string='Affreteur', comodel_name='res.partner', ondelete='restrict')
    bl_many_ids = fields.Many2many('folder.transit.bl', 'rel_transit_bl_order', string="BLs")
    sale_ids = fields.One2many(string='Proformas', comodel_name='sale.order', inverse_name='folder_id')
    sales_count = fields.Integer('Picking count', compute='compute_sales_ids', store=True, )

    # champs pour les port charges
    pilotage_entry = fields.Integer('PILOTAGE Entry, IN Offshore> 70.001TJB', compute='compute_pilotage_entry_amount', store=True, )
    pilot_bonus = fields.Integer('PILOT Bonus In  Offshore', compute='compute_pilot_bonus_amount', store=True, )
    pilot_night = fields.Integer('PILOTAGE Out Night Offshore > 70.001 TJB', compute='compute_pilot_night_amount', store=True, )
    pilot_bonus_night = fields.Integer('PILOT Bonus Out Night offshore', compute='compute_pilot_bonus_night_amount', store=True, )
    pilot_immo_in_night = fields.Integer('PILOT Immobilization--- IN/NIGHT', compute='compute_pilot_immo_in_night_amount', store=True, )
    bonus_pilot_immo_in_night = fields.Integer('Bonus PILOT Immobilization --- IN/ NIGHT', compute='compute_bonus_pilot_immo_in_night_amount', store=True, )
    pilot_immo_night_week = fields.Integer('PILOT Immobilization---Night, Weekend & holidays (IN)', compute='compute_pilot_immo_night_week_amount', store=True, )
    bonus_pilot_immo_night_week = fields.Integer('Bonus PILOT Immobilization---Night, Weekend & holidays (IN)', compute='compute_bonus_pilot_immo_night_week_amount', store=True, )
    security_watch = fields.Integer('Security Watch Bonus --- Night time ', compute='compute_security_watch_amount', store=True, )
    ship_stay = fields.Integer('Ship stay on waters', compute='compute_ship_stay_amount', store=True, )
    royalty_stay = fields.Integer('Royalty stay on operation per tonne of cargo loaded', compute='compute_royalty_stay_amount', store=True, )
    port_royalty = fields.Integer('Port Royalty /Redevance consignation classe 1 KK1', compute='compute_port_royalty_amount', store=True, )
    environmental_royalty = fields.Integer('Environmental Royalties /REDEVANCE ENVIR Petrolier', compute='compute_environmental_royalty_amount', store=True, )


    # champs pour les Outlays / Terminal costs / MOORING
    mooring = fields.Integer('Mooring  /per 36 Hrs Stay (lumpsum)', store=True)
    per_each = fields.Integer('Per each additional hour over 36 Hrs', store=True)
    traffic_due = fields.Integer('Traffic Dues', store=True)


    # champs pour les Outlays / Terminal costs / MOORING

    customs_boarding = fields.Integer('Customs boarding in & out', store=True)
    piloting_thro_trip = fields.Integer('Piloting thro & fro (  TRIP)', store=True)
    trans_ship_sanitation = fields.Integer('Transportation of Ship Sanitaion Control Officer (thro & fro )', store=True)
    piloting_thro_night = fields.Integer('Piloting thro & fro ( NIGHT 50%)', compute='compute_piloting_thro_night_amount', store=True)
    trans_piloting_thro_trip = fields.Integer('Transport of Piloting thro & fro ( TRIPS) Disembarkation', store=True)
    trans_immi_thro_trip = fields.Integer('Transport of Immigration thro & fro ( TRIPS) Disembarkation', store=True)
    customs_supervision = fields.Integer('Customs supervision per day (Offshore)', store=True)
    accomodation_trans_pilot = fields.Integer('Accomodation and Transportation to the Port - Pilot (Thro & fro)', store=True)
    port_health = fields.Integer('Port health Inspection (Free Pratique granted)', store=True)
    accomodation_trans_port_health = fields.Integer('Accomodation and Transportation to the Port - Port health officer  (Thro & fro)', store=True)
    immi_formality = fields.Integer('Immigration formality (Offshore)', store=True)

    # champs pour les services
    agency_fees = fields.Integer('Agency Fees (ALL IN) LUMPSUM ', store=True)

    @api.depends('vessel_loa', 'vessel_beam', 'vessel_draft')
    def _get_data_vessel(self):
        for vessel in self:
            vessel.volum_vessel = vessel.vessel_loa * vessel.vessel_beam * vessel.vessel_draft

    @api.depends('sale_ids')
    def compute_sales_ids(self):
        for lot in self:
            lot.sales_count = len(lot.sale_ids)


    @api.depends('total_weighty','pilotage_entry')
    def compute_pilotage_entry_amount(self):
        for pil in self:
            pil.pilotage_entry = pil.total_weighty * 0.063 * 655.957

    @api.depends('total_weighty','pilot_bonus')
    def compute_pilot_bonus_amount(self):
        for pil in self:
            pil.pilot_bonus = pil.total_weighty * 0.0047 * 655.957

    @api.depends('total_weighty','pilot_night')
    def compute_pilot_night_amount(self):
        for pil in self:
            pil.pilot_night = pil.total_weighty * 0.063 * 655.957


    @api.depends('total_weighty','pilot_bonus_night')
    def compute_pilot_bonus_night_amount(self):
        for pil in self:
            pil.pilot_bonus_night = pil.total_weighty * 0.0047 * 655.957

    @api.depends('total_weighty','pilot_immo_in_night')
    def compute_pilot_immo_in_night_amount(self):
        for pil in self:
            pil.pilot_immo_in_night = 87.6 * 1 * 655.957

    @api.depends('total_weighty','bonus_pilot_immo_in_night')
    def compute_bonus_pilot_immo_in_night_amount(self):
        for pil in self:
            pil.bonus_pilot_immo_in_night = 30 * 1 * 655.957

    @api.depends('total_weighty','pilot_immo_night_week')
    def compute_pilot_immo_night_week_amount(self):
        for pil in self:
            pil.pilot_immo_night_week = 87.6 * 1 * 655.957


    @api.depends('total_weighty','bonus_pilot_immo_night_week')
    def compute_bonus_pilot_immo_night_week_amount(self):
        for pil in self:
            pil.bonus_pilot_immo_night_week = 30 * 1 * 655.957




    @api.depends('total_weighty','security_watch')
    def compute_security_watch_amount(self):
        for pil in self:
            pil.security_watch = 51 * 655.957

    @api.depends('total_weighty','ship_stay')
    def compute_ship_stay_amount(self):
        for pil in self:
            pil.ship_stay = 0.015 * pil.total_weighty * 655.957

    @api.depends('total_weighty','royalty_stay')
    def compute_royalty_stay_amount(self):
        for pil in self:
            pil.royalty_stay = 0.014 * pil.total_weighty * 655.957

    @api.depends('total_weighty','port_royalty')
    def compute_port_royalty_amount(self):
        for pil in self:
            pil.port_royalty = 0.076 * pil.weight_grt * 655.957


    @api.depends('total_weighty','environmental_royalty')
    def compute_environmental_royalty_amount(self):
        for pil in self:
            pil.environmental_royalty = 182.94 * 655.957



    @api.depends('piloting_thro_trip','piloting_thro_night')
    def compute_piloting_thro_night_amount(self):
        for pil in self:
            pil.piloting_thro_night = pil.piloting_thro_trip / 2










    def act_folder_transit_2_sale_order(self):
        action = self.env.ref('inov_shipping.act_folder_transit_2_sale_order').read()[0]
        saleids = self.mapped('sale_ids')
        data = {
            'search_default_folder_id': self.id,
            'search_default_partner_id': self.customer_id.id,
        }

        action['context'] = data
        if len(saleids) > 1:
            action['domain'] = [('id', 'in', saleids.ids)]
        # else:
        #     action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        #     action['res_id'] = saleids.id
        return action


class FolderTransitBL(models.Model):
    _name = 'folder.transit.bl'
    _description = 'BL'

    name = fields.Char(string='Numero de BL')
    customer_id = fields.Many2one(
        'res.partner',
        string='Client',
        domain=[('customer', '=', True)],
        tracking=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='Produit',
        domain=[('type', '=', 'product')],
    )
    package = fields.Selection([('manos', 'T20'), ('plus', 'T40'), ('other', 'Colis')], string="Colisage")
    qty = fields.Float(string='Quantite')
    package_uom_id = fields.Many2one(
        'uom.uom',
        string='Unite de Mesure',
    )

    state_related = fields.Selection([('transit', 'Dedouanement'), ('accone', 'Acconage'), ('ship', 'Shipping')],
                                     string="Processus")
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('sent', 'Envoye'),
    ], string='Etat', default='draft')