# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today BrowseInfo (<http://www.browseinfo.in>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.report import report_sxw
from datetime import datetime
from openerp.modules.module import get_module_resource

import operator
import itertools

from dateutil import relativedelta
from cStringIO import StringIO
import base64
from openerp import netsvc
from openerp import tools


class ewReporteEntregas(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(ewReporteEntregas, self).__init__(cr, uid, name, context=context)
        self.resultado_consulta = []
        self.localcontext.update({

            'getDeliveryData': self.getDeliveryData,
            'totalYesterdayStock': self.totalYesterdayStock,
            'totalTodayInStock': self.totalTodayInStock,
            'totalTodayOutStock': self.totalTodayOutStock,
            'totalTodayStock': self.totalTodayStock,
            'getStateSpanish': self.getStateSpanish,
            })       
           
    def getDeliveryData(self,filtros):
        lst = []
        start_date = filtros['form']['start_date']
        end_date = filtros['form']['end_date']
        
        if filtros:
            stock_move_pool = self.pool.get('stock.move')
            today_stock_search_out = stock_move_pool.search(self.cr, self.uid, [('create_date','>=', start_date),
                                                                             ('create_date','<=', end_date),
                                                                             ('picking_type_id.code','=','outgoing'),
                                                                             ('state','not in',['draft','cancel'])])
            for entregas in today_stock_search_out:
                entrega = stock_move_pool.browse(self.cr, self.uid, entregas)
                dic = {}
                dic = {
                       'product': entrega.name,
                       'partner': entrega.partner_id.name,
                       'date': entrega.date,
                       'product_qty': entrega.product_qty,
                       'state': entrega.state,
                       'price_unit': entrega.price_unit
                       }
                lst.append(dic)
                
        print "----RESULTADO DE ENTREGAS PARA PDF:",lst
                    
        return lst    
        
                  
    def getInventoryData(self,filtros):
       
        print '-----Datos Formulario Recibidos:',filtros

        start_date = filtros['form']['start_date']
        end_date = filtros['form']['end_date']
        print '-----Fechas:',start_date,"-----",end_date
        self.yesterday_stock = 0.00
        self.today_in_stock = 0.00
        self.today_out_stock = 0.00
        self.today_stock = 0.00
        print "-----Filtros:",filtros
        if filtros:
            #self_browse = self.browse(cr, uid, filtros[0])
            product_obj = self.pool.get('product.product')
            stock_move_pool = self.pool.get('stock.move')
            result = []
            product_ids = self.pool.get('product.product').search(self.cr, self.uid, [('qty_available','>',0)])
            
            
            if product_ids:
                for product in product_obj.browse(self.cr, self.uid, product_ids):
                    
                    #Logic For get yesterday stock (Yesterday Stock (all history before  Initial date)
                    yesterday_stock_search = stock_move_pool.search(self.cr, self.uid, [('product_id','=',product.id),
                                                                              ('create_date','<=', start_date),
                                                                              ('picking_type_id.code','in',['incoming', 'outgoing']),
                                                                              ('state','not in',['draft','cancel'])])
                    yesterday_stock = 0.00
                    if yesterday_stock_search:
                        stock_plus = 0.00
                        stock_minus = 0.00
                        for yesterday_stock in yesterday_stock_search:
                            yesterday_stock_browse = stock_move_pool.browse(self.cr, self.uid, yesterday_stock)
                            if yesterday_stock_browse.picking_type_id.code == 'incoming':
                                stock_plus += yesterday_stock_browse.product_uom_qty
                            if yesterday_stock_browse.picking_type_id.code == 'outgoing':
                                stock_minus += yesterday_stock_browse.product_uom_qty
                            yesterday_stock = stock_plus - stock_minus
                    
                    #Logic For get today in stock (Yesterday Stock (In's (between Initial Date)
                    today_stock_search_in = stock_move_pool.search(self.cr, self.uid, [('product_id','=',product.id),
                                                                             ('create_date','>=', start_date),
                                                                             ('create_date','<=', end_date),
                                                                             ('picking_type_id.code','=','incoming'),
                                                                             ('state','not in',['draft','cancel'])])
                    
                    
                    today_in_stock = 0.00
                    if today_stock_search_in:
                        for today_stock_in in today_stock_search_in:
                            today_stock_in_browse = stock_move_pool.browse(self.cr, self.uid, today_stock_in)
                            today_in_stock += today_stock_in_browse.product_uom_qty
                        self.today_in_stock = today_in_stock
                    
                    
                    
                    #Logic For get today out stock (Yesterday Stock (Out's (between Final Date))
                    
                    today_stock_search_out = stock_move_pool.search(self.cr, self.uid, [('product_id','=',product.id),
                                                                             ('create_date','>=', start_date),
                                                                             ('create_date','<=', end_date),
                                                                             ('picking_type_id.code','=','outgoing'),
                                                                             ('state','not in',['draft','cancel'])])
                    
                    today_out_stock = 0.00
                    if today_stock_search_out:
                        for today_stock_out in today_stock_search_out:
                            today_stock_out_browse = stock_move_pool.browse(self.cr, self.uid, today_stock_out)
                            today_out_stock += today_stock_out_browse.product_uom_qty
                        self.today_out_stock = today_out_stock
                        
                    # creando matriz de resultado   
                    dic = {
                           'name': product.name,
                           'yesterday_stock': yesterday_stock,
                           'today_in_stock': today_in_stock,
                           'today_out_stock': today_out_stock,
                           'today_stock': product.qty_available,
                           }
                    self.yesterday_stock += yesterday_stock
                
                    self.today_stock += product.qty_available
                    
                    result.append(dic)
                    
                    self.resultado = result
                    
        print "----Resultado de busqueda de INVENTARIOS PARA PDF:",result
                    
        return result
    
    def totalYesterdayStock (self):
        return self.yesterday_stock
    def totalTodayInStock (self):
        return self.today_in_stock
    def totalTodayOutStock (self):
        return self.today_out_stock
    def totalTodayStock (self):
        return self.today_stock
    
    def getStateSpanish(self, state):
        print "estado ingles ", state
        estado = state
        if estado == 'draft':
            estado = 'Borrador'
        if estado == 'sent':
            estado = 'Enviado'
        if estado == 'cancel':
            estado = 'Cancelado'
        if estado == 'waiting_date':
            estado = 'Esperando fecha'
        if estado == 'progress':
            estado = 'Pedido de Venta'
        if estado == 'manual':
            estado = 'Venta a Facturar'
        if estado == 'shipping_expect':
            estado = 'Excepcion de envio'
        if estado == 'invoice_except':
            estado = 'Excepcion de factura'
        if estado == 'done':
            estado = 'Realizado'
        if estado == 'confirmed':
            estado = 'Esperando Disponibilidad'
            
        print "estado español ", state
        return estado

class ew_entregas(osv.AbstractModel):
    _name = 'report.ew_quilocons.ew_entregas'
    _inherit = 'report.abstract_report'
    _template = 'ew_quilocons.ew_entregas'# llama al pdf que tienen que imprimir
    _wrapped_report_class = ewReporteEntregas
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
