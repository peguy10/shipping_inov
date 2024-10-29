# -*- coding: utf-8 -*-
# from odoo import http


# class FsmsShipping(http.Controller):
#     @http.route('/fsms_shipping/fsms_shipping', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsms_shipping/fsms_shipping/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsms_shipping.listing', {
#             'root': '/fsms_shipping/fsms_shipping',
#             'objects': http.request.env['fsms_shipping.fsms_shipping'].search([]),
#         })

#     @http.route('/fsms_shipping/fsms_shipping/objects/<model("fsms_shipping.fsms_shipping"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsms_shipping.object', {
#             'object': obj
#         })

