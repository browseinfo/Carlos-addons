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


class ew_pos_resumen_ventas_productos(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(ew_pos_resumen_ventas_productos, self).__init__(cr, uid, name, context=context)
        self.resultado_consulta = []
        self.localcontext.update({
            
            'get_pos_data': self.get_pos_data,
            'total_quantity': self.__total_quantity__,
            'total_price': self.__total_price__,
            })
    
    def get_pos_data(self, data):
        print '-----Datos Formulario Recibidos:',data
        pos_pool = self.pool.get('pos.order')

        lst = []
        
        if data['form']['session_id'] is False:
            sessionName = "%"
        else:
            sessionName = data['form']['session_id'][1]
        print "-----Session:",sessionName
        self.cr.execute("SELECT product_product.name_template as Producto, pol.sale_type AS Tipo, "\
                        "Sum(pol.qty) AS Cantidad, Sum(pol.qty * pol.price_unit) AS Total "\
                        "FROM pos_order "\
                        "INNER JOIN pos_order_line AS pol ON (pos_order.id = pol.order_id) "\
                        "INNER JOIN product_product ON (product_product.id = pol.product_id) "\
                        "INNER JOIN pos_session ON pos_order.session_id = pos_session.id "\
                        "WHERE pos_order.date_order >= %s AND pos_order.date_order <= %s AND pos_session.name Like %s "\
                        "GROUP BY product_product.name_template, pol.sale_type "\
                        "ORDER BY producto ASC" , (data['form']['start_date'],data['form']['end_date'], sessionName))
                
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

class pos_resumen_productos(osv.AbstractModel):
    _name = 'report.ew_panchita.pos_resumen_productos'
    _inherit = 'report.abstract_report'
    _template = 'ew_panchita.pos_resumen_productos'
    _wrapped_report_class = ew_pos_resumen_ventas_productos

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
