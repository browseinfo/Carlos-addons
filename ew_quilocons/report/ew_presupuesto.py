# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Experts Working S.R.L. (<http://www.expertsworking.com>).
#    Copyright (C) 2004 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp.report import report_sxw
from openerp.osv import osv
import datetime
import qrcode
import base64
import tempfile
from BeautifulSoup import BeautifulSoup
import subprocess
import urllib, urllib2
from urllib import urlencode
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

# Clase para DEFINIR EL REPORTE
class ew_reporte_presupuesto(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ew_reporte_presupuesto, self).__init__(cr, uid, name, context=context)
        
        self.numero = 0
        
        self.localcontext.update({
#            'get_amount': self.get_amount,
#            'get_qrcode': self.get_qrcode,
#            'get_qrdate': self.get_qrdate,
#            'get_datelimit': self.get_datelimit,
#            'get_username': self.get_username,
             'obtenerComision': self._obtenerComision,
             'totalMasComision': self._totalMasComision,
             'numero':self._contador
        })
        
    def _obtenerComision(self, venta, totalBs):
        comision = 0.00
        #totalCantidad = 0.00
        print '-----Variable enviada:',totalBs

        if not venta.order_id.comision == 0.00:
            comision = (( venta.price_subtotal / totalBs) * venta.order_id.comision) + venta.price_subtotal
        else:
            comision = 0.00
        return comision
    
    def _obtenerComisionMasTotalProducto(self, venta, totalBs):
        comision = 0.00
        #totalCantidad = 0.00
        print '-----Variable enviada:',totalBs

        if not venta.order_id.comision == 0.00:
            comision = ( venta.price_subtotal / totalBs) * venta.order_id.comision
            comision = comision + (venta.price_subtotal)
        else:
            comision = 0.00
        return comision
    
    def _totalMasComision(self, comision, totalBs):
        totalSuma = comision + totalBs
        print '>>>>>SumaComision: ',totalSuma
        return totalSuma
    
    def _contador(self):
        numero = 0
        self.numero += 1
        numero = self.numero
        return numero        

# Aqui se DEFINE EL REPORTE
class ew_presupuesto(osv.AbstractModel):
    _name = 'report.ew_quilocons.ew_presupuesto'
    _inherit = 'report.abstract_report'
    _template = 'ew_quilocons.ew_presupuesto'
    _wrapped_report_class = ew_reporte_presupuesto
    
