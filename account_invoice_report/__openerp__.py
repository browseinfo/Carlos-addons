# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>)
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

{
    'name' : 'Facturacion QR 2015 para Ventas',
    'version' : '1.0',
    'author' : 'Expertsworking.com S.R.L.',
    'category' : 'Accounting',
    'description' : """
Localizacion Boliviana para facturacion QR segun normal de impuestos 2015.
    """,
    'website': 'http://www.expertsworking.com',
    'depends' : ['account','sale_stock',],
    'data': [
        'security/group_view.xml',
        'partner_view.xml',
        'invoice_view.xml',
        'sale_view.xml',
        'report_view.xml',
        'qr_sequence.xml',
        'wizard/invoice_format_a_view.xml',
        
#         'security/ir.model.access.csv'
    ],
    'js': [],
    'qweb' : [],
    'css':[],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: