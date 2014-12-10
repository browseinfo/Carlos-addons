# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-today browseinfo (<http://browseinfo.in>)
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
    "name": "Multi-DB Synchronization",
    "version": "1.2",
    "category": "Tools",
    "description": """
Synchronization with all objects.
=================================

Configure servers and trigger synchronization with its database objects.
""",
    "author": "Browseinfo",
    "images": ['images/1_servers_synchro.jpeg','images/2_synchronize.jpeg','images/3_objects_synchro.jpeg',],
    "depends": ["base"],
    'website': 'http://www.browseinfo.in',
    "data": [
        "wizard/base_synchro_view.xml",
        "base_synchro_view.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "auto_install": False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
