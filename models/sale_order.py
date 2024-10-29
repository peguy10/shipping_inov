# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta, date
from ast import literal_eval


class SaleShipTemplate(models.Model):
    _inherit='sale.order.template'

    is_proforma  = fields.Boolean("Est une Proforma")

class SaleTransit(models.Model):
    _inherit='sale.order'

    folder_id = fields.Many2one(
        'folder.transit',
        string='Dossier',
        )
    vessel_id = fields.Many2one("vessel.transit",related="folder_id.vessel", strong="Navire", )
    weight_grt = fields.Float(related="folder_id.weight_grt", strong="GRT", store=True)
    vessel_loa = fields.Float(related="folder_id.vessel_loa", strong="LOA" , store=True)
    vessel_beam = fields.Float(related="folder_id.vessel_beam", strong="Beam(m)", store=True)
    vessel_draft = fields.Float(related="folder_id.vessel_draft", strong="SSWD", store=True)
    volume = fields.Float(related="folder_id.volum_vessel", strong="Volume", store=True)
    days = fields.Float("Nombre de Jours",)
    vessel_qty= fields.Float(related="folder_id.total_weighty", strong="Quantity", store=True)
    shipping_use = fields.Boolean(default=False)


    def _compute_line_data_for_vessel_change(self,line):
        if line.product_id.id == self.env.ref("inov_shipping.product_product_pilotage").id:
            return self.volume
        elif line.product_id.id == self.env.ref("inov_shipping.product_product_quay").id:
            return  self.volume*self.days
        elif line.product_id.id == self.env.ref("inov_shipping.product_product_ops").id:
            return  self.vessel_qty
        elif line.product_id.id == self.env.ref("inov_shipping.product_product_bonus").id:
            return  self.weight_grt
        elif line.product_id.id == self.env.ref("inov_shipping.product_product_pilotage_royaltie").id:
            return self.weight_grt
        elif line.product_id.id == self.env.ref("inov_shipping.product_product_royal").id:
            return self.weight_grt
        elif line.product_id.id == self.env.ref("inov_shipping.product_product_vessel").id:
            return self.days
        elif line.product_id.id == self.env.ref("inov_shipping.product_product_customs_watch").id:
            return self.days
        elif line.product_id.id == self.env.ref("inov_shipping.product_product_carservices").id:
            return self.days
        elif line.product_id.id == self.env.ref("inov_shipping.product_product_vhf").id:
            return self.days
        elif line.product_id.id == self.env.ref("inov_shipping.product_product_lumpsun").id:
            return self.vessel_qty
        else:
            return 1.0

    @api.onchange('sale_order_template_id')
    def onchange_sale_order_template_id(self):
        if not self.sale_order_template_id:
            self.require_signature = self._get_default_require_signature()
            self.require_payment = self._get_default_require_payment()
            return
        template = self.sale_order_template_id.with_context(lang=self.partner_id.lang)

        order_lines = [(5, 0, 0)]
        for line in template.sale_order_template_line_ids:
            data = self._compute_line_data_for_vessel_change(line)
            if line.product_id and not template.is_proforma:
                discount = 0
                if self.pricelist_id:
                    price = self.pricelist_id.with_context(uom=line.product_uom_id.id).get_product_price(line.product_id, 1, False)
                    if self.pricelist_id.discount_policy == 'without_discount' and line.price_unit:
                        discount = (line.price_unit - price) / line.price_unit * 100
                        # negative discounts (= surcharge) are included in the display price
                        if discount < 0:
                            discount = 0
                        else:
                            price = line.price_unit

                else:
                    price = line.price_unit

                data.update({
                    'price_unit': price,
                    'discount': 100 - ((100 - discount) * (100 - line.discount) / 100),
                    'product_uom_qty': line.product_uom_qty,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom_id.id,
                    'customer_lead': self._get_customer_lead(line.product_id.product_tmpl_id),
                })
                if self.pricelist_id:
                    data.update(self.env['sale.order.line']._get_purchase_price(self.pricelist_id, line.product_id, line.product_uom_id, fields.Date.context_today(self)))
            elif line.product_id and template.is_proforma:
                discount = 0
                if self.pricelist_id:
                    price = self.pricelist_id.with_context(uom=line.product_uom_id.id).get_product_price(line.product_id, 1, False)
                    if self.pricelist_id.discount_policy == 'without_discount' and line.price_unit:
                        discount = (line.price_unit - price) / line.price_unit * 100
                        # negative discounts (= surcharge) are included in the display price
                        if discount < 0:
                            discount = 0
                        else:
                            price = line.price_unit

                else:
                    price = line.price_unit

                data.update({
                    'price_unit': line.product_id.list_price,
                    'discount': 100 - ((100 - discount) * (100 - line.discount) / 100),
                    'product_uom_qty': self._compute_line_data_for_vessel_change(line),
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom_id.id,
                    'customer_lead': self._get_customer_lead(line.product_id.product_tmpl_id),
                })
                if self.pricelist_id:
                    data.update(self.env['sale.order.line']._get_purchase_price(self.pricelist_id, line.product_id, line.product_uom_id, fields.Date.context_today(self)))
            order_lines.append((0, 0, data))

        self.order_line = order_lines
        self.order_line._compute_tax_id()

        option_lines = []
        for option in template.sale_order_template_option_ids:
            data = self._compute_option_data_for_template_change(option)
            option_lines.append((0, 0, data))
        self.sale_order_option_ids = option_lines

        if template.number_of_days > 0:
            self.validity_date = fields.Date.to_string(datetime.now() + timedelta(template.number_of_days))

        self.require_signature = template.require_signature
        self.require_payment = template.require_payment

        if template.note:
            self.note = template.note

    def get_shipping_price(self):
        prod1=self.env.ref("inov_shipping.product_product_pilotage")
        prod2=self.env.ref("inov_shipping.product_product_tug")
        prod3=self.env.ref("inov_shipping.product_product_line")
        prod4=self.env.ref("inov_shipping.product_product_overt")
        prod5=self.env.ref("inov_shipping.product_product_code")
        prod6=self.env.ref("inov_shipping.product_product_quay")
        prod7=self.env.ref("inov_shipping.product_product_ops")
        prod8=self.env.ref("inov_shipping.product_product_bonus")
        prod9=self.env.ref("inov_shipping.product_product_pilotage_bonus")
        prod10=self.env.ref("inov_shipping.product_product_chanel")
        prod11=self.env.ref("inov_shipping.product_product_vessel")
        prod12=self.env.ref("inov_shipping.product_product_tax")
        prod13 = self.env.ref("inov_shipping.product_product_vat")
        prod14 = self.env.ref("inov_shipping.product_product_lumpsun")
        line1=self.order_line.filtered(lambda line:line.product_id.id==prod1.id)
        line2=self.order_line.filtered(lambda line:line.product_id.id==prod2.id)
        line3=self.order_line.filtered(lambda line:line.product_id.id==prod3.id)
        line4=self.order_line.filtered(lambda line:line.product_id.id==prod4.id)
        line5=self.order_line.filtered(lambda line:line.product_id.id==prod5.id)
        line6=self.order_line.filtered(lambda line:line.product_id.id==prod6.id)
        line7=self.order_line.filtered(lambda line:line.product_id.id==prod7.id)
        line8=self.order_line.filtered(lambda line:line.product_id.id==prod8.id)
        line9=self.order_line.filtered(lambda line:line.product_id.id==prod9.id)
        line10=self.order_line.filtered(lambda line:line.product_id.id==prod10.id)
        line11=self.order_line.filtered(lambda line:line.product_id.id==prod11.id)
        line12=self.order_line.filtered(lambda line:line.product_id.id==prod12.id)
        line13=self.order_line.filtered(lambda line:line.product_id.id==prod13.id)
        line14=self.order_line.filtered(lambda line:line.product_id.id==prod14.id)
        if line1 and line2 and line3 and line4:
            line4.update({
                'product_uom_qty': (line1.price_subtotal + line2.price_subtotal + line3.price_subtotal),
            })
        line5.update({
            'product_uom_qty':
            (line1.price_subtotal + line2.price_subtotal + line3.price_subtotal
             + line4.price_subtotal + line6.price_subtotal +
             line7.price_subtotal + line8.price_subtotal +
             line9.price_subtotal + line10.price_subtotal +
             line11.price_subtotal + line12.price_subtotal) * 0.08,
        })
        line13.update({
            'product_uom_qty': (line14.price_subtotal),
        })
        self.write({
            'shipping_use': True,
        })