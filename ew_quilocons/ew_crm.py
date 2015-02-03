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


import crm
from datetime import datetime
from operator import itemgetter

import openerp
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.addons.base.res.res_partner import format_address
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp.tools import email_re, email_split



class res_users(osv.osv):
    
    _inherit = 'res.users'
    
    _columns = {
                'assign_seq': fields.integer('Assign Sequence')
                }
    
    

class crm_lead(format_address, osv.osv):
    """ CRM Lead Case """
    _inherit = "crm.lead"
    
    
    
    def _get_sales_person(self, cr, uid, context=None):
        """Finds id for case object"""
        context = context or {}
        user_pool = self.pool.get('res.users')
        lead_pool = self.pool.get('crm.lead')
        #searhc all active users
        total_users = user_pool.search(cr, uid, [('active','=',True)])
        
        #get all lead and get latest lead using max(highest_lead_no)
        highest_lead_no = lead_pool.search(cr, uid, [])
        
        if max(highest_lead_no):
            lead_browse = lead_pool.browse(cr, uid, max(highest_lead_no))
            
            #check for current sequence and increase with one
            currenct_seq = lead_browse.user_id.assign_seq
            next_seq = currenct_seq + 1
            next_user = user_pool.search(cr, uid, [('assign_seq','=',next_seq)])
            if next_user:
                sales_person = next_user or next_user[0] or False
            # if next user and sequence not found then start again with sequence 1
            else:
                sales_person = user_pool.search(cr, uid, [('assign_seq','=',1)])
        
        return sales_person or False
    
    
    _defaults = {
                 'user_id': _get_sales_person
                 }
    
    