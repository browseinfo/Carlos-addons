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

# Cierre de Caja

class ew_pos_cierre_caja(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(ew_pos_cierre_caja, self).__init__(cr, uid, name, context=context)
        self.resultado_consulta = []
        self.suma_cierre_caja_global = []
        self.suma_cierre_caja_ATC = []
        self.suma_cierre_caja_chica = []
        self.granTotalResta = 0
        self.granTotalVentas = 0
        self.localcontext.update({
            
            'get_pos_data_datos_cierre_caja': self.get_pos_data_datos_cierre_caja,
            'fecha_impresion': self.__fecha_impresion__,
            'hora_impresion': self.__hora_impresion__,
            'get_pos_data_ventas_cierre_caja_detallado': self.get_pos_data_ventas_cierre_caja_detallado,
            'get_pos_data_ventas_cierre_caja_global': self.get_pos_data_ventas_cierre_caja_global,
            'get_pos_data_ventas_cierre_caja_pagos_atc': self.get_pos_data_ventas_cierre_caja_pagos_atc,
            'get_pos_data_ventas_cierre_caja_pagos_caja_chica': self.get_pos_data_ventas_cierre_caja_pagos_caja_chica,
            'get_pos_data_factura_maxima': self.get_pos_data_factura_maxima,
            'get_pos_data_factura_minima': self.get_pos_data_factura_minima,
            'total_cierre_caja_global': self.__total_cierre_caja_global__,
            'total_cierre_caja_atc_chica': self.__total_atc_chica__,
            'gran_total_cierre_caja': self.__total_cierre_caja__,
            'get_pos_data_facturas_anuladas': self.get_pos_data_facturas_anuladas,
            })
    
    def get_pos_data_datos_cierre_caja(self, data):
        
        if data['form']['session_id'] is False:
            sessionName = "%"
        else:
            sessionName = data['form']['session_id'][1]
        
        self.cr.execute("SELECT pc.name "\
                        ",cajero.name "\
                        ",ps.start_at "\
                        "FROM pos_order AS po "\
                        "INNER JOIN pos_session AS ps ON ps.id = po.session_id "\
                        "INNER JOIN pos_config AS pc ON pc.id = ps.config_id "\
                        "INNER JOIN res_users AS usuario ON usuario.id = ps.user_id "\
                        "INNER JOIN res_partner AS cajero ON cajero.id = usuario.partner_id "\
                        "WHERE ps.name = %s"\
                        "GROUP BY pc.name, cajero.name, ps.start_at", [sessionName])
        
        pos_datos_cierre = [x for x in self.cr.fetchall()]
        
        return pos_datos_cierre 
    
    def __fecha_impresion__(self):
        fecha = time.strftime("%x")
        print "----->>>FECHA ACTUAL:",fecha
        return fecha
    
    def __hora_impresion__(self):
        hora = time.strftime("%X")
        print "----->>>HORA ACTUAL:",hora
        return hora

    def get_pos_data_ventas_cierre_caja_global(self, data):
        pos_pool = self.pool.get('pos.order')

        lst = []
        
        if data['form']['session_id'] is False:
            sessionName = "%"
        else:
            sessionName = data['form']['session_id'][1]
        
        self.cr.execute("SELECT "\
                        "COUNT(po.id) AS cantidad_ventas "\
                        ",SUM (detalle_pedido.total_venta) AS total_pagos "\
                        "FROM pos_order AS po "\
                        "INNER JOIN pos_session AS ps ON ps.id = po.session_id "\
                        "JOIN ( "\
                        "SELECT "\
                        "ps.name AS sesion "\
                        ",po.id AS po_id "\
                        ",ps.id AS ps_id "\
                        ",SUM (pol.price_subtotal_incl) AS total_venta "\
                        "FROM pos_order_line AS pol "\
                        "INNER JOIN pos_order AS po ON po.id = pol.order_id "\
                        "INNER JOIN pos_session AS ps ON ps.id = po.session_id "\
                        "GROUP BY pol.order_id, po.id,ps.id "\
                        ") AS detalle_pedido ON detalle_pedido.po_id = po.id "\
                        "JOIN ( "\
                        "SELECT "\
                        "po.id AS po_id "\
                        ",aj.name AS tipo_pago "\
                        "FROM pos_order AS po "\
                        "INNER JOIN account_bank_statement_line AS acbastli ON acbastli.pos_statement_id = po.id "\
                        "INNER JOIN account_journal AS aj ON aj.id = acbastli.journal_id "\
                        "WHERE acbastli.amount > 0 "\
                        "GROUP BY acbastli.pos_statement_id, acbastli.journal_id, po.id, aj.name "\
                        ") AS detalle_pago ON detalle_pago.po_id = po.id "\
                        "WHERE po.order_status <> 'anulada' "\
                        "AND detalle_pago.tipo_pago <> 'ATC' "\
                        "AND ps.name = %s ", [sessionName])
        pos_search2 = [x for x in self.cr.fetchall()]
        
        return pos_search2

    def __total_cierre_caja_global__(self):
        granTotal = 0
        for line in self.suma_cierre_caja_global:
            granTotal += line[2]
        self.granTotalVentas = granTotal
        print ">>>>>>>GRAN TOTAL: ",granTotal
        return granTotal

    def get_pos_data_ventas_cierre_caja_detallado(self, data):
        pos_pool = self.pool.get('pos.order')

        lst = []
        
        if data['form']['session_id'] is False:
            sessionName = "%"
        else:
            sessionName = data['form']['session_id'][1]
        
        self.cr.execute("SELECT "\
                        "COUNT(po.id) AS cantidad_ventas "\
                        ",(CASE WHEN po.color ISNULL THEN 'VENTAS FAC. MAN.' ELSE 'VENTAS POR SIST.'END) AS tipo_venta "\
                        ",SUM (detalle_pedido.total_venta) AS total_pagos "\
                        "FROM pos_order AS po "\
                        "INNER JOIN pos_session AS ps ON ps.id = po.session_id "\
                        "JOIN ( "\
                        "SELECT "\
                        "ps.name AS sesion "\
                        ",po.id AS po_id "\
                        ",ps.id AS ps_id "\
                        ",SUM (pol.price_subtotal_incl) AS total_venta "\
                        "FROM pos_order_line AS pol "\
                        "INNER JOIN pos_order AS po ON po.id = pol.order_id "\
                        "INNER JOIN pos_session AS ps ON ps.id = po.session_id "\
                        "GROUP BY pol.order_id, po.id,ps.id "\
                        ") AS detalle_pedido ON detalle_pedido.po_id = po.id "\
                        "JOIN ( "\
                        "SELECT "\
                        "po.id AS po_id "\
                        ",aj.name AS tipo_pago "\
                        "FROM pos_order AS po "\
                        "INNER JOIN account_bank_statement_line AS acbastli ON acbastli.pos_statement_id = po.id "\
                        "INNER JOIN account_journal AS aj ON aj.id = acbastli.journal_id "\
                        "WHERE acbastli.amount > 0 "\
                        "GROUP BY acbastli.pos_statement_id, acbastli.journal_id, po.id, aj.name "\
                        ") AS detalle_pago ON detalle_pago.po_id = po.id "\
                        "WHERE po.order_status <> 'anulada' "\
                        "AND detalle_pago.tipo_pago <> 'ATC' "\
                        "AND ps.name = %s "\
                        "GROUP BY tipo_venta", [sessionName])
        pos_search = [x for x in self.cr.fetchall()]
        
        self.suma_cierre_caja_global = pos_search
        
        return pos_search
    
    def get_pos_data_ventas_cierre_caja_pagos_atc(self, data):
        
        if data['form']['session_id'] is False:
            sessionName = "%"
        else:
            sessionName = data['form']['session_id'][1]
        
        self.cr.execute("SELECT "\
                        "COUNT(po.id) AS cantidad_ventas "\
                        ",detalle_pago.tipo_pago AS tipo_venta "\
                        ",SUM (detalle_pedido.total_venta) AS total_pagos "\
                        "FROM pos_order AS po "\
                        "INNER JOIN pos_session AS ps ON ps.id = po.session_id "\
                        "JOIN ( "\
                        "SELECT "\
                        "ps.name AS sesion "\
                        ",po.id AS po_id "\
                        ",ps.id AS ps_id "\
                        ",SUM (pol.price_subtotal_incl) AS total_venta "\
                        "FROM pos_order_line AS pol "\
                        "INNER JOIN pos_order AS po ON po.id = pol.order_id "\
                        "INNER JOIN pos_session AS ps ON ps.id = po.session_id "\
                        "GROUP BY pol.order_id, po.id,ps.id "\
                        ") AS detalle_pedido ON detalle_pedido.po_id = po.id "\
                        "JOIN ( "\
                        "SELECT "\
                        "po.id AS po_id "\
                        ",aj.name AS tipo_pago "\
                        "FROM pos_order AS po "\
                        "INNER JOIN account_bank_statement_line AS acbastli ON acbastli.pos_statement_id = po.id "\
                        "INNER JOIN account_journal AS aj ON aj.id = acbastli.journal_id "\
                        "WHERE acbastli.amount > 0 "\
                        "GROUP BY acbastli.pos_statement_id, acbastli.journal_id, po.id, aj.name "\
                        ") AS detalle_pago ON detalle_pago.po_id = po.id "\
                        "WHERE po.order_status <> 'anulada' "\
                        "AND detalle_pago.tipo_pago = 'ATC' "\
                        "AND ps.name = %s "\
                        "GROUP BY tipo_venta", [sessionName])
        posSearchATC = [x for x in self.cr.fetchall()]
        
        self.suma_cierre_caja_ATC = posSearchATC
        return posSearchATC
    
    def get_pos_data_ventas_cierre_caja_pagos_caja_chica(self, data):
        
        if data['form']['session_id'] is False:
            sessionName = "%"
        else:
            sessionName = data['form']['session_id'][1]
        
        self.cr.execute("SELECT "\
                        "COUNT(*) AS caja_chica "\
                        ",'CAJA CHICA' AS nombre "\
                        ",SUM (aml.debit) AS total_caja_chica "\
                        "FROM account_move AS am "\
                        "INNER JOIN account_move_line AS aml ON aml.move_id = am.id "\
                        "WHERE am.partner_id ISNULL "\
                        "AND aml.debit > 0 "\
                        "AND am.ref = %s", [sessionName])
        pos_search4 = [x for x in self.cr.fetchall()]
        
        self.suma_cierre_caja_chica = pos_search4
        return pos_search4
    
    def __total_atc_chica__(self):
        granTotalATC = 0
        granTotalChica = 0
        granTotalResta = 0
        
        if self.suma_cierre_caja_ATC is not None:
            for line in self.suma_cierre_caja_ATC:
                granTotalATC += line[2]
            self.granTotalATC = granTotalATC
        
        if self.suma_cierre_caja_chica[0][2] is not None:
            for line in self.suma_cierre_caja_chica:
                granTotalChica += line[2]
            self.granTotalChica = granTotalChica
        
        granTotalResta = granTotalATC + granTotalChica
        print ">>>>>>>>>CAJA CHICA Y UTC",granTotalResta
        self.granTotalResta = granTotalResta
        return granTotalResta
    
    def get_pos_data_factura_minima(self, data):
        
        if data['form']['session_id'] is False:
            sessionName = "%"
        else:
            sessionName = data['form']['session_id'][1]
        
        self.cr.execute("SELECT po.qr_order_no AS factura "\
                        "FROM pos_order AS po "\
                        "WHERE po.id = ( "\
                        "SELECT MIN(po2.id) "\
                        "FROM pos_order AS po2 "\
                        "INNER JOIN pos_session AS ps ON ps.id = po2.session_id "\
                        "WHERE po2.qr_order_no NOTNULL "\
                        "AND ps.name = %s)", [sessionName])
        pos_minima = [x for x in self.cr.fetchall()]
        
        self.resultado_consulta = pos_minima
        return pos_minima
    
    def get_pos_data_factura_maxima(self, data):
        
        if data['form']['session_id'] is False:
            sessionName = "%"
        else:
            sessionName = data['form']['session_id'][1]
        
        self.cr.execute("SELECT po.qr_order_no AS factura "\
                        "FROM pos_order AS po "\
                        "WHERE po.id = ( "\
                        "SELECT MAX(po2.id) "\
                        "FROM pos_order AS po2 "\
                        "INNER JOIN pos_session AS ps ON ps.id = po2.session_id "\
                        "WHERE po2.qr_order_no NOTNULL "\
                        "AND ps.name = %s)", [sessionName])
        pos_search3 = [x for x in self.cr.fetchall()]
        
        self.resultado_consulta = pos_search3
        return pos_search3
    
    def __total_cierre_caja__(self):

        print ">>>>>>TOTAL: ",self.granTotalVentas, "<<<<>>>> ",self.granTotalResta 
        granTotal = self.granTotalVentas - self.granTotalResta 
        
        print ">>>>>>GRAN TOTAL: ",granTotal
        return granTotal
    
    def get_pos_data_facturas_anuladas(self, data):
        
        if data['form']['session_id'] is False:
            sessionName = "%"
        else:
            sessionName = data['form']['session_id'][1]
        
        self.cr.execute("SELECT "\
                        "COUNT(po.id) AS cantidad_ventas "\
                        ",SUM (detalle_pedido.total_venta) AS total_pagos "\
                        "FROM pos_order AS po "\
                        "INNER JOIN pos_session AS ps ON ps.id = po.session_id "\
                        "JOIN ( "\
                        "SELECT "\
                        "ps.name AS sesion "\
                        ",po.id AS po_id "\
                        ",ps.id AS ps_id "\
                        ",SUM (pol.price_subtotal_incl) AS total_venta "\
                        "FROM pos_order_line AS pol "\
                        "INNER JOIN pos_order AS po ON po.id = pol.order_id "\
                        "INNER JOIN pos_session AS ps ON ps.id = po.session_id "\
                        "GROUP BY pol.order_id, po.id,ps.id "\
                        ") AS detalle_pedido ON detalle_pedido.po_id = po.id "\
                        "WHERE po.order_status = 'anulada' "\
                        "AND ps.name = %s", [sessionName])
        pos_search4 = [x for x in self.cr.fetchall()]
        
        self.resultado_consulta = pos_search4
        return pos_search4

class pos_cierre_caja(osv.AbstractModel):
    _name = 'report.ew_panchita.pos_cierre_caja'
    _inherit = 'report.abstract_report'
    _template = 'ew_panchita.pos_cierre_caja'
    _wrapped_report_class = ew_pos_cierre_caja

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
