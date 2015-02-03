# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Expertsworking.com (<http://www.expertsworking.com>).
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
    'name' : "Customizacion para Quilocons S.R.L.",
    'version' : "1.0",
    'author' : "ExpertsWorking.com S.R.L.",
    'description' : 'Customizacion para Quilocons S.R.L.',
    'category' : "Quilocons S.R.L.",
    'depends' : ['account','sale','stock','crm','sale_crm','marketing','base_setup','report'],
    'website': 'http://www.expertsworking.com',
    'data' : [
              'report/report_menu_ew_presupuesto.xml',
              'report/report_menu_ew_nota_venta.xml',
              'report/report_menu_ew_nota_entrega.xml',
              'report/report_menu_ew_entregas.xml',
              'views/ew_presupuesto.xml',
              'views/ew_nota_venta.xml',
              'views/ew_nota_entrega.xml',
              'views/ew_entregas.xml',
              'wizard/ew_entregas_wiz_view.xml',
              'ew_sale.xml',
              'ew_stock.xml'
             ],
    'demo' : [],
    'installable': True,
    'auto_install': False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
