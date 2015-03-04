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

class ew_pos_report_cierre_caja_wiz_qweb(osv.osv):
    _name="ew.pos_report_cierre_caja.wiz.qweb"
    _columns={
                'session_id' : fields.many2one('pos.session', 'Turno', required=True),
    }
    
    # Accion del Boton de OK en el Wizard
    def print_cierre_caja_qweb(self,cr,uid,ids,context=None):
        data={}
        data['ids'] = ids
        data['form'] = self.read(cr, uid, ids, ['session_id'])[0]
        data['form']['context'] = context
        print '----- Informacion del formulario:',data
        resultadoCierreCajaWizard = self.pool['report'].get_action(cr, uid, [], 'ew_panchita.pos_cierre_caja', data=data, context=context)
        print '----- Informacion enviada al reporte:',resultadoCierreCajaWizard
        return resultadoCierreCajaWizard

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: