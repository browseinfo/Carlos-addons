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

{
    'name' : "Customizacion para FERCA S.R.L.",
    'version' : "1.1",
    'author' : "ExpertsWorking.com S.R.L.",
    'description' : 'Customizacion adicionales para POS 8 Restaurant para FERCA S.R.L.',
    'category' : "Customizacion FERCA S.R.L.",
    'depends' : ['account','sale','project','point_of_sale'],
    'website': 'http://www.expertsworking.com',
    'data' : [
              'report/ew_pos_resumen_ventas_productos_menu.xml',
              'report/ew_pos_inventario_menu.xml',
              'report/ew_pos_apertura_caja_menu.xml',
              'report/ew_pos_cierre_caja_menu.xml',
              'views/pos_resumen_productos.xml',
              'views/pos_apertura_caja.xml',
              'views/pos_cierre_caja.xml',
              'views/pos_inventario.xml',
              'wizard/ew_pos_report_wiz_view.xml',
              'wizard/ew_pos_apertura_caja_wiz_view.xml',
              'wizard/ew_pos_cierre_caja_wiz_view.xml',
              'wizard/ew_pos_inventario_wiz_view.xml',
			  'pos_sesiones_view.xml',
			  'pos_sesion_workflow.xml',
             ],
    'demo' : [],
    'installable': True,
    'auto_install': False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: