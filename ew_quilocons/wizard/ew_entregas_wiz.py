# -*- coding: utf-8 -*-
##############################################################################
#
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

from openerp.osv import fields, osv
import time
import operator
import itertools
from datetime import datetime
from dateutil import relativedelta
import xlwt
from xlsxwriter.workbook import Workbook
from openerp.tools.translate import _
from cStringIO import StringIO
import base64
from openerp import netsvc
from openerp import tools


# Declaracion del Wizard
class ew_report_entregas_wiz_qweb(osv.osv):
    _name="ew.report_entregas.wiz.qweb"
    _columns={
                'start_date': fields.datetime('Desde la Fecha'),
                'end_date': fields.datetime('Hasta la Fecha'),
                #'session_id' : fields.many2one('pos.session', 'Turno', required=False),
    }
    _defaults = {
        'start_date': lambda *a: time.strftime('%Y-%m-%d'),
        'end_date': lambda *a: time.strftime('%Y-%m-%d'),
    }
    
    # Accion del Boton de OK en el Wizard
    def printEntregasPdf(self,cr,uid,filtros,context=None):
        data={}
        data['ids'] = filtros
        data['form'] = self.read(cr, uid, filtros, ['start_date','end_date'])[0]
        data['form']['context'] = context
        print '----- Informacion del formulario:',data
        resultadoEntregasWizard = self.pool['report'].get_action(cr, uid, [], 'ew_quilocons.ew_entregas', data=data, context=context)
        print '----- Informacion enviada al reporte:',resultadoEntregasWizard

        return resultadoEntregasWizard

ew_report_entregas_wiz_qweb()

class inventory_excel_extended(osv.osv_memory):
    _name= "excel.extended"
    _columns= {
               'excel_file': fields.binary('Descargar Reporte Excel'),
               'file_name': fields.char('Excel File', size=64),
               }


    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: