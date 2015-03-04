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

# Apertura de Caja

class ew_pos_apertura_caja(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(ew_pos_apertura_caja, self).__init__(cr, uid, name, context=context)
        self.resultado_consulta = []
        self.resultado_consulta2 = []
        self.localcontext.update({
            
            'get_pos_data_apertura_caja': self.get_pos_data_apertura_caja,
            'get_pos_data_ultima_factura': self.get_pos_data_ultima_factura,
            'total_quantity': self.__total_quantity__,
            'total_price': self.__total_price__,
            })
    
    def get_pos_data_apertura_caja(self, data):
        print '-----Datos Formulario Recibidos:',data
        pos_pool = self.pool.get('pos.order')

        lst = []
        
        if data['form']['session_id'] is False:
            sessionName = "%"
        else:
            sessionName = data['form']['session_id'][1]
        print "-----Session:",sessionName
        
        self.cr.execute("SELECT ps.id "\
                        ",pc.name "\
                        ",cajero.name AS responsable "\
                        ",ps.start_at AS fecha_apertura "\
                        ",ps.name AS sesion "\
                        ",acbast.balance_start AS monto_inicial "\
                        "FROM pos_session AS ps "\
                        "INNER JOIN account_bank_statement AS acbast ON acbast.pos_session_id = ps.id "\
                        "INNER JOIN res_partner AS cajero ON cajero.id = ps.user_id "\
                        "INNER JOIN pos_config AS pc ON pc.id = ps.config_id "\
                        "WHERE acbast.balance_start >= 0 "\
                        #"AND ps.state <> 'closed' "\
                        "AND ps.name LIKE %s "\
                        "ORDER BY ps.state DESC "\
                        "LIMIT 1", [sessionName])
        pos_search = [x for x in self.cr.fetchall()]
        
        print '-----Resultado Busqueda por Query:',repr(pos_search)
        
        self.resultado_consulta = pos_search
        return pos_search
    
    def __total_quantity__(self):
        print self.resultado_consulta;
        granTotal = 0
        for line in self.resultado_consulta:
            granTotal += line[2]
        self.granTotal = granTotal
        print granTotal
        return granTotal
    
    def __total_price__(self):
        print self.resultado_consulta;
        granTotalPrice = 0
        for line in self.resultado_consulta:
            granTotalPrice += line[3]
        self.granTotalPrice = granTotalPrice
        print granTotalPrice
        return granTotalPrice

    def get_pos_data_ultima_factura(self, data):
        
        self.cr.execute("SELECT "\
                        "po.qr_order_no "\
                        "FROM pos_order AS po "\
                        "WHERE po.id = (SELECT MAX(po2.id) FROM pos_order AS po2)")
        pos_search2 = [x for x in self.cr.fetchall()]
        
        print '-----Resultado Busqueda por Query Ultima Factura:',repr(pos_search2)
        
        self.resultado_consulta2 = pos_search2
        return pos_search2

class pos_apertura_caja(osv.AbstractModel):
    _name = 'report.ew_panchita.pos_apertura_caja'
    _inherit = 'report.abstract_report'
    _template = 'ew_panchita.pos_apertura_caja'
    _wrapped_report_class = ew_pos_apertura_caja

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
