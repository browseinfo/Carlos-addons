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
import time
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
class ew_reporte_nota_entrega(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ew_reporte_nota_entrega, self).__init__(cr, uid, name, context=context)
        
        self.numero = 0
        
        self.localcontext.update({
#            'get_amount': self.get_amount,
#            'get_qrcode': self.get_qrcode,
#            'get_qrdate': self.get_qrdate,
#            'get_datelimit': self.get_datelimit,
#            'get_username': self.get_username,
            'cantidadProductos':self._cantidadProductos,
            'fechaActual':self._fechaActual,
            'vendedor': self.pool.get('res.users').browse(cr, uid, uid).name,
            'telefonoUsuario': self.pool.get('res.users').browse(cr, uid, uid).phone,
            'numero':self._contador
        })
    
    def _cantidadProductos(self, lineaEntrega):
        totalProductos = 0
        for fila in lineaEntrega:
            totalProductos += fila.product_uom_qty
        return totalProductos            
    
    def _fechaActual(self):
        fecha = time.strftime("%x")
        return fecha
    
    def _contador(self):
        numero = 0
        self.numero += 1
        numero = self.numero
        return numero

# Aqui se DEFINE EL REPORTE
class ew_presupuesto(osv.AbstractModel):
    _name = 'report.ew_quilocons.ew_nota_entrega'
    _inherit = 'report.abstract_report'
    _template = 'ew_quilocons.ew_nota_entrega'
    _wrapped_report_class = ew_reporte_nota_entrega
    
